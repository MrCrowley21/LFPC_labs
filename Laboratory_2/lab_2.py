from NFA import NFA
from DFA import DFA

# read the FA from file
with open('Variant_13.txt', 'r') as file:
    automaton = file.read().splitlines()

nfa = NFA(automaton)  # initiate the FA of type NFA
dfa = DFA(automaton)  # initiate the FA of type DFA

print('Table of transformation from NFA to DFA: \n', nfa.get_transformation_table())
print('\nRepresentation and steps of transformation from NFA to DFA: ')
print(dfa.transform_to_DFA())
print('\nAnalytical representation of regular grammar graph: \n', nfa.convert_to_rgrammar())
print('\nRegular grammar for presented FA: \n', nfa.represent_RG())
