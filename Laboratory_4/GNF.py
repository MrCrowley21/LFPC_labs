from copy import deepcopy


class GNF:

    def __init__(self, nonterminals, terminals, productions):
        # self.__grammar = grammar  # file with the input grammar
        self.nonterminals = nonterminals  # list of nonterminal symbols from grammar
        self.terminals = terminals  # list of terminal symbols from grammar
        self.productions = productions  # dictionary with productions of the input grammar
        self.productions_wt_recursion = {}  # dictionary with productions without left recursion
        self.first_nonterminal_productions = {}  # dictionary with the leading nonterminals in each production
        self.left_recursion = []  # list of nonterminals and their left recursion transitions
        self.accessible_symbols = []  # list of accessible symbols
        self.prod_leading_terminals = []  # list of terminals that leading production
        self.gnf_grammar = {}  # grammar in GNF
        self.iterate = 2  # the index of nonterminal after left factorization

    # Create a dictionary with the first nonterminals for each nonterminal
    def get_first_symbol_prod(self, grammar):
        self.first_nonterminal_productions = {}
        for nonteminal in grammar:
            self.first_nonterminal_productions[nonteminal] = []
            for production in grammar[nonteminal]:
                if production[0] in self.nonterminals and \
                        production[0] not in self.first_nonterminal_productions[nonteminal]:
                    self.first_nonterminal_productions[nonteminal].append(production[0])

    # Search for cycles in dictionary with first nonteminals of productions (dfs algorithm)
    def __get_cycles(self, graph, start, end):
        nodes = [(start, [])]
        while nodes:
            state, path = nodes.pop()
            # ends when comes to the first node or no more path
            if path and state == end:
                yield path
                continue
            # Check if a node is visited
            for next_state in graph[state]:
                if next_state in path:
                    continue
                nodes.append((next_state, path + [next_state]))

    # Build cycles for nodes if exists
    def __get_left_cycles(self, grammar):
        self.left_recursion = [[node] + path for node in grammar
                                        for path in self.__get_cycles(grammar, node, node)]

    # Remove repetitive recursions from the list
    def __get_left_recursion(self, grammar):
        self.__get_left_cycles(grammar)
        path_index = 0
        while path_index < len(self.left_recursion):
            index = path_index + 1
            while index < len(self.left_recursion):
                # Chech if two recursions involves the same symbols
                if set(self.left_recursion[path_index]) == set(self.left_recursion[index]):
                    del self.left_recursion[index]
                index += 1
            path_index += 1

    # Check which element that leads to left recursion must be replaced and create a list of replacements
    def get_new_productions(self, recursion, i, replace, grammar):
        new_replace = []
        for production in grammar[recursion[i]]:
            if production[0] == recursion[i + 1]:
                for target in replace:
                    # Generate new production
                    result = target + production[1:]
                    if result not in new_replace:
                        new_replace.append(result)
        return new_replace

    # Remove productions which starts with nonterminal in recursive path
    def remove_old_productions(self, recursion, grammar):
        for production in grammar[recursion[0]]:
            if production[0] == recursion[1]:
                grammar[recursion[0]].remove(production)

    # Delete rplaced productions and create replacements
    def get_symbols_indirect_recursion(self, recursion, grammar):
        replace = deepcopy(grammar[recursion[-2]])
        i = len(recursion) - 3
        while i >= 0:
            new_replace = self.get_new_productions(recursion, i, replace, grammar)
            self.remove_old_productions(recursion, grammar)
            replace.clear()
            replace += new_replace
            i -= 1
        return replace

    # Append created productions to the dictionary
    def add_new_productions(self, new_productions, recursion, grammar):
        for production in new_productions:
            if production not in grammar[recursion[0]]:
                grammar[recursion[0]].append(production)

    # Transform indirect recursion into direct
    def remove_indirect_left_recursion(self, grammar):
        self.replace_first_terminal(grammar)
        for recursion in self.left_recursion:
            if len(recursion) > 2:
                new_productions = self.get_symbols_indirect_recursion(recursion, grammar)
                self.add_new_productions(new_productions, recursion, grammar)

    # Replace first terminal for convenience
    def replace_first_terminal(self, grammar):
        # self.__get_left_recursion()
        for nonterminal in self.productions:
            grammar[nonterminal] = []
            for production in self.productions[nonterminal]:
                # Replace our replacemants from CNF
                if production[0] == 'X' or production[0] == 'Y':
                    while production[0] == 'X' or production[0] == 'Y':
                        production = production.replace(production[:2], self.productions[production[:2]][0])
                    grammar[nonterminal].append(production)
                else:
                    grammar[nonterminal].append(production)

    # Create new rules to convert recursion
    def define_new_nonterminal(self, nonterminal, recursive_productions, grammar):
        nonrecursive_productions = []
        index = 0
        while index < len(grammar[nonterminal]):
            production = grammar[nonterminal][index]
            i = 1
            # Check if double symbol
            if len(production) > 1:
                if '0' <= production[1] <= '9':
                    i = 2
            # Append productions to newly created rules and recursive list
            if production[0:i] == nonterminal:
                recursive_productions.append([production])
                grammar[nonterminal].remove(production)
                grammar[nonterminal + '1'].append(production[i:])
                grammar[nonterminal + '1'].append(production[i:] + nonterminal + '1')
                index -= 1
            else:
                # append nonrecursivly result productions
                nonrecursive_productions.append(production + nonterminal + '1')
            index += 1
        return nonrecursive_productions, recursive_productions

    # Append previously created lists to their places. Create ne rules in dictionary
    def eliminate_left_recursion(self, grammar):
        self.recursive_nonterminals = []
        self.remove_indirect_left_recursion(grammar)
        for recursion in self.left_recursion:
            recursive_productions = []
            nonterminal = recursion[0]
            if nonterminal not in self.recursive_nonterminals:
                grammar[nonterminal + '1'] = []
                nonrecursive_productions, recursive_productions = \
                    self.define_new_nonterminal(nonterminal, recursive_productions, grammar)
                grammar[nonterminal] += nonrecursive_productions
            self.recursive_nonterminals.append(nonterminal)
        return grammar

    # update the set of accessible symbols with all accessible symbols from 'S'
    def __update_accesibles(self, nonterminal, grammar):
        for production in grammar[nonterminal]:
            index = 0
            while index < len(production):
                i = 1
                while index + i < len(production):
                    if '0' <= production[index + i] <= '9':
                        i += 1

                    else:
                        break
                symbol = production[index]
                if index + 1 < len(production):
                    if '0' <= production[index + 1] <= '9':
                        symbol += production[index + 1: index + i]
                if symbol not in self.accessible_symbols and symbol in grammar:
                    self.accessible_symbols.append(symbol)
                index += i

    # get the set of accessible symbols
    def __get_accessible_set(self, grammar):
        self.accessible_symbols.append('S')  # append start-node by default
        # add symbols to the list of accessible symbols
        for nonterminal in self.accessible_symbols:
            self.__update_accesibles(nonterminal, grammar)
        return self.accessible_symbols

    # build the grammar without inaccessible symbols
    def get_grammar_wt_unacces(self, grammar):
        # remove inaccessible symbols and their productions
        self.__get_accessible_set(grammar)
        for nonterminal in self.productions:
            if nonterminal not in self.accessible_symbols:
                del grammar[nonterminal]
        return grammar

    # Search for productions for each value starting with terminal
    def check_leading_terminal(self, grammar):
        for nonterminal in grammar:
            match = True
            # Check if all productions starts with terminals
            if nonterminal not in self.prod_leading_terminals:
                for production in grammar[nonterminal]:
                    if production[0] not in self.terminals:
                        match = False
            if match and nonterminal not in self.prod_leading_terminals:
                self.prod_leading_terminals.append(nonterminal)

    # Replace leading nonterminals using productions where each starts with terminal
    def replace_leading_nonterm(self, index, nonterminal, grammar):
        inner_index = 0
        while inner_index < len(grammar[nonterminal]):
            production = grammar[nonterminal][inner_index]
            # check if in any case may be replaced by terminal
            i = 1
            if len(production) > 1:
                if '0' <= production[1] <= '9':
                    i = 2
            if production[0] == self.prod_leading_terminals[index]:
                for result in grammar[self.prod_leading_terminals[index]]:
                    new_production = result + production[1:]
                    if new_production not in grammar[nonterminal]:
                        grammar[nonterminal].append(new_production)
                grammar[nonterminal].remove(production)
                inner_index -= 1
            inner_index += 1

    # Transform CNF to GNF
    def transform_to_gnf(self, grammar):
        index = 0
        self.check_leading_terminal(grammar)
        while index < len(self.prod_leading_terminals):
            for nonterminal in grammar:
                self.replace_leading_nonterm(index, nonterminal, grammar)
            self.check_leading_terminal(grammar)
            index += 1

    # Get the largest common part of two strings
    def get_left_factor_length(self, prod_1, prod_2):
        i = 0
        for i, pair in enumerate(zip(prod_1, prod_2)):
            if pair[0] != pair[1]:
                if '0' <= pair[0] <= '9' or '0' <= pair[1] <= '9':
                    return i - 1
                return i
        return 0

    # Group productions by the largest common factor
    def group_by_factor(self, candidates):
        longest = 0
        previous = []
        for production in candidates:
            if previous:
                factor_length = self.get_left_factor_length(production, previous[-1])
                if (factor_length != longest and longest != 0) or factor_length == 0:
                    yield previous, longest
                    longest = 0
                    previous = []
                else:
                    longest = factor_length
            previous.append(production)
        if previous:
            yield previous, longest

    # Append to new dictionary unit terminal productions and note possible left factor
    def select_left_factoring(self, nonterminal):
        if nonterminal not in self.gnf_grammar:
            self.gnf_grammar[nonterminal] = []
        lf_candidates = []
        for production in self.productions_wt_recursion[nonterminal]:
            if len(production) == 1:
                self.gnf_grammar[nonterminal].append(production)
            else:
                lf_candidates.append(production)
        return lf_candidates

    # Replace factoring using the rules (create new production for factors)
    def transform_common_factor(self, longest, nonterminal, productions):
        index = 0
        if longest == len(productions[0]):
            self.gnf_grammar[nonterminal].append(productions[0])
            index += 1
        new_nonterminal = nonterminal + str(self.iterate)
        self.iterate += 1
        self.gnf_grammar[nonterminal].append(productions[0][:longest] + new_nonterminal)
        self.gnf_grammar[new_nonterminal] = []
        while index < len(productions):
            self.gnf_grammar[new_nonterminal].append(productions[index][longest:])
            index += 1

    # Remove old rules and append newly created ones
    def remove_left_factoring(self):
        for nonterminal in self.productions_wt_recursion:
            candidates = self.select_left_factoring(nonterminal)
            candidates.sort()
            self.iterate = 2
            for group in self.group_by_factor(candidates):
                productions = group[0]
                is_left_factoring = False
                for production in productions:
                    if production[-(len(nonterminal)):] == nonterminal:
                        is_left_factoring = True
                        break
                longest = group[1]
                if len(productions) > 1 and is_left_factoring:
                    self.transform_common_factor(longest, nonterminal, productions)
                else:
                    for production in productions:
                        self.gnf_grammar[nonterminal].append(production)
        return self.gnf_grammar

    # Build Greibach normal form from grammar
    def get_gnf(self):
        self.get_first_symbol_prod(self.productions)
        self.__get_left_recursion(self.first_nonterminal_productions)
        self.eliminate_left_recursion(self.productions_wt_recursion)
        self.get_grammar_wt_unacces(self.productions_wt_recursion)
        self.transform_to_gnf(self.productions_wt_recursion)
        return self.productions_wt_recursion

    # Eliminate left factoring by formula
    def get_gnf_wt_left_factoring(self):
        self.get_gnf()
        self.remove_left_factoring()
        self.productions = deepcopy(self.gnf_grammar)
        self.get_first_symbol_prod(self.gnf_grammar)
        self.__get_left_recursion(self.first_nonterminal_productions)
        self.eliminate_left_recursion(self.gnf_grammar)
        self.get_grammar_wt_unacces(self.gnf_grammar)
        self.transform_to_gnf(self.gnf_grammar)
        return self.gnf_grammar

    # Illustrate the steps of converting the grammar into Greibach Normal Form
    def show_transitions(self):
        print('Greibach Normal Form Grammar:\n', self.get_gnf())
        print('Left Factoring removing:\n', self.get_gnf_wt_left_factoring())
