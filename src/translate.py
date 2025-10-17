from tatsu import compile
import json

grammar = open('hoa.tatsu').read()

parser = compile(grammar)

hoa_text = open("test.hoa").read()

