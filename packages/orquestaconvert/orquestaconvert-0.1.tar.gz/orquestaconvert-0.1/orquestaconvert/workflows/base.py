import re
import six
import warnings

import ruamel.yaml

from orquestaconvert.expressions import ExpressionConverter
from orquestaconvert.expressions.base import BaseExpressionConverter
from orquestaconvert.expressions.jinja import JinjaExpressionConverter
from orquestaconvert.expressions.yaql import YaqlExpressionConverter
from orquestaconvert.expressions.mixed import MixedExpressionConverter
from orquestaconvert.utils import task_utils
from orquestaconvert.utils import type_utils

WORKFLOW_TYPES = [
    'direct',
]

WORKFLOW_UNSUPPORTED_ATTRIBUTES = [
    'output-on-error',
]

TASK_UNSUPPORTED_ATTRIBUTES = [
    'keep-result',
    'pause-before',
    'safe-rerun',
    'target',
    'timeout',
    'wait-after',
    'wait-before',
    'workflow',
]

UNSUPPORTED_MISTRAL_ACTIONS = [
    'std.echo',
    'std.email',
    'std.javascript',
    'std.js',
    'std.ssh',
]

MISTRAL_ACTION_CONVERSION_TABLE = {
    'std.fail': 'fail',
    'std.http': 'core.http',
    'std.mistral_http': 'core.http',
    'std.noop': 'core.noop',
}

# Comparison operators and their inverses (both Jinja and YAQL):
COMPARISON_OPERATOR_INVERSES = {
    '!=': '=',
    '<':  '>=',  # noqa: E241
    '<=': '>',
    '=':  '!=',  # noqa: E241
    '>':  '<=',  # noqa: E241
    '>=': '<',
    # YAQL has additional regex matching operators:
    '=~': '!~',
    '!~': '=~',
    # More importantly, Jinja does not have either of those operators, so this
    # should not inavertently any Jinja expressions
}


# This regex matches Mistral's with-items syntax:
# variable_name in <% YAQL_EXPRESSION %>
# variable_name in {{ JINJA_EXPRESSION }}
# variable_name in [static, list]
WITH_ITEMS_PATTERN = r'^\s*(?P<var>\w+)\s+in\s+(?P<expr>(?:<%|{{)?\s*.+?\s*(?:%>|}})?)\s*$'
WITH_ITEMS_EXPR_RGX = re.compile(WITH_ITEMS_PATTERN)

RETRY_BREAK_ON_PATTERN = r'^(?P<lhs>[^!~?=<>\s]+)\s*(?P<comp_op>!?=|<=?|>=?|[=!]~)\s*(?P<rhs>[^!~?=<>\s]+)$'
RETRY_BREAK_ON_RGX = re.compile(RETRY_BREAK_ON_PATTERN)

CTX_PATTERN = r'\bctx\([\'"]*(\w+)[\'"]*\)|\bctx\(\).(\w+)\b'
CTX_RGX = re.compile(CTX_PATTERN)


class WorkflowConverter(object):
    task_with_item_vars = []

    def group_task_transitions(self, mistral_transition_list):
        expr_transitions = ruamel.yaml.comments.CommentedMap()

        # If the transition is just a string, convert it to a list containing
        # the string
        if isinstance(mistral_transition_list, six.string_types):
            mistral_transition_list = [mistral_transition_list]

        simple_transitions = []
        for transition in mistral_transition_list:
            # if this is a string, then the transition is simply the name of the
            # next task
            if isinstance(transition, six.string_types):
                simple_transitions.append(transition)

            # if the transition is a dict, then it has an expression
            #  key = next task name
            #  value = conditional expression for when this transition should take place
            elif isinstance(transition, type_utils.dict_types):
                # group transitions by their common expression, this way we can keep
                # all of the transitions with the same expressions in the same
                # `when:` condition
                for task_name, expr in six.iteritems(transition):
                    if expr not in expr_transitions:
                        expr_transitions[expr] = []
                    expr_transitions[expr].append(task_name)
            else:
                raise TypeError('Task transition is not a "string" or "dict": {}  type={}'
                                .format(transition, type(transition)))

        return simple_transitions, expr_transitions

    def dict_to_list(self, d):
        return [{k: v} for k, v in six.iteritems(d)]

    def extract_context_variables(self, obj):
        # given an object that contains Orquesta YAQL or Jinja expressions (eg: contain 'ctx()'),
        # extract all variable names into a set
        variable_names = set()
        if isinstance(obj, type_utils.dict_types):
            for key in obj.keys():
                variable_names = variable_names | self.extract_context_variables(key)
            for val in obj.values():
                variable_names = variable_names | self.extract_context_variables(val)
        elif isinstance(obj, list):
            for element in obj:
                variable_names = variable_names | self.extract_context_variables(element)
        elif isinstance(obj, six.string_types):
            for mobj in CTX_RGX.finditer(obj):
                match = mobj.group(1) or mobj.group(2)
                variable_names.add(match)
        return variable_names

    def convert_task_transition_simple(self, transitions, publish, orquesta_expr, expr_converter):
        # if this is a simple name of a task:
        # on-success:
        #   - do_thing_a
        #   - do_thing_b
        #
        # this should produce the following in orquesta
        # next:
        #   - when: "{{ succeeded() }}"
        #     do:
        #       - do_thing_a
        #       - do_thing_b
        simple_transition = ruamel.yaml.comments.CommentedMap()

        # on-complete doesn't have an orquesta_expr, so we should not
        # add the 'when' clause in that case
        if orquesta_expr:
            simple_transition['when'] = expr_converter.wrap_expression(orquesta_expr)

        # add in published variables
        if publish:
            publish_converted = ExpressionConverter.convert_dict(publish)
            simple_transition['publish'] = self.dict_to_list(publish_converted)

        # add in the transition list
        if transitions:
            simple_transition['do'] = transitions

        return simple_transition

    def convert_task_transition_expr(self, task_name, expression_list, publish, orquesta_expr):
        # group all complex expressions by their common expression
        # this way we can keep all of the transitions with the same
        # expressions in the same `when:` condition
        #
        # on-success:
        #   - do_thing_a: "{{ _.x }}"
        #   - do_thing_b: "{{ _.x }}"
        #   - do_thing_c: "{{ not _.x }}"
        #
        # should produce the following in orquesta
        #
        # next:
        #   - when: "{{ succeeded() and _.x }}"
        #     do:
        #       - do_thing_a
        #       - do_thing_b
        #   - when: "{{ succeeded() and not _.x }}"
        #     do:
        #       - do_thing_c
        transitions = []
        for expr, task_list in six.iteritems(expression_list):
            expr_transition = ruamel.yaml.comments.CommentedMap()
            expr_converted = ExpressionConverter.convert(expr)

            # for some transitions (on-complete) the orquesta_expr may be empty
            # so only add it in, if it's necessary
            if orquesta_expr:
                converter = ExpressionConverter.get_converter(expr_converted)
                expr_converted = converter.unwrap_expression(expr_converted)
                o_expr = '{} and ({})'.format(orquesta_expr, expr_converted)
                o_expr = converter.wrap_expression(o_expr)
            else:
                o_expr = expr_converted

            expr_transition['when'] = o_expr
            if publish:
                converted_publish = ExpressionConverter.convert_dict(publish)
                expr_transition['publish'] = [{k: v} for k, v in converted_publish.items()]

                expr_transition['when'] = self.replace_immediately_referenced_variables(task_name,
                                                                                        expr_transition['when'],
                                                                                        converted_publish)

            expr_transition['do'] = task_list
            transitions.append(expr_transition)
        return transitions

    def replace_immediately_referenced_variables(self, task_name, when_expr, publish_dict):
        # Check for context variable references that are used in the 'when'
        # expression
        variables_in_when = self.extract_context_variables(when_expr)

        variables_in_publish = set(publish_dict.keys())

        immediately_referenced_variables = variables_in_when & variables_in_publish

        # Replace the context variable references in the 'when'
        # expression with their expression from the 'publish' block
        for variable in immediately_referenced_variables:
            # First off, make sure they are the same type of expression,
            # we don't want to inject a Jinja expression in the middle
            # of a YAQL expression
            when_expr_type = ExpressionConverter.expression_type(when_expr)
            publish_expr_type = ExpressionConverter.expression_type(publish_dict[variable])

            if when_expr_type == publish_expr_type:
                # Grab the variable expression
                converter = ExpressionConverter.get_converter(publish_dict[variable])
                unwrapped_expr = converter.unwrap_expression(publish_dict[variable])

                # Replace double parentheses
                # ((ctx().variable))    ->  (result().result['variable'] + 1)
                variable_reference_dp = r'\(\(ctx\(\).{var}\)\)'.format(var=variable)
                when_expr = re.sub(variable_reference_dp, "({})".format(unwrapped_expr), when_expr)

                # Don't add in parentheses if they already exist
                # (ctx().variable)      ->  (result().result['variable'] + 1)
                variable_reference_dp = r'\(ctx\(\).{var}\)'.format(var=variable)
                when_expr = re.sub(variable_reference_dp, "({})".format(unwrapped_expr), when_expr)

                # Keep surrounding context and add surrounding parentheses
                # (ctx().variable ...   ->  ((result().result['variable'] + 1) ...
                # ... ctx().variable)   ->  ... (result().result['variable'] + 1))
                # ...ctx().variable...  ->  ...(result().result['variable'] + 1)...
                variable_reference_ep = r'(.)\bctx\(\).{var}\b(.)'.format(var=variable)
                when_expr = re.sub(variable_reference_ep, r"\1({})\2".format(unwrapped_expr), when_expr)

                # Keep double enclosing internal parentheses
                # (ctx(variable))  ->  (result().result['variable'] + 1)
                variable_reference_eip = r'\(ctx\({var}\)\)'.format(var=variable)
                when_expr = re.sub(variable_reference_eip, "({})".format(unwrapped_expr), when_expr)

            else:
                warnings.warn("The transition \"{when_expr}\" in {task_name} "
                              "references the '{variable}' context variable, "
                              "which is published in the same transition. You "
                              "will need to manually convert the {variable} "
                              "expression in the transition."
                              .format(when_expr=when_expr,
                                      task_name=task_name,
                                      variable=variable)),
        return when_expr

    def default_task_transition_map(self):
        transitions = ruamel.yaml.comments.CommentedMap()
        transitions['on-success'] = ruamel.yaml.comments.CommentedMap()
        transitions['on-success']['publish'] = ruamel.yaml.comments.CommentedMap()
        transitions['on-success']['orquesta_expr'] = 'succeeded()'

        transitions['on-error'] = ruamel.yaml.comments.CommentedMap()
        transitions['on-error']['publish'] = ruamel.yaml.comments.CommentedMap()
        transitions['on-error']['orquesta_expr'] = 'failed()'

        transitions['on-complete'] = ruamel.yaml.comments.CommentedMap()
        transitions['on-complete']['publish'] = ruamel.yaml.comments.CommentedMap()
        transitions['on-complete']['orquesta_expr'] = None
        return transitions

    def normalize_transition_task_names(self, o_task_spec):
        for i, transition in enumerate(o_task_spec['next']):
            if 'do' in o_task_spec['next'][i]:
                new_dos = [task_utils.translate_task_name(tname) for tname in transition['do']]
                o_task_spec['next'][i]['do'] = new_dos
        return o_task_spec

    def convert_task_transitions(self, task_name, m_task_spec, expr_converter, wf_vars):
        # group all complex expressions by their common expression
        # this way we can keep all of the transitions with the same
        # expressions in the same `when:` condition
        #
        # publish:
        #   good_data: "{{ _.good }}"
        # publish-on-error:
        #   bad_data: "{{ _.bad }}"
        # on-success:
        #   - do_thing_a: "{{ _.x }}"
        #   - do_thing_b: "{{ _.x }}"
        # on-error:
        #   - do_thing_error: "{{ _.e }}"
        # on-complete:
        #   - do_thing_sometimes: "{{ _.d }}"
        #   - do_thing_always
        #
        # should produce the following in orquesta
        #
        # next:
        #   - when: "{{ succeeded() }}"
        #     publish:
        #       - good_data: "{{ ctx().good }}"
        #   - when: "{{ failed() }}"
        #     publish:
        #       - bad_data: "{{ ctx().bad }}"
        #   - when: "{{ succeeded() and ctx().x }}"
        #     publish:
        #       - good_data: "{{ ctx().good }}"
        #     do:
        #       - do_thing_a
        #       - do_thing_b
        #   - when: "{{ failed() and ctx().e }}"
        #     publish:
        #       - bad_data: "{{ ctx().bad }}"
        #     do:
        #       - do_thing_error
        #   - when: "{{ ctx().d }}"
        #     publish:
        #       - good_data: "{{ ctx().good }}"
        #       - bad_data: "{{ ctx().bad }}"
        #     do:
        #       - do_thing_sometimes
        #   - publish:
        #       - good_data: "{{ ctx().good }}"
        #       - bad_data: "{{ ctx().bad }}"
        #     do:
        #       - do_thing_always
        o_task_spec = ruamel.yaml.comments.CommentedMap()
        o_task_spec['next'] = []

        transitions = self.default_task_transition_map()

        if m_task_spec.get('publish'):
            transitions['on-success']['publish'] = m_task_spec['publish']

        if m_task_spec.get('publish-on-error'):
            transitions['on-error']['publish'] = m_task_spec['publish-on-error']

        if m_task_spec.get('on-complete'):
            # Handling on-complete publishing is more complicated, because the
            # dictionaries from publish and publish-on-error need to be
            # combined, but cannot overlap.
            publish = m_task_spec.get('publish', ruamel.yaml.comments.CommentedMap())
            publish_on_error = m_task_spec.get('publish-on-error',
                                               ruamel.yaml.comments.CommentedMap())

            # Generate a list of common keys for publish and publish-on-error
            # dictionaries
            common_publish_keys = list(set(publish.keys()) & set(publish_on_error.keys()))

            # If common keys have the same value, it's fine if we merge the
            # dictionaries.
            common_publish_keys_different_values = [
                k for k in common_publish_keys if publish[k] != publish_on_error[k]
            ]

            # If there are any common keys that correspond to different values
            # the publish dictionary and publish-on-error dictionaries, we need
            # to bail.
            if common_publish_keys_different_values:
                error_message = ("Task '{}' contains one or more keys ({}) in both publish and "
                                 "publish-on-error dictionaries that have different values. "
                                 "Please either remove the common keys, or ensure that the values "
                                 "of any common keys are the same.").\
                    format(task_name, ', '.join(common_publish_keys_different_values))
                raise NotImplementedError(error_message)

            publish_on_complete = publish.copy()
            publish_on_complete.update(publish_on_error)
            transitions['on-complete']['publish'] = publish_on_complete

        for m_transition_name, data in six.iteritems(transitions):
            m_transitions = m_task_spec.get(m_transition_name, [])
            trans_simple, trans_expr = self.group_task_transitions(m_transitions)

            publish_to_workflow_context = bool(wf_vars & set(data.get('publish').keys()))

            # Create a transition for the simple task lists
            if trans_simple or publish_to_workflow_context:
                o_trans_simple = self.convert_task_transition_simple(trans_simple,
                                                                     data.get('publish'),
                                                                     data['orquesta_expr'],
                                                                     expr_converter)
                o_task_spec['next'].append(o_trans_simple)

            # Create multiple transitions, one for each unique expression
            o_trans_expr_list = self.convert_task_transition_expr(task_name,
                                                                  trans_expr,
                                                                  data.get('publish'),
                                                                  data['orquesta_expr'])
            o_task_spec['next'].extend(o_trans_expr_list)

        o_task_spec = self.normalize_transition_task_names(o_task_spec)

        return o_task_spec if o_task_spec['next'] else ruamel.yaml.comments.CommentedMap()

    def convert_action(self, m_action):
        if m_action in UNSUPPORTED_MISTRAL_ACTIONS:
            raise NotImplementedError(("Action '{}' is not supported in orquesta.").
                                      format(m_action))

        o_action = MISTRAL_ACTION_CONVERSION_TABLE.get(m_action, m_action)

        kwargs = {'item_vars': self.task_with_item_vars}
        return MixedExpressionConverter.convert_string(o_action, **kwargs)

    def _get_inverse_comparison_operator(self, operator):
        # Should probably push this into the converters themselves,
        # but this will suffice for now
        # Convert and invert *simple* YAQL comparisons, since most continue-on's will
        # likely be simple comparisons
        return COMPARISON_OPERATOR_INVERSES[operator]

    def convert_retry(self, m_retry, task_name):
        o_retry = ruamel.yaml.comments.CommentedMap()
        if m_retry.get('count'):
            o_retry['count'] = m_retry['count']
        if m_retry.get('delay'):
            o_retry['delay'] = m_retry['delay']

        # Check for both and bail early
        if m_retry.get('continue-on') and m_retry.get('break-on'):
            raise NotImplementedError("Cannot convert \"retry\" spec with both a \"break-on\" and "
                                      "\"continue-on\" attributes in the \"{task_name}\" task."
                                      .format(task_name=task_name))
        elif m_retry.get('continue-on') or m_retry.get('break-on'):
            expr = m_retry.get('continue-on') or m_retry.get('break-on')

            converter = ExpressionConverter.get_converter(expr)
            if converter:
                expr = converter.unwrap_expression(expr)
                expr = converter.convert_string(expr)

                comp_op_match = RETRY_BREAK_ON_RGX.match(expr)

                if comp_op_match:
                    inv_op = self._get_inverse_comparison_operator(comp_op_match.group('comp_op'))
                    expr = '{lhs} {op} {rhs}'.format(
                        lhs=comp_op_match.group('lhs'),
                        op=inv_op,
                        rhs=comp_op_match.group('rhs'))
                    # TODO: For YAQL we can also simply do 'not (expr)'

                expr = converter.wrap_expression(expr)
            o_retry['when'] = expr

        return o_retry

    def convert_input(self, input_):
        kwargs = {'item_vars': self.task_with_item_vars}
        return MixedExpressionConverter.convert_dict(input_, **kwargs)

    def convert_with_items_expr(self, expression, expr_converter):
        # Convert all with-items attributes
        #
        # with-items:
        #   - i in <% $.yaql_data %>
        #
        # with-items:
        #   - i in <% $.yaql_data %>
        #   - j in <% $.more_data %>
        #   - k in <% $.all_the_data %>
        #
        # with-items: i in <% $.yaql_data %>
        # concurrency: 2
        #
        # with-items: i in {{ _.jinja_data }}
        #
        # with-items: i in [0, 1, 2, 3]
        #
        # should produce the following in orquesta
        #
        # with:
        #   items: i in <% ctx().yaql_data %>
        #
        # with:
        #   items: i, j, k in <% zip($.yaql_data, $.more_data, $.all_the_data) %>
        #
        # with:
        #   items: i in <% $.yaql_data %>
        #   concurrency: 2
        #
        # with:
        #   items: i in {{ ctx().jinja_data }}
        #
        # with:
        #   items: i in <% [0, 1, 2, 3] %>
        converter = None
        var_list = []
        expr_list = []
        if isinstance(expression, list):
            expression_list = expression
        else:
            # Create a list with a single element
            expression_list = [expression]

        for expr_item in expression_list:
            m = WITH_ITEMS_EXPR_RGX.match(expr_item)
            if m:
                var = m.group('var')
                expr = m.group('expr')
                converter = ExpressionConverter.get_converter(expr)
                if converter:
                    expr = converter.unwrap_expression(expr)
                    expr = converter.convert_string(expr)
                var_list.append(var)
                expr_list.append(expr)
            else:
                raise NotImplementedError("Unrecognized with-items expression: '{}'".
                                          format(expr_item))

        # If we have a list of expressions, we need to join them with commas
        # and feed that into 'zip()'
        # If we only have one expression in the list, we don't need to join
        # them or use 'zip()', we just use it directly
        if len(expr_list) > 1:
            expr_list_string = 'zip({expr})'.format(expr=', '.join(expr_list))
        else:
            expr_list_string = expr_list[0]

        # Default to the global expression converter if we could not determine one
        converter = converter if converter else expr_converter

        # We need to save the list of expression variables for when we convert
        # item access to item() instead of ctx()
        self.task_with_item_vars.extend(var_list)

        return "{vars} in {wrapped_expr}".format(
            vars=', '.join(var_list),
            wrapped_expr=converter.wrap_expression(expr_list_string))

    def convert_with_items(self, m_task_spec, expr_converter):
        with_items = m_task_spec['with-items']

        with_attr = {
            'items': self.convert_with_items_expr(with_items, expr_converter),
        }

        if m_task_spec.get('concurrency'):
            concurrency_expr = m_task_spec['concurrency']

            # Only try to convert the concurrency expression if it's a str
            if isinstance(concurrency_expr, six.string_types):
                converter = ExpressionConverter.get_converter(concurrency_expr)
                if converter:
                    concurrency_expr = converter.unwrap_expression(concurrency_expr)
                    concurrency_expr = converter.convert_string(concurrency_expr)
                    concurrency_expr = converter.wrap_expression(concurrency_expr)
            with_attr['concurrency'] = concurrency_expr

        return with_attr

    def convert_tasks(self, mistral_wf_tasks, expr_converter, wf_vars, force=False):
        orquesta_wf_tasks = ruamel.yaml.comments.CommentedMap()
        for task_name, m_task_spec in six.iteritems(mistral_wf_tasks):
            # The variables in with-items expressions need to be accessed using
            # the `item(var)` syntax, not the usual `ctx().var` syntax, so we
            # use this list to keep track of which variables are within the
            # task context
            self.task_with_item_vars = []
            o_task_spec = ruamel.yaml.comments.CommentedMap()
            if force:
                for attr in TASK_UNSUPPORTED_ATTRIBUTES:
                    val = m_task_spec.get(attr)
                    if val:
                        o_task_spec[attr] = val
            else:
                for attr in TASK_UNSUPPORTED_ATTRIBUTES:
                    if attr in m_task_spec:
                        raise NotImplementedError(("Task '{}' contains an attribute '{}'"
                                                   " that is not supported in orquesta.").
                                                  format(task_name, attr))

            if m_task_spec.get('with-items'):
                o_task_spec['with'] = self.convert_with_items(m_task_spec, expr_converter)

            if m_task_spec.get('action'):
                o_task_spec['action'] = self.convert_action(m_task_spec['action'])

            if m_task_spec.get('retry'):
                o_task_spec['retry'] = self.convert_retry(m_task_spec['retry'], task_name)

            if m_task_spec.get('join'):
                o_task_spec['join'] = m_task_spec['join']

            if m_task_spec.get('input'):
                o_task_spec['input'] = self.convert_input(m_task_spec['input'])

            o_task_transitions = self.convert_task_transitions(
                task_name, m_task_spec, expr_converter, wf_vars)
            o_task_spec.update(o_task_transitions)

            orquesta_wf_tasks[task_utils.translate_task_name(task_name)] = o_task_spec

        return orquesta_wf_tasks

    def expr_type_converter(self, expr_type):
        if expr_type is None:
            expr_converter = JinjaExpressionConverter()
        elif isinstance(expr_type, six.string_types):
            expr_type = expr_type.lower()
            if expr_type == 'jinja':
                expr_converter = JinjaExpressionConverter()
            elif expr_type == 'yaql':
                expr_converter = YaqlExpressionConverter()
            else:
                raise TypeError("Unknown expression type: {}".format(expr_type))
        elif isinstance(expr_type, BaseExpressionConverter):
            expr_converter = expr_type
        else:
            raise TypeError("Unknown expression class type: {}".format(type(expr_type)))
        return expr_converter

    def convert(self, mistral_wf, expr_type=None, force=False):
        variables_used_in_output = set()
        expr_converter = self.expr_type_converter(expr_type)
        orquesta_wf = ruamel.yaml.comments.CommentedMap()
        orquesta_wf['version'] = '1.0'

        if force:
            for attr in WORKFLOW_UNSUPPORTED_ATTRIBUTES:
                val = mistral_wf.get(attr)
                if val:
                    orquesta_wf[attr] = val
        else:
            for attr in WORKFLOW_UNSUPPORTED_ATTRIBUTES:
                if attr in mistral_wf:
                    raise NotImplementedError(("Workflow contains an attribute '{}' that is not"
                                               " supported in orquesta.").format(attr))

        if mistral_wf.get('description'):
            orquesta_wf['description'] = mistral_wf['description']

        if mistral_wf.get('type'):
            if mistral_wf['type'] not in WORKFLOW_TYPES:
                raise NotImplementedError(("Workflows of type '{}' are NOT supported."
                                           " Only 'direct' workflows can be converted").
                                          format(mistral_wf['type']))

        if mistral_wf.get('input'):
            orquesta_wf['input'] = ExpressionConverter.convert_list(mistral_wf['input'])

        if mistral_wf.get('vars'):
            expression_vars = ExpressionConverter.convert_dict(mistral_wf['vars'])
            orquesta_wf['vars'] = self.dict_to_list(expression_vars)

        if mistral_wf.get('output'):
            output = ExpressionConverter.convert_dict(mistral_wf['output'])
            orquesta_wf['output'] = self.dict_to_list(output)

            variables_used_in_output = self.extract_context_variables(output)

        if mistral_wf.get('tasks'):
            o_tasks = self.convert_tasks(
                mistral_wf['tasks'],
                expr_converter,
                variables_used_in_output,
                force=force)
            if o_tasks:
                orquesta_wf['tasks'] = o_tasks

        return orquesta_wf
