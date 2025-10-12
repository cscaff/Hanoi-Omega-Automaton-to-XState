from lark import Lark, Transformer

hoa_grammar = """
// Lark grammar for HOA automata

// --------------------
// Terminals
// --------------------
%import common.CNAME       -> IDENTIFIER   // letters, digits, underscore, not starting with digit
%import common.INT         // integer numbers
%import common.WS
%import common.ESCAPED_STRING -> STRING
%ignore WS

BOOLEAN: "true" | "false"
ANAME: /[A-Za-z_][A-Za-z0-9_]*/
HEADERNAME: /[A-Za-z_][A-Za-z0-9_]*/

!automaton: header "--BODY--" body "--END--"

header: format_version header_item*

format_version: "HOA:" IDENTIFIER

header_item: states
           | start
           | ap
           | alias
           | acceptance
           | acc_name
           | tool
           | name
           | properties
           | other_header

states: "States:" INT
start: "Start:" state_conj
ap: "AP:" INT STRING*
alias: "Alias:" ANAME label_expr
acceptance: "Acceptance:" INT acceptance_cond
acc_name: "acc-name:" IDENTIFIER (BOOLEAN|INT|IDENTIFIER)*
tool: "tool:" STRING STRING?
name: "name:" STRING
properties: "properties:" IDENTIFIER*
other_header: HEADERNAME (BOOLEAN|INT|STRING|IDENTIFIER)*

// --------------------
// Expressions
// --------------------
state_conj: INT ("&" INT)*

?label_expr: BOOLEAN
           | INT
           | ANAME
           | "!" label_expr
           | "(" label_expr ")"
           | label_expr "&" label_expr
           | label_expr "|" label_expr

?acceptance_cond: IDENTIFIER "(" "!"? INT ")"
                | "(" acceptance_cond ")"
                | acceptance_cond "&" acceptance_cond
                | acceptance_cond "|" acceptance_cond
                | BOOLEAN

// --------------------
// Body (placeholder)
// --------------------
body: state+

state: "State:" INT transition+
transition: "[" label_expr "]" INT
"""

