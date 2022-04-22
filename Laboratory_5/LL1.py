from copy import deepcopy


class LL1:

    def __init__(self, grammar):
        self.__grammar = grammar  # file with the input grammar
        self.lines = self.__read_grammar()  # Lines in the file with the input grammar
        self.nonterminals = self.__get_nonterminals()  # list of nonterminal symbols from grammar
        self.start = self.__get_start()  # the start symbol
        self.terminals = self.__get_terminals()  # list of terminal symbols from grammar
        self.productions = self.__get_productions()  # dictionary with productions of the input grammar
        self.first = {}  # dictionary of FRST(symbol)
        self.follow = {}  # dictionary of FOLLOW(symbol)
        self.productions_wt_recursion = {}  # dictionary with productions without left recursion
        self.first_nonterminal_productions = {}  # dictionary with the leading nonterminals in each production
        self.left_recursion = []  # list of nonterminals and their left recursion transitions
        self.grammar_wt_left_factoring = {}  # dictionary with the grammar with removed left factoring
        self.parsing_table = {}  # dictionary with the values from the parsing table

    # read the input grammar and split in lines
    def __read_grammar(self):
        with open(self.__grammar, 'r') as file:
            lines = file.read().splitlines()
        return lines

    # extract nonterminal symbols
    def __get_nonterminals(self):
        return set(self.lines[0].split(', '))

    # extract nonterminal symbols
    def __get_start(self):
        return self.lines[1]

    # extract terminal symbols
    def __get_terminals(self):
        return set(self.lines[2].split(', '))

    # extract productions and write them into a dictionary
    def __get_productions(self):
        set_of_productions = []
        for line in self.lines[3:]:
            set_of_productions.append(tuple(line.split(' -> ')))
        return {vn[0]: [prod_right[1] for prod_right in set_of_productions if prod_right[0] == vn[0]] for vn in
                set_of_productions}

    # Create a dictionary with the first nonterminals for each nonterminal
    def __get_first_symbol_prod(self, grammar):
        self.first_nonterminal_productions = {}
        for nonteminal in grammar:
            self.first_nonterminal_productions[nonteminal] = []
            self.first[nonteminal] = []
            for production in grammar[nonteminal]:
                self.first[nonteminal].append(production[0])
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
                # Check if two recursions involves the same symbols
                if set(self.left_recursion[path_index]) == set(self.left_recursion[index]):
                    del self.left_recursion[index]
                index += 1
            path_index += 1

    # Check which element that leads to left recursion must be replaced and create a list of replacements
    def __get_new_productions(self, recursion, i, replace, grammar):
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
    def __remove_old_productions(self, recursion, grammar):
        for production in grammar[recursion[0]]:
            if production[0] == recursion[1]:
                grammar[recursion[0]].remove(production)

    # Delete rplaced productions and create replacements
    def __get_symbols_indirect_recursion(self, recursion, grammar):
        replace = deepcopy(grammar[recursion[-2]])
        i = len(recursion) - 3
        while i >= 0:
            new_replace = self.__get_new_productions(recursion, i, replace, grammar)
            self.__remove_old_productions(recursion, grammar)
            replace.clear()
            replace += new_replace
            i -= 1
        return replace

    # Append created productions to the dictionary
    def __add_new_productions(self, new_productions, recursion, grammar):
        for production in new_productions:
            if production not in grammar[recursion[0]]:
                grammar[recursion[0]].append(production)

    # Transform indirect recursion into direct
    def __remove_indirect_left_recursion(self, grammar):
        for recursion in self.left_recursion:
            if len(recursion) > 2:
                new_productions = self.__get_symbols_indirect_recursion(recursion, grammar)
                self.__add_new_productions(new_productions, recursion, grammar)

    # Create new rules to convert recursion
    def __define_new_nonterminal(self, nonterminal, recursive_productions, grammar):
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
                # append nonrecursive result productions
                if production != 'empty':
                    nonrecursive_productions.append(production + nonterminal + '1')
                else:
                    nonrecursive_productions.append(nonterminal + '1')
            index += 1
        return nonrecursive_productions, recursive_productions

    # Append previously created lists to their places. Create ne rules in dictionary
    def __eliminate_left_recursion(self, grammar):
        self.recursive_nonterminals = []
        self.__remove_indirect_left_recursion(grammar)
        for recursion in self.left_recursion:
            recursive_productions = []
            nonterminal = recursion[0]
            if nonterminal not in self.recursive_nonterminals:
                grammar[nonterminal + '1'] = []
                nonrecursive_productions, recursive_productions = \
                    self.__define_new_nonterminal(nonterminal, recursive_productions, grammar)
                grammar[nonterminal] += nonrecursive_productions
            self.recursive_nonterminals.append(nonterminal)
        return grammar

    # Get the largest common part of two strings
    def __get_left_factor_length(self, prod_1, prod_2):
        j = 0
        for i, pair in enumerate(zip(prod_1, prod_2)):
            if pair[0] != pair[1]:
                if '0' <= pair[0] <= '9' or '0' <= pair[1] <= '9':
                    return i - 1
                return i
            j = i + 1
        return j

    # Group productions by the largest common factor
    def __group_by_factor(self, candidates):
        longest = 0
        previous = []
        for production in candidates:
            if previous:
                factor_length = self.__get_left_factor_length(production, previous[-1])
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
    def __select_left_factoring(self, nonterminal):
        if nonterminal not in self.grammar_wt_left_factoring:
            self.grammar_wt_left_factoring[nonterminal] = []
        lf_candidates = []
        for production in self.productions_wt_recursion[nonterminal]:
            # analyze all production but empty
            if production != 'empty':
                lf_candidates.append(production)
        return lf_candidates

    # Replace factoring using the rules (create new production for factors)
    def __transform_common_factor(self, longest, nonterminal, productions):
        index = 0
        new_nonterminal = nonterminal + str(self.iterate)
        self.iterate += 1
        self.grammar_wt_left_factoring[nonterminal].append(productions[0][:longest] + new_nonterminal)
        self.grammar_wt_left_factoring[new_nonterminal] = []
        while index < len(productions):
            if len(productions[index][longest:]) == 0 and \
                    'empty' not in self.grammar_wt_left_factoring[new_nonterminal]:
                self.grammar_wt_left_factoring[new_nonterminal].append('empty')
            else:
                self.grammar_wt_left_factoring[new_nonterminal].append(productions[index][longest:])
            index += 1

    # Remove old rules and append newly created ones
    def __remove_left_factoring(self):
        for nonterminal in self.productions_wt_recursion:
            candidates = self.__select_left_factoring(nonterminal)
            candidates.sort()
            self.iterate = 2
            for group in self.__group_by_factor(candidates):
                productions = group[0]
                longest = group[1]
                if len(productions) > 1:
                    self.__transform_common_factor(longest, nonterminal, productions)
                else:
                    for production in productions:
                        self.grammar_wt_left_factoring[nonterminal].append(production)
            # add the 'empty' value from the original grammar in case exists
            if 'empty' in self.productions_wt_recursion[nonterminal]:
                self.grammar_wt_left_factoring[nonterminal].append('empty')
        return self.grammar_wt_left_factoring

    # normalize the original grammar before starting computing forward
    def __initiate_LL1(self):
        self.productions_wt_recursion = deepcopy(self.productions)
        self.__get_first_symbol_prod(self.productions)
        self.__get_left_recursion(self.first_nonterminal_productions)
        self.__eliminate_left_recursion(self.productions_wt_recursion)
        return self.__remove_left_factoring()

    # in case first is nonterminal, replace it with its first values
    def __replace_first_nonterminal(self, nonterminal):
        index = 0
        while index < len(self.first[nonterminal]):
            symbol = self.first[nonterminal][index]
            if symbol in self.grammar_wt_left_factoring:
                index -= 1
                # remove nonterminal value
                self.first[nonterminal].remove(symbol)
                # append all first of the analyzed nonterminal value
                for new_symbol in self.first[symbol]:
                    if new_symbol not in self.first[nonterminal]:
                        self.first[nonterminal].append(new_symbol)
            index += 1

    # in case of composed nonterminal, get its correct whole value
    def __get_whole_nonterminal(self, index, symbol, production):
        while index < len(production) and '0' <= production[index] <= '9':
            symbol += production[index]
            index += 1
        return symbol

    # analyze first in case the first symbol has empty productions
    def __get_first_in_case_empty(self, nonterminal, symbol, production, is_empty):
        start = 0
        index = 1
        if symbol in self.grammar_wt_left_factoring and 'empty' in self.grammar_wt_left_factoring[symbol]:
            # check all the next production till the first one has an empty production
            while is_empty and index < len(production):
                start = index
                index += 1
                # get the current symbol for First
                new_symbol = production[start:index]
                new_symbol = self.__get_whole_nonterminal(index, new_symbol, production)
                self.first[nonterminal].append(new_symbol)
                # check if the ne first symbols has empty productions
                first_symbol = production[start:index]
                if first_symbol in self.nonterminals and \
                        'empty' in self.grammar_wt_left_factoring[first_symbol]:
                    is_empty = True
                else:
                    is_empty = False

    def __get_first_table(self):
        is_empty = True  # the state of first symbol
        for nonterminal in self.grammar_wt_left_factoring:
            start = 0
            index = 1
            self.first[nonterminal] = []
            for production in self.grammar_wt_left_factoring[nonterminal]:
                # check productions that are not empty
                if 'empty' not in production:
                    symbol = production[start]
                    symbol = self.__get_whole_nonterminal(index, symbol, production)
                    self.first[nonterminal].append(symbol)
                    # check if empty productions in the current first
                    self.__get_first_in_case_empty(nonterminal, symbol, production, is_empty)
        # replace values of nonterminal first
        for nonterminal in self.first:
            self.__replace_first_nonterminal(nonterminal)
        # append empty productions if exist
        for nonterminal in self.grammar_wt_left_factoring:
            if 'empty' in self.grammar_wt_left_factoring[nonterminal]:
                self.first[nonterminal].append('empty')
        return self.first

    #
    def __get_follow_symbols(self, index, production, symbol):
        # get the follow symbol
        follow = production[index]
        index += 1
        while index < len(production) and '0' <= production[index] <= '9':
            follow += production[index]
            index += 1
        # append follow if terminal
        if follow in self.terminals:
            self.follow[symbol].append(follow)
        else:
            # append FIRST(symbol) if follow nonterminal
            for first in self.first[follow]:
                if first not in self.follow[symbol] and first != 'empty':
                    self.follow[symbol].append(first)
            # recursively call in case follow is empty
            if 'empty' in self.first[follow] and index < len(production):
                self.__get_follow_symbols(index - 2, production, symbol)

    # append follows to the superset from the subset
    def __add_follows(self, start, index, production, nonterminal, is_complete):
        is_complete = True
        # get follow symbol
        while production[start:index] not in self.follow:
            start -= 1
        symbol = production[start:index]
        for follow in self.follow[nonterminal]:
            if follow not in self.follow[symbol]:
                self.follow[symbol].append(follow)
                is_complete = False
        # add subset in case empty productions
        if 'empty' in self.grammar_wt_left_factoring[symbol] and len(production) > len(symbol):
            if start > 0 and production[start - 1] not in self.terminals:
                is_complete = is_complete and self.__add_follows(start - 1, start, production, nonterminal, is_complete)
        return is_complete

    def __get_subset_follow(self, nonterminal):
        is_complete = True
        for production in self.grammar_wt_left_factoring[nonterminal]:
            # find superset
            if production[-1] not in self.terminals and production != 'empty':
                start = len(production) - 1
                index = len(production)
                # check any additions
                is_complete = is_complete and self.__add_follows(start, index, production, nonterminal, is_complete)
        return is_complete

    def __find_follow(self, symbol):
        for nonterminal in self.grammar_wt_left_factoring:
            for production in self.grammar_wt_left_factoring[nonterminal]:
                if symbol in production:
                    # get the follow symbols of the current symbol
                    index = production.index(symbol) + len(symbol)
                    if index < len(production) and (production[index] <= '0' or production[index] >= '9'):
                        self.__get_follow_symbols(index, production, symbol)

    # get the table for follow
    def __get_follow_table(self):
        # initiate follow dictionary
        for nonterminal in self.grammar_wt_left_factoring:
            self.follow[nonterminal] = []
            if nonterminal == self.start:
                self.follow[nonterminal].append('$')
        # find the direct follows
        for nonterminal in self.follow:
            self.__find_follow(nonterminal)
        is_complete = False  # mark if the whole subsets was added to the main set
        while not is_complete:
            is_complete = True
            # add subsets to the main set
            for nonterminal in self.follow:
                is_complete = is_complete * self.__get_subset_follow(nonterminal)
        return self.follow

    # get the parsing table
    def __get_parsing_table(self):
        # initiate parsing dictionary
        for nonterminal in self.grammar_wt_left_factoring:
            self.parsing_table[nonterminal] = {}
            for production in self.grammar_wt_left_factoring[nonterminal]:
                # in case of non-empty productions
                # in case production starts with a terminal
                if production[0] in self.terminals and production != 'empty':
                    self.parsing_table[nonterminal][production[0]] = production
                # in case first symbol in nonterminal
                elif production != 'empty':
                    # add to the table to each terminal symbol but empty
                    for symbol in self.first[nonterminal]:
                        if symbol != 'empty':
                            self.parsing_table[nonterminal][symbol] = production
                # complete in case empty productions in first
                if 'empty' in self.first[nonterminal]:
                    # add empty to the values from follow
                    for follow in self.follow[nonterminal]:
                        self.parsing_table[nonterminal][follow] = ''
        return self.parsing_table

    def parse(self, word):
        # initiate the grammar by normalizing it
        self.__initiate_LL1()
        print('Normalized grammar:\n', self.grammar_wt_left_factoring)
        # build the necessary tables for First, Follow and the parsing table
        print('FIRST(symbol):\n', self.__get_first_table())
        print('FOLLOW(symbol):\n', self.__get_follow_table())
        print('Parsing table:\n', self.__get_parsing_table())
        user_input = word + '$' # define initial input
        stack = self.start + '$'  # define initial stack
        action = '-'# define initial action
        print('Stack', 'Input', 'Action')
        print(stack, user_input, action)
        # if value in the table:
        try:
            # do while not $ $ ''
            while stack != user_input or stack != '$':
                # push from the stack in case the same value (may be only terminals)
                if stack[0] == user_input[0]:
                    stack = stack[1:]
                    user_input = user_input[1:]
                    action = '-'
                else:
                    # define the action in case different symbols in stack and input
                    index = 1
                    nonterminal = stack[0]
                    # get the whole first nonterminal symbol
                    while len(stack) > 1 and '0' <= stack[index] <= '9':
                        nonterminal += stack[index]
                        index += 1
                    # describe action and new stack
                    action = self.parsing_table[nonterminal][user_input[0]]
                    stack = stack.replace(nonterminal, action)
                print(stack, user_input, action)
            # if the form $ $ '' achieved, accept the string
            print('Accepted')
        # if value not in the table, not accepted string
        except KeyError:
            print('Not accepted')
