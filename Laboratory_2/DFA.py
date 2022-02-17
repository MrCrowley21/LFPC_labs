from NFA import NFA

class DFA:

    # initiation function
    def __init__(self, automaton):
        self.__automaton = automaton  # the input FA
        self.dfa_representation = self.transform_to_DFA()  # the DFA representation as dictionary
        self.initial_state = self.__get_initial_state()  # the initial state of DFA
        self.final_state = self.__get_final_state()  # the final states of DFA

    # transform the input FA into DFA
    def transform_to_DFA(self):
        return NFA(self.__automaton).transform_to_DFA()

    # show the table of transformation to DFA
    def get_transformation_table(self):
        return NFA(self.__automaton).get_transformation_table()

    # give the initial state of DFA
    def __get_initial_state(self):
        return NFA(self.__automaton).initial_state

    # give the final states of DFA
    def __get_final_state(self):
        return NFA(self.__automaton).get_dfa_final_state(self.dfa_representation)
