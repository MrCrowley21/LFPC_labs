from itertools import combinations
from copy import deepcopy
from GNF import GNF


class CNF:

    def __init__(self, grammar):
        self.__grammar = grammar  # file with the input grammar
        self.lines = self.__read_grammar()  # Lines in the file with the input grammar
        self.nonterminals = self.__get_nonterminals()  # list of nonterminal symbols from grammar
        self.terminals = self.__get_terminals()  # list of terminal symbols from grammar
        self.productions = self.__get_productions()  # dictionary with productions of the input grammar
        self.renamings = []  # list of renamings in the grammar
        self.empty_nonterminals = self.__get_empty_nonterminals()  # list of nonterminals that derives in empty
        self.nonempty_productions = self.get_nonempty_productions()  # dictionary with nonempty productions
        self.productive_symbs = []  # list of productive symbols
        self.grammar_wt_renamings = self.__get_grammar_wt_renamings()  # dictionary with nonempty productions without renamings
        self.grammar_wt_nonproductives = self.__get_grammar_wt_nonproductives()  # dictionary without unproductive symbols
        self.accessible_symbols = self.__get_accessible_set()  # list of accessible symbols
        self.grammar_wt_unacces = self.__get_grammar_wt_unacces() # dictionary without inaccessible symbols
        self.y_index = 1  # counter for the Y index in the replacement phase

    # read the input grammar and split in lines
    def __read_grammar(self):
        with open(self.__grammar, 'r') as file:
            lines = file.read().splitlines()
        return lines

    # extract nonterminal symbols
    def __get_nonterminals(self):
        return set(self.lines[0].split(', '))

    # extract terminal symbols
    def __get_terminals(self):
        return set(self.lines[1].split(', '))

    # extract productions and write them into a dictionary
    def __get_productions(self):
        set_of_productions = []
        for line in self.lines[2:]:
            set_of_productions.append(tuple(line.split(' -> ')))
        return {vn[0]: [prod_right[1] for prod_right in set_of_productions if prod_right[0] == vn[0]] for vn in
                set_of_productions}

    # extract and remove nonterminals that derives into empty
    def __get_empty_nonterminals(self):
        self.nonempty_productions = deepcopy(self.productions)  # dictionary for grammar without nonempty productions
        empty_nonterminals = []  # list of nonterminals tha derives in empty
        for nonterminal in self.productions:
            for production in self.productions[nonterminal]:
                if production == 'epsilon':
                    # remove if derives in empty
                    self.nonempty_productions[nonterminal].remove(production)
                    empty_nonterminals.append(nonterminal)
        return empty_nonterminals

    # extract renamings and check if nonterminal indirectly derives into empty
    def __get_renamings(self, nonterminal, production):
        if len(production) == 1 and production[0] in self.nonterminals:
            # define renaming as tuple if found
            renaming = (nonterminal, production[0])
            # append renaming if it is new
            if renaming not in self.renamings:
                self.renamings.append(renaming)
                # append nonterminal to the set of nonterminals that derives in empty if derives indirectly
                if renaming[1] in self.empty_nonterminals:
                    self.empty_nonterminals.append(renaming[0])

    # get the indices of the occurrences of a character into a string
    def __get_occurrences_indices(self, s, ch):
        return [i for i, letter in enumerate(s) if letter == ch]

    # define and append new productions if nonterminal derives in empty
    def __get_new_combinations(self, remove_combinations, production, nonterminal):
        for removings in remove_combinations:
            # build the production by eliminating the indices of string of the input combination
            new_production = "".join([symbol for index, symbol in enumerate(production) if
                                      index not in removings])
            # append thd new production to dictionary of grammar without empty productions
            self.nonempty_productions[nonterminal].append(new_production)

    # build and append new productions after eliminating empty production
    def __replace_empty_productions(self, empty_nonterminal, production, nonterminal):
        if empty_nonterminal in production:
            # count the number of nonterminal with empty production in the given production
            nr_empty_symbols = production.count(empty_nonterminal)
            # return a list of empty-nonterminal occurrences in the production
            empty_occurences = self.__get_occurrences_indices(production, empty_nonterminal)
            remove_combinations = []
            # in case the productions contains other symbols apart empty-nonterminal
            if nr_empty_symbols != len(production):
                # remove all possible combinations of empty-nonterminal appearances
                for i in range(1, nr_empty_symbols + 1):
                    remove_combinations += combinations(empty_occurences, i)
                    self.__get_new_combinations(remove_combinations, production, nonterminal)
            # in case production contains only empty nonterminal
            else:
                # get the number of possible combinations if only empty-nonterminal in production
                for i in range(1, len(production)):
                    self.nonempty_productions[nonterminal].append(empty_nonterminal * i)

    # add new productions to each rule where the empty-nonterminal is present and check for indirect empty production
    def __fill_nonempty_productions(self, empty_nonterminal):
        for nonterminal in self.productions:
            for production in self.nonempty_productions[nonterminal]:
                self.__get_renamings(nonterminal, production)
                self.__replace_empty_productions(empty_nonterminal, production, nonterminal)

    # build the grammar without empty productions
    def get_nonempty_productions(self):
        # self.nonempty_productions = deepcopy(self.productions)
        while len(self.empty_nonterminals) > 0:
            for empty_nonterminal in self.empty_nonterminals:
                self.__fill_nonempty_productions(empty_nonterminal)
                self.empty_nonterminals.remove(empty_nonterminal)
        return self.nonempty_productions

    # replace the renaming with its productions
    def __replace_renamings(self):
        replaced = False  # check if everything was replaced
        while not replaced and len(self.renamings) > 0:
            for renaming in self.renamings:
                left = renaming[0]
                right = renaming[1]
                for production in self.grammar_wt_renamings[right]:
                    # print(renaming)
                    if production not in self.grammar_wt_renamings[left]:
                        self.grammar_wt_renamings[left].append(production)
                    else:
                        replaced = True

    # identify, remove and replace renamings if exist
    def __get_grammar_wt_renamings(self):
        self.grammar_wt_renamings = deepcopy(self.nonempty_productions)
        for nonterminal in self.grammar_wt_renamings:
            for production in self.grammar_wt_renamings[nonterminal]:
                self.__get_renamings(nonterminal, production)
                # remove renaming if exists
                if len(production) == 1 and production[0] in self.nonterminals:
                    self.grammar_wt_renamings[nonterminal].remove(production)
        # replaced removed renaming with its values
        self.__replace_renamings()
        return self.grammar_wt_renamings

    # get immediate productive symbols (that derives into terminal)
    def __get_direct_productive_symbols(self):
        # list of productive symbols
        self.productive_symbs = []
        for nonterminal in self.grammar_wt_nonproductives:
            for production in self.grammar_wt_nonproductives[nonterminal]:
                # add in list of productive symbols if derives in terminal and no there yet
                if len(production) == 1 and production[0] in self.terminals and nonterminal not in self.productive_symbs:
                    self.productive_symbs.append(nonterminal)
        return self.productive_symbs

    # update the list of productive symbols with indirect productive symbols
    # (that derives in combination o terminals and productive nonterminals)
    def __update_productive_symbols(self, nonterminal):
        updated = False  # check if the list was updated
        for production in self.grammar_wt_nonproductives[nonterminal]:
            # counts the length of productive symbols in the production
            count = 0
            while count < len(production) and (production[count] in self.productive_symbs or production[count] in
                                                   self.terminals):
                count += 1
            # if all symbols are productive, update the list and stop
            if count == len(production):
                self.productive_symbs.append(nonterminal)
            else:
                updated = True
        return updated

    # remove unproductive productions from the grammar
    def __remove_unproductive_productions(self, symbol):
        # check and remove all occurrences
        for nonterminal in self.grammar_wt_nonproductives:
            for production in self.grammar_wt_nonproductives[nonterminal]:
                if symbol in production:
                    self.grammar_wt_nonproductives[nonterminal].remove(production)

    # get the productive symbols
    def __get_productive_prods(self):
        self.grammar_wt_nonproductives = deepcopy(self.grammar_wt_renamings)
        self.__get_direct_productive_symbols()
        updated = True  # check if productions were updated
        while updated:
            updated = False
            for nonterminal in self.grammar_wt_nonproductives:
                if nonterminal not in self.productive_symbs:
                    if self.__update_productive_symbols(nonterminal):
                        updated = self.__update_productive_symbols(nonterminal)

    # build the grammar without unproductive symbols
    def __get_grammar_wt_nonproductives(self):
        # get the set of productive symbols
        self.__get_productive_prods()
        # remove symbol if not productive
        for nonterminal in self.nonterminals:
            if nonterminal not in self.productive_symbs:
                del self.grammar_wt_nonproductives[nonterminal]
                self.__remove_unproductive_productions(nonterminal)
        return self.grammar_wt_nonproductives

    # update the set of accessible symbols with all accessible symbols from 'S'
    def __update_accesibles(self, nonterminal):
        for production in self.grammar_wt_unacces[nonterminal]:
            for symbol in production:
                if symbol not in self.accessible_symbols and symbol in self.grammar_wt_unacces:
                    self.accessible_symbols.append(symbol)

    # get the set of accessible symbols
    def __get_accessible_set(self):
        self.grammar_wt_unacces = deepcopy(self.grammar_wt_nonproductives)
        self.accessible_symbols = []  # list of accessible symbols
        self.accessible_symbols.append('S')  # append start-node by default
        # add symbols to the list of accessible symbols
        for nonterminal in self.accessible_symbols:
            self.__update_accesibles(nonterminal)
        return self.accessible_symbols

    # build the grammar without inaccessible symbols
    def __get_grammar_wt_unacces(self):
        # remove inaccessible symbols and their productions
        for nonterminal in self.productive_symbs:
            if nonterminal not in self.accessible_symbols:
                del self.grammar_wt_unacces[nonterminal]
        return self.grammar_wt_unacces

    # get terminals that do not need transformation (are the only production of a valid nonterminals)
    def __get_transformed_terminals(self):
        transformed_terminals = []  # list of terminals that should not be transformed
        for nonterminal in self.cnf_grammar_terminal:
            production = self.cnf_grammar_terminal[nonterminal]
            if len(production) == 1:
                if production[0] in self.terminals:
                    transformed_terminals.append(production[0])
                    # append the value of the corresponded nonterminal to the list of nonterminals
                    # that derives into a single terminal
                    self.replaced_terminal_dict[production[0]] = nonterminal
        return transformed_terminals

    # get the list of the terminals that should be transformed
    def __get_to_transform_terminals(self):
        transformed_terminals = self.__get_transformed_terminals()
        to_transform_terminals = []  # list of terminals that should be transformed
        for symbol in self.terminals:
            if symbol not in transformed_terminals:
                # append symbol if necessary
                to_transform_terminals.append(symbol)
        return to_transform_terminals

    # transform terminals into productions of nonterminals
    def __transform_terminals(self):
        self.replaced_terminal_dict = {}  # keep the replaced terminals
        self.cnf_grammar_terminal = deepcopy(self.grammar_wt_unacces)
        to_transform_terminals = self.__get_to_transform_terminals()
        terminal_to_nonterminal = []  # keep the transformed terminals
        for symbol in to_transform_terminals:
            # note encoded terminals with X and index according to the position in list
            terminal_to_nonterminal.append('X' + str(ord(symbol) - 96))
            self.replaced_terminal_dict[symbol] = 'X' + str(ord(symbol) - 96)
            self.cnf_grammar_terminal[terminal_to_nonterminal[-1]] = [symbol]
        # replace all terminals in composed productions with their nonterminal equivalents
        for nonterminal in self.cnf_grammar_terminal:
            self.__replace_terminals(nonterminal)

    # replace terminals in the productions
    def __replace_terminals(self, nonterminal):
        i = 0
        for production in self.cnf_grammar_terminal[nonterminal]:
            if len(production) >= 2:
                index = 0  # index of the current character in production
                replaced = 0  # check if nonterminal symbols were replaced
                while index < len(production):
                    # if find terminal in a composed production, replace it with its equivalent
                    if production[index] in self.replaced_terminal_dict:
                        production = \
                            production.replace(production[index], self.replaced_terminal_dict[production[index]])
                        self.cnf_grammar_terminal[nonterminal][i] = production
                    # replace nonterminals with <nonterminal><black_space>
                    if production[index] in self.nonterminals and not replaced:
                        production = production.replace(production[index], production[index] + ' ')
                        # replace the value of production into the grammar
                        self.cnf_grammar_terminal[nonterminal][i] = production
                        replaced = 1
                        index += 1
                    index += 1
            i += 1

    # replace current values of productions with equivalent one
    def __modify_production(self, production, nonterminal, i, index):
        production = production.replace(index, self.replaced_nonterminal_dict[index])
        self.cnf_grammar_nonterminal[nonterminal][i] = production
        return production

    # if equivalence of the combination already exists, replace with it
    def __replace_existent_nonterminal_productions(self, production, nonterminal, i):
        replaced = 0  # check if was replaced
        # check first two symbols
        if production[(len(production) - 4):] in self.replaced_nonterminal_dict:
            production = self.__modify_production(production, nonterminal, i, production[(len(production) - 4):])
            replaced += 1
        # check the last two symbols
        if production[:4] in self.replaced_nonterminal_dict:
            production = self.__modify_production(production, nonterminal, i, production[:4])
            replaced += 1
        return replaced, production

    # replace nonterminals with their equivalences
    def __replace_nonterminals(self, production, nonterminal, i):
        # if more than two nonterminals as production (2 nonterminals + 2 black spaces)
        if len(production) > 4:
            # check if extreme symbols have already equivalences
            replaced, production = self.__replace_existent_nonterminal_productions(production, nonterminal, i)
            # if extreme symbols does not have equivalences
            if not replaced:
                # make an equivalece for the first two values
                self.replaced_nonterminal_dict[production[:4]] = 'Y' + str(self.y_index)
                self.y_index += 1
                production = self.__modify_production(production, nonterminal, i, production[:4])
                # if possible, make another equivalence
                if len(production) > 4:
                    # check extreme values
                    replaced, production = self.__replace_existent_nonterminal_productions(production, nonterminal, i)
                    # if not extreme values, replace last two symbols
                    if not replaced:
                        self.replaced_nonterminal_dict[production[(len(production) - 4):]] = 'Y' + str(self.y_index)
                        self.y_index += 1
                        production = \
                            self.__modify_production(production, nonterminal, i, production[(len(production) - 4):])
            # recursive call of the function until done
            self.__replace_nonterminals(production, nonterminal, i)

    # replace productions if needed
    def __transform_nonterminals(self):
        self.cnf_grammar_nonterminal = deepcopy(self.cnf_grammar_terminal)
        self.replaced_nonterminal_dict = {}
        for nonterminal in self.cnf_grammar_nonterminal:
            i = 0
            # if more than two symbols in production, replace them
            for production in self.cnf_grammar_nonterminal[nonterminal]:
                if len(production) > 4:
                    self.__replace_nonterminals(production, nonterminal, i)
                i += 1
        self.__update_nonterminals()

    # add equivalences (notations) in the grammar
    def __update_nonterminals(self):
        for production in self.replaced_nonterminal_dict:
            key = self.replaced_nonterminal_dict[production]
            self.cnf_grammar_nonterminal[key] = [production]

    # convert grammar to Chomsky Normal Form
    def transform_to_CNF(self):
        self.y_index = 0
        self.cnf_grammar = {}  # dictionary with converted grammar
        self.__transform_terminals()  # transform terminal symbols
        self.__transform_nonterminals()  # transform nonterminal symbols
        # remove helper spaces and add rules to the final form of grammar
        for nonterminal in self.cnf_grammar_nonterminal:
            self.cnf_grammar[nonterminal] = []
            for production in self.cnf_grammar_nonterminal[nonterminal]:
                self.cnf_grammar[nonterminal].append(production.replace(' ', ''))
        return self.cnf_grammar

    # illustrate the steps of converting the grammar into Chomsky Normal Form
    def print_CNF_transform_with_steps(self):
        print('Input rules:\n', self.productions)
        print('Step 1. Eliminate epsilon productions\n', self.nonempty_productions)
        print('Step 2. Eliminate renamings\n', self.grammar_wt_renamings)
        print('Step 3. Eliminate unproductive symbols\n', self.grammar_wt_nonproductives)
        print('Step 4. Eliminate inaccessible symbols\n', self.grammar_wt_unacces)
        print('Step 5. Convert to Chomsky Normal Form\n', self.transform_to_CNF())

    # illustrate the steps of converting the grammar into Greibach Normal Form
    def transform_to_GNF(self):
        self.y_index = 0
        self.transform_to_CNF()
        gnf = GNF(self.cnf_grammar.keys(), self.terminals, self.cnf_grammar)
        print('Initial grammar:\n', self.productions)
        print('Chomsky Normal Form:\n', self.transform_to_CNF())
        gnf.show_transitions()
