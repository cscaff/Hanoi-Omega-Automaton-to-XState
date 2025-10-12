from lark import Lark, Transformer, v_args
import json

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

# --------------------------
# Step 1: Parse the HOA
# --------------------------
parser = Lark(hoa_grammar, start="automaton", parser="lalr")

# --------------------------
# Step 2: Transform parse tree
# --------------------------
class HOATransformer(Transformer):
    def automaton(self, items):
        header, body = items[0], items[1:]
        return {"header": header, "body": body}

    def header(self, items):
        result = {}
        for item in items:
            result.update(item)
        return result

    def states(self, items):
        return {"states": int(items[0])}

    def start(self, items):
        # state_conj: INT ("&" INT)*
        return {"start": [int(i) for i in items]}

    def ap(self, items):
        return {"ap": [str(i) for i in items]}  # store AP names

    def alias(self, items):
        name, expr = items
        return {"alias": {"name": str(name), "expr": expr}}

    def acceptance(self, items):
        num, cond = items
        return {"acceptance": {"num": int(num), "cond": cond}}

    def acc_name(self, items):
        return {"acc_name": [str(i) for i in items]}

    def tool(self, items):
        return {"tool": [str(i) for i in items]}

    def name(self, items):
        return {"name": str(items[0])}

    def properties(self, items):
        return {"properties": [str(i) for i in items]}

    def other_header(self, items):
        key, *vals = items
        return {str(key): [str(v) for v in vals]}

    # --------------------
    # Body
    # --------------------
    def body(self, items):
        return items

    def state(self, items):
        state_id, transitions = items[0], items[1:]
        return {"id": int(state_id), "transitions": transitions}

    def transition(self, items):
        label, target = items
        return {"label": label, "target": int(target)}

    # --------------------
    # Expressions
    # --------------------
    def label_expr(self, items):
        if len(items) == 1:
            return items[0]
        # If binary operator
        left = items[0]
        for op, right in zip(items[1::2], items[2::2]):
            left = {"op": str(op), "left": left, "right": right}
        return left

    def BOOLEAN(self, tok):
        return tok.value == "true"

    def INT(self, tok):
        return int(tok)

    def ANAME(self, tok):
        return str(tok)

    def IDENTIFIER(self, tok):
        return str(tok)

# --------------------------
# Step 3: Convert to XState JSON
# --------------------------
def hoastates_to_xstate(states, start_state):
    xstate = {
        "id": "hoa_machine",
        "initial": str(start_state),
        "states": {}
    }
    for s in states:
        sid = str(s["id"])
        xstate["states"][sid] = {
            "on": {}
        }
        for t in s["transitions"]:
            # XState uses a map of event -> target states
            event = json.dumps(t["label"])  # convert label expression to string
            xstate["states"][sid]["on"][event] = str(t["target"])
    return xstate

# --------------------------
# Example Usage
# --------------------------
hoa_text = open("./src/test.hoa").read()
tree = parser.parse(hoa_text)
parsed = HOATransformer().transform(tree)

# extract body and start
body = parsed["body"]
start_state = parsed["header"]["start"][0]
xstate_json = hoastates_to_xstate(body, start_state)

print(json.dumps(xstate_json, indent=2))