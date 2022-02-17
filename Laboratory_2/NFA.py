import pandas as pd
from copy import deepcopy

class NFA:

    # initiation function
    def __init__(self, automaton):
        self.automaton = automaton  # stores the input NFA
        self.states = self.__get_states()  # stores the states of NFA
        self.alphabet = self.__get_alphabet()  # stores the alphabet of NFA
        self.initial_state = self.__get_initial_state()  # stores the initial state of NFA
        self.final_state = self.__get_final_state()  # stores the final nodes of NFA
        self.transitions = self.__split_transitions()  # stores the transitions of NFA as dictionary with destination
                                                       # nodes as list

    # return the list of states of NFA
    def __get_states(self):
        return self.automaton[0].split(', ')

    # return the alphabet of NFA
    def __get_alphabet(self):
        return self.automaton[1].split(', ')

    # return the initial state of NFA
    def __get_initial_state(self):
        return self.automaton[2]

    # return the final state of NFA
    def __get_final_state(self):
        return [self.automaton[3]]

    # check if the given symbol is valid
    def check_nfa(self, variable, related_set):
        if variable not in related_set:
            raise Exception(f'Incorrect transition. There is no character {variable} in {related_set}')

    # represent transitions in form of dictionary
    def __split_transitions(self):
        transitions = dict()  # initiate a dictionary to store the transitions

        for transition in self.automaton[4:]:
            # extract state from the tranition
            state = transition.split(', ')[0].replace('sigma(', '')
            self.check_nfa(state, self.states)
            # initiate the state in dictionary if it does not exist
            if state not in transitions:
                transitions[state] = {}
            # extract alphabet character from transition
            action = transition.split(', ')[1].replace('sigma(', '').replace(')', '').split(' = ')[0]
            self.check_nfa(action, self.alphabet)
            # initiate the alphabet character if it is not in state values
            if action not in transitions[state]:
                transitions[state][action] = []
            # extract the destination state from transition
            transitions[state][action].append(transition.split(' = ')[1])
            self.check_nfa(transition.split(' = ')[1], self.states)
        return transitions

    # update the list of states of the DFA in the process of transformation
    def __update_states(self, dfa_states, temp_dfa_states):
        # for each alphabet state, check if new state created
        for action in temp_dfa_states:
            if len(temp_dfa_states[action]) > 1 and set(temp_dfa_states[action]) not in dfa_states:
                dfa_states.append(set(temp_dfa_states[action]))
            elif len(temp_dfa_states[action]) == 1 and temp_dfa_states[action] not in dfa_states:
                dfa_states.append(temp_dfa_states[action])
        return dfa_states

    # define the states obtained after one row transition
    def define_DFA_states(self, current_state):
        temp_dfa_states = dict()  # initiate the possible states dictionary
        # find results for each component-state of the given state
        for state in current_state:
            # check states that have transitions
            if state in self.transitions:
                for action in self.transitions[state]:
                    # if the alphabet not in dictionary, add it
                    if action not in temp_dfa_states:
                        temp_dfa_states[action] = []
                    # add the productions of the given state and alphabet in dictionary if it does not exist
                    if len(self.transitions[state][action]) == 1 and self.transitions[state][action][0] not in \
                            temp_dfa_states[action]:
                        temp_dfa_states[action].append(self.transitions[state][action][0])
                    elif len(self.transitions[state][action]) > 1:
                        for i in range(len(self.transitions[state][action])):
                            if self.transitions[state][action][i] not in temp_dfa_states[action]:
                                temp_dfa_states[action].append(self.transitions[state][action][i])
        return temp_dfa_states

    # transform NFA to DFA
    def transform_to_DFA(self):
        dfa_states = [[self.initial_state]]  # initiate the list of states
        dfa_representation = dict()  # initiate the dictionary for DFA representation

        # for all states
        for current_state in dfa_states:
            # find production of the state
            temp_dfa_states = self.define_DFA_states(current_state)
            # update the list of states
            dfa_states = self.__update_states(dfa_states, temp_dfa_states)
            # transform composed states into strings
            dfa_state = ''.join(component_state for component_state in sorted(list(current_state)))
            # add new state to DFA dictionary
            dfa_representation[dfa_state] = temp_dfa_states
            # transform the destination composed nodes into strings
            for action in self.alphabet:
                if action in dfa_representation[dfa_state]:
                    dfa_representation[dfa_state][action] = ''.join(component_state for component_state in
                                                                    sorted(dfa_representation[dfa_state][action]))
            # print each step
            print(dfa_representation)
        return dfa_representation

    # get the final states of the DFA
    def get_dfa_final_state(self, dfa_representation):
        final_state = []  # initiate the final states of DFA
        # check if one of the final states of NFA appears in DFA
        for state in self.final_state:
            for dfa_state in dfa_representation:
                if dfa_state.find(state) != -1 and dfa_state not in final_state:
                    final_state.append(dfa_state)
        return final_state

    # Show the table of transformation from NFA to DFA
    def get_transformation_table(self):
        transformation_df = pd.DataFrame(columns=self.alphabet)  # create a dataframe
        transformations = self.transform_to_DFA()  # get the representation of DFA
        for transformation in transformations:
            # create the row
            transformation_df.append(pd.Series(name=transformation).astype(object))
            #  add values to the cells
            if transformations[transformation].items():
                for action in transformations[transformation]:
                    transformation_df.at[transformation, action] = transformations[transformation][action]
            else:
                for action in transformation_df.columns:
                    transformation_df.at[transformation, action] = ' - '
        return transformation_df

    # convert FA into regular grammar
    def convert_to_rgrammar(self):
        transitions = deepcopy(self.transitions)  # the list of transitions
        regular_grammar = dict()  # dictionary that stores the regular grammar
        states_grammar = dict()  # dictionary that stores relation between state and non-terminal symbol
        i = ord('A')  # the first non-terminal symbol besides start

        for state in transitions:
            # if transition has productions, assign a non-terminal value to the state
            if transitions[state]:
                if state == self.initial_state:
                    nonterinal_symbol = 'S'
                else:
                    nonterinal_symbol = chr(i)
                    # iterate the value of non-terminal symbol
                    i += 1
                # copy transitions into regular grammar dictionary
                regular_grammar[nonterinal_symbol] = transitions[state]
                # replace state with non-terminal symbol
                states_grammar[state] = nonterinal_symbol

        # replace result states into corresponding non-terminal symbols
        for nonterminal_symbol in regular_grammar:
            for action in regular_grammar[nonterminal_symbol]:
                i = 0
                # convert each state in case of multiple states as results
                for production in regular_grammar[nonterminal_symbol][action]:
                    if production in states_grammar:
                        regular_grammar[nonterminal_symbol][action][i] = states_grammar[production]
                    # set the empty productions as 'FS'
                    elif production in self.final_state:
                        regular_grammar[nonterminal_symbol][action] = ['FS']
                    i += 1
        return regular_grammar

    # give the analytical description of the grammar
    def represent_RG(self):
        nonterminal_symbols = []  # initiate the set of non-terminal symbols
        productions = []  # initiate the set of productions
        regular_grammar = self.convert_to_rgrammar()  # get the regular grammar
        for nonterminal_symbol in regular_grammar:
            # add values to the list of non-terminal symbols
            nonterminal_symbols.append(nonterminal_symbol)
            for terminal_symbol in regular_grammar[nonterminal_symbol]:
                # define productions
                for production in regular_grammar[nonterminal_symbol][terminal_symbol]:
                    if production != 'FS':
                        # in case of not final state, presente production as
                        # <non-terminal symbol> -> <terminal symbol><non-terminal symbol>
                        productions.append(nonterminal_symbol + ' -> ' + terminal_symbol + production)
                    else:
                        # in case of final state, presente production as
                        # <non-terminal symbol> -> <terminal symbol>
                        productions.append(nonterminal_symbol + ' -> ' + terminal_symbol)

        rg_representation = (f'Non-terminal symbols: {nonterminal_symbols}', f'Terminal symbols: {self.alphabet}',
                             f'Transitions: {productions}')
        return rg_representation

