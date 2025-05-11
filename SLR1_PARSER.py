from FIRST_FOLLOW import FOLLOW
from tabulate import tabulate

class Item:
    def __init__(self, left, right, dot_pos):
        self.left = left
        self.right = right
        self.dot_pos = dot_pos

    def __eq__(self, other):
        return (self.left == other.left and
                self.right == other.right and
                self.dot_pos == other.dot_pos)

    def __hash__(self):
        return hash((self.left, self.right, self.dot_pos))

    def __str__(self):
        right_with_dot = list(self.right)
        if self.dot_pos <= len(self.right):
            right_with_dot.insert(self.dot_pos, '•')
        return f"{self.left} -> {''.join(right_with_dot)}"

    def next_symbol(self):
        if self.dot_pos < len(self.right):
            return self.right[self.dot_pos]
        return None

    def advance(self):
        return Item(self.left, self.right, self.dot_pos + 1)

def compute_closure(grammar_data, items):

    grammar = grammar_data['grammar']
    closure = set(items)

    while True:
        new_items = set()
        for item in closure:
            next_sym = item.next_symbol()

            if next_sym in grammar_data['non_terminals']:
                for production in grammar[next_sym]:
                    if production == 'ε':
                        new_item = Item(next_sym, '', 0)
                    else:
                        new_item = Item(next_sym, production, 0)

                    if new_item not in closure:
                        new_items.add(new_item)

        if not new_items:
            break

        closure.update(new_items)

    return closure

def goto(grammar_data, items, symbol):
    next_items = set()
    for item in items:
        if item.next_symbol() == symbol:
            next_items.add(item.advance())

    if next_items:
        return compute_closure(grammar_data, next_items)

    return set()

def canonical_collection(grammar_data):
    grammar = grammar_data['grammar']
    symbols = grammar_data['terminals'].union(grammar_data['non_terminals']) - {'ε'}

    start_symbol = list(grammar.keys())[0]
    initial_item = Item('S\'', start_symbol, 0)

    initial_state = compute_closure(grammar_data, {initial_item})

    states = [initial_state]
    transitions = {}

    i = 0
    while i < len(states):
        current_state = states[i]

        for symbol in symbols:
            next_state = goto(grammar_data, current_state, symbol)

            if next_state and next_state not in states:
                states.append(next_state)

            if next_state:
                transitions[(i, symbol)] = states.index(next_state)

        i += 1

    return states, transitions

def create_slr_table(grammar_data):

    grammar = grammar_data['grammar']
    terminals = grammar_data['terminals'].copy() - {'ε'}
    terminals.add('$')
    non_terminals = grammar_data['non_terminals']

    states, transitions = canonical_collection(grammar_data)

    action = {}
    goto_table = {}

    start_symbol = list(grammar.keys())[0]
    augmented_production = start_symbol

    grammar_data['conflicts'] = []

    for i, state in enumerate(states):
        for item in state:
            next_sym = item.next_symbol()

            if next_sym is None:
                if item.left == 'S\'' and item.right == start_symbol:
                    action[(i, '$')] = ('accept', '')
                else:
                    follow_set = FOLLOW(grammar_data, item.left)

                    for terminal in follow_set:
                        if (i, terminal) in action:
                            grammar_data['conflicts'].append(
                                f"Conflicto en estado {i}, terminal '{terminal}': "
                                f"{action[(i, terminal)]} vs ('reduce', '{item.left} -> {item.right}')"
                            )
                        else:
                            action[(i, terminal)] = ('reduce', (item.left, item.right))

            elif next_sym in terminals:
                if (i, next_sym) in transitions:
                    next_state = transitions[(i, next_sym)]

                    if (i, next_sym) in action:
                        grammar_data['conflicts'].append(
                            f"Conflicto en estado {i}, terminal '{next_sym}': "
                            f"{action[(i, next_sym)]} vs ('shift', {next_state})"
                        )
                    else:
                        action[(i, next_sym)] = ('shift', next_state)

            elif next_sym in non_terminals:
                if (i, next_sym) in transitions:
                    goto_table[(i, next_sym)] = transitions[(i, next_sym)]

    return action, goto_table, states

def print_slr_table(grammar_data):
    terminals = sorted(grammar_data['terminals'].copy() - {'ε'}) + ['$']
    non_terminals = sorted(grammar_data['non_terminals'])

    action, goto_table, states = create_slr_table(grammar_data)

    headers = ["Estado"] + terminals + non_terminals
    table = []

    for i in range(len(states)):
        row = [i]

        for terminal in terminals:
            if (i, terminal) in action:
                act, value = action[(i, terminal)]
                if act == 'shift':
                    cell = f"s{value}"
                elif act == 'reduce':
                    left, right = value
                    right_str = right if right else 'ε'
                    cell = f"r({left}->{right_str})"
                elif act == 'accept':
                    cell = "acc"
                else:
                    cell = ""
            else:
                cell = ""
            row.append(cell)

        for nt in non_terminals:
            if (i, nt) in goto_table:
                row.append(goto_table[(i, nt)])
            else:
                row.append("")

        table.append(row)

    print("\nTabla de análisis SLR(1):")
    print(tabulate(table, headers=headers, tablefmt="grid"))

    print("\nEstados:")
    for i, state in enumerate(states):
        print(f"Estado {i}:")
        for item in state:
            print(f"  {item}")

    return action, goto_table

def parse_string(grammar_data, input_string, verbose=False):
    action, goto_table, _ = create_slr_table(grammar_data)

    stack = [0]
    symbols = []
    input_string = input_string + '$'
    input_pos = 0

    steps = []

    while True:
        state = stack[-1]
        current_input = input_string[input_pos]

        if verbose:
            stack_str = ' '.join(map(str, stack))
            symbols_str = ''.join(symbols)
            input_str = input_string[input_pos:]

        if (state, current_input) not in action:
            if verbose:
                steps.append([stack_str, symbols_str, input_str, "Error: No hay acción definida"])
                print(tabulate(steps, headers=["Estados", "Símbolos", "Entrada", "Acción"], tablefmt="grid"))
            return False

        act, value = action[(state, current_input)]

        if act == 'shift':
            stack.append(value)
            symbols.append(current_input)
            input_pos += 1

            if verbose:
                steps.append([stack_str, symbols_str, input_str, f"Desplazar {current_input}, ir a estado {value}"])

        elif act == 'reduce':
            left, right = value
            right_len = len(right) if right != 'ε' else 0

            for _ in range(right_len):
                stack.pop()
                symbols.pop()

            top_state = stack[-1]
            if (top_state, left) not in goto_table:
                if verbose:
                    steps.append([stack_str, symbols_str, input_str, f"Error: No hay GOTO para estado {top_state} y no terminal {left}"])
                    print(tabulate(steps, headers=["Estados", "Símbolos", "Entrada", "Acción"], tablefmt="grid"))
                return False

            goto_state = goto_table[(top_state, left)]
            stack.append(goto_state)
            symbols.append(left)

            if verbose:
                right_str = right if right else 'ε'
                steps.append([stack_str, symbols_str, input_str, f"Reducir por {left} -> {right_str}, ir a estado {goto_state}"])

        elif act == 'accept':
            if verbose:
                steps.append([stack_str, symbols_str, input_str, "Aceptar"])
                print(tabulate(steps, headers=["Estados", "Símbolos", "Entrada", "Acción"], tablefmt="grid"))
            return True

    return False

def is_slr1(grammar_data):
    create_slr_table(grammar_data)

    if 'conflicts' in grammar_data and grammar_data['conflicts']:
        return False

    return True