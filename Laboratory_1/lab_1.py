import matplotlib.pyplot as plt
import networkx as nx
import random

from matplotlib.lines import Line2D


# the function to traverse the graph and return the nodes in order of their appearance
def dfs(visited, set_of_productions, node, order):
    if node not in visited:
        visited.add(node)
        order += node
        # for not the ending points
        for neighbour in set_of_productions[node]:
            if len(neighbour) > 1:
                dfs(visited, set_of_productions, neighbour[1], order)
    return order


# the function that tests if the input fit the grammar
def test_word(start_symbol, final_symbol, finiteAutomaton, input_word):
    state = start_symbol
    for symbol in input_word:
        if state in finiteAutomaton and symbol in finiteAutomaton[state]:
            state = finiteAutomaton[state][symbol]
        else:
            return False
    return state == final_symbol


# get the input from file
with open('Variant_13.txt', 'r') as file:
    lines = file.read().splitlines()

# initialize variable for graph plotting
G = nx.Graph()

# set the start symbol, non-terminal symbols, terminal symbols and divide productions in tuples pf left nd right parts
start_symbol = 'q0'
final_symbol = 'qF'
nonterminal_symbols = set(lines[0].split(', '))
terminal_symbols = set(lines[1].split(', '))
set_of_productions = []
for line in lines[2:]:
    set_of_productions.append(tuple(line.split(' -> ')))


# determine all right parts of production of the same non-terminal symbol
set_of_productions = {vn[0]: [prod_right[1] for prod_right in set_of_productions if prod_right[0] == vn[0]] for
                      vn in set_of_productions}

visited = set()  # set of visited nodes
order = []  # the order of appearance of nodes in traversing
order = dfs(visited, set_of_productions, 'S', order)

# assign a Finite Automaton analog to each non-terminal symbols
fa_symbols = dict()
for index in range(len(order)):
    fa_symbols[order[index]] = ('q' + str(index))

# set a random color for each edge in graph which holds under a certain terminal symbol
color = {}
for vt in terminal_symbols:
    color[vt] = ("#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)]))

finiteAutomaton = dict()  # Finite Automaton representation
edge_list = []  # Set of edges for graph input
label_list = []  # Set of labels for graph input

set_of_productions_fa = {}  # set of productions with Finite Automaton symbols

# build the Finite Automaton
for left_part in set_of_productions:
    # rise error if there are the non-terminal symbol does not exist
    print(set_of_productions)
    if left_part not in nonterminal_symbols:
        raise Exception("Incorrect non-terminal symbols in production")
    # change non-terminal symbols into Finite Automaton symbol
    set_of_productions_fa[fa_symbols[left_part]] = set_of_productions[left_part]
    left_part_fa = fa_symbols[left_part]
    # initiate the dictionary of productions for each unique non-terminal symbol
    if left_part not in finiteAutomaton:
        finiteAutomaton[left_part_fa] = {}
    for right_part in set_of_productions_fa[left_part_fa]:
        # rise error if there are the terminal symbol does not exist
        if len(right_part) == 2 and right_part[0] not in terminal_symbols:
            raise Exception("Incorrect terminal symbols in production")
        elif len(right_part) == 1 and right_part[0] not in terminal_symbols:
            raise Exception("Incorrect terminal symbols in production")
        # set the final node
        if len(right_part) != 2:
            finiteAutomaton[left_part_fa][right_part[0]] = 'qF'
        # define the tuple of terminal - non-terminal symbols
        else:
            # change the non-terminal symbols in destination to Finite Automaton symbols
            right_part = right_part.replace(right_part[1], fa_symbols[right_part[1]])
            finiteAutomaton[left_part_fa][right_part[0]] = right_part[1:]
            # add edges to the graph
        G.add_edge(left_part_fa, finiteAutomaton[left_part_fa][right_part[0]], color=color[right_part[0]])
        # add edges to list of edges
        edge_list.append((left_part_fa, finiteAutomaton[left_part_fa][right_part[0]]))
        # add labels to list of labels
        label_list.append(((left_part_fa, finiteAutomaton[left_part_fa][right_part[0]]), right_part[0]))

print('The Finite Automation representation is: \n', finiteAutomaton)
print('The Finite Automation edges: \n', label_list)

# build the graph representation
pos = nx.spring_layout(G, seed=5)  # position

# define vertices
nx.draw_networkx_nodes(G, pos, node_size=450)

# define edges
colors = [G[u][v]['color'] for u, v in edge_list]  # assign color to each edge by letter
symbol_label = [label for label in color]   # order of terminal-symbols
color_label = [color[label] for label in color]  # order of colors which correspond to each terminal symbol
nx.draw_networkx_edges(G, pos, edgelist=edge_list, edge_color=colors, width=1, arrows=True, arrowsize=10,
                       connectionstyle='arc3, rad = 0.1')

# define labels
nx.draw_networkx_edge_labels(G, pos, edge_labels=dict(label_list), font_size=8, font_family='sans-serif',
                             label_pos=0.25)
nx.draw_networkx_labels(G, pos, font_size=14, font_family="sans-serif")

# plot and show the graph
ax = plt.gca()
ax.margins(0.08)
handles = [Line2D([], [], color=color, label=label)
           for color, label in zip(color_label, symbol_label)]
ax.legend(handles=handles)
plt.axis('off')
plt.tight_layout()
plt.show()


# user input for testing word
while True:
    print('Enter a word: ')
    word = input()
    if word == '':
        break
    else:
        if test_word(start_symbol, final_symbol, finiteAutomaton, word):
            print('It fits the grammar')
        else:
            print('It does not fit the grammar')