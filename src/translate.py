from tatsu import compile
import json

grammar = open('hoa.tatsu').read()

parser = compile(grammar)

hoa_text = open("test.hoa").read()

ast = parser.parse(hoa_text, start="automaton",  trace=True)
print(json.dumps(ast, indent=2))

