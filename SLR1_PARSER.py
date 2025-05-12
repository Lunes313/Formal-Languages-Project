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

    changed = True
    while changed:
        changed = False
        new_items = set()

        for item in closure:
            next_sym = item.next_symbol()

            if next_sym in grammar_data['non_terminals']:
                for production in grammar[next_sym]:
                    if production == 'ε':
                        # For epsilon productions, create an item with empty string
                        new_item = Item(next_sym, '', 0)
                    else:
                        new_item = Item(next_sym, production, 0)

                    if new_item not in closure:
                        new_items.add(new_item)
                        changed = True

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
    initial_item = Item("S'", start_symbol, 0)

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

    # To record conflicts
    grammar_data['conflicts'] = []

    for i, state in enumerate(states):
        for item in state:
            next_sym = item.next_symbol()

            # Case 1: Dot is at the end of production
            if next_sym is None:
                # Special case for accept state
                if item.left == "S'" and item.right == start_symbol:
                    action[(i, '$')] = ('accept', '')
                else:
                    # For reductions, we need the FOLLOW set
                    follow_set = FOLLOW(grammar_data, item.left)

                    for terminal in follow_set:
                        if (i, terminal) in action:
                            # Record conflict
                            current_action = action[(i, terminal)]
                            grammar_data['conflicts'].append(
                                f"Conflict in state {i}, terminal '{terminal}': "
                                f"{current_action} vs ('Reduce', '{item.left} → {item.right}')"
                            )
                        else:
                            action[(i, terminal)] = ('reduce', (item.left, item.right))

            # Case 2: Next symbol is a terminal
            elif next_sym in terminals:
                if (i, next_sym) in transitions:
                    next_state = transitions[(i, next_sym)]

                    if (i, next_sym) in action and action[(i, next_sym)][1] != next_state:
                        # Record conflict
                        current_action = action[(i, next_sym)]
                        grammar_data['conflicts'].append(
                            f"Conflict in state {i}, terminal '{next_sym}': "
                            f"{current_action} vs ('shift', {next_state})"
                        )
                    else:
                        action[(i, next_sym)] = ('shift', next_state)

            # Case 3: Next symbol is a non-terminal
            elif next_sym in non_terminals:
                if (i, next_sym) in transitions:
                    goto_table[(i, next_sym)] = transitions[(i, next_sym)]

    return action, goto_table, states


def print_slr_table(grammar_data):
    terminals = sorted(grammar_data['terminals'].copy() - {'ε'}) + ['$']
    non_terminals = sorted(grammar_data['non_terminals'])

    action, goto_table, states = create_slr_table(grammar_data)

    headers = ["State"] + terminals + non_terminals
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
                    cell = f"r({left}→{right_str})"
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

    print("\nSLR(1) Analysis Table:")
    print(tabulate(table, headers=headers, tablefmt="grid"))

    print("\nStates:")
    for i, state in enumerate(states):
        print(f"State {i}:")
        for item in state:
            print(f"  {item}")

    # Check and show conflicts
    if 'conflicts' in grammar_data and grammar_data['conflicts']:
        print("\nDetected conflicts:")
        for conflict in grammar_data['conflicts']:
            print(conflict)

    return action, goto_table

def print_reduction(grammar_data, input_string):

    action, goto_table, _ = create_slr_table(grammar_data)

    stack = [0]  # State stack
    symbols = ['$']  # Symbol stack
    input_string = input_string + '$'
    input_pos = 0
    reductions = []  # To store reductions

    steps = []

    while True:
        state = stack[-1]
        current_input = input_string[input_pos]

        stack_str = ' '.join(map(str, stack))
        symbols_str = ''.join(symbols)
        input_str = input_string[input_pos:]

        # Check if there's an action defined for current state and input symbol
        if (state, current_input) not in action:
            steps.append([stack_str, symbols_str, input_str, "Reject"])
            print(tabulate(steps, headers=["States", "Symbols", "Input", "Action"], tablefmt="grid"))
            return False

        act, value = action[(state, current_input)]

        if act == 'shift':
            # Shift: Add state and symbol to stacks
            next_state = value
            stack.append(next_state)
            symbols.append(current_input)
            input_pos += 1

            steps.append(
                [stack_str, symbols_str, input_str, f"Shift {next_state}"])

        elif act == 'reduce':
            # Reduce: Apply a production rule
            left, right = value
            right_len = len(right) if right != 'ε' else 0

            # Pop symbols and states of reduced productions
            for _ in range(right_len):
                stack.pop()
                symbols.pop()

            # Get state from top of stack
            top_state = stack[-1]

            # Check if there's a defined transition
            if (top_state, left) not in goto_table:
                steps.append([stack_str, symbols_str, input_str, "Reject"])
                print(tabulate(steps, headers=["States", "Symbols", "Input", "Action"], tablefmt="grid"))
                return False

            # Perform GOTO transition
            goto_state = goto_table[(top_state, left)]
            stack.append(goto_state)
            symbols.append(left)

            right_str = right if right else 'ε'
            action_msg = f"Reduce {left} -> {right_str}"
            reductions.append(f"{left} -> {right_str}")

            steps.append([stack_str, symbols_str, input_str, action_msg, ' '.join(reductions)])

        elif act == 'accept':
            # Accept: String is valid
            steps.append([stack_str, symbols_str, input_str, "Accept"])
            print(tabulate(steps, headers=["States", "Symbols", "Input", "Action"], tablefmt="grid"))
            return True

def is_slr1(grammar_data):

    # Create the SLR table and check for conflicts
    create_slr_table(grammar_data.copy())

    if 'conflicts' in grammar_data and grammar_data['conflicts']:
        print("\nDetected conflicts:")
        return False

    return True