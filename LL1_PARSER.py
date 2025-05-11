from FIRST_FOLLOW import FIRST, FOLLOW
from tabulate import tabulate


def create_parsing_table(grammar_data):
    grammar = grammar_data['grammar']
    terminals = grammar_data['terminals'].copy()
    terminals.discard("ε")
    terminals.add("$")
    non_terminals = grammar_data['non_terminals']

    parsing_table = {nt: {t: None for t in terminals} for nt in non_terminals}
    for nt in non_terminals:
        for production in grammar[nt]:
            first_set = FIRST(grammar_data, production)
            for terminal in first_set:
                if terminal != 'ε':
                    parsing_table[nt][terminal] = production
                else:
                    follow_set = FOLLOW(grammar_data, nt)
                    for follow in follow_set:
                        parsing_table[nt][follow] = production

    return parsing_table

def print_ll_table(grammar_data):
    terminals = grammar_data['terminals'].copy()
    terminals.discard("ε")
    terminals.add("$")
    non_terminals = grammar_data['non_terminals']

    parsing_table = create_parsing_table(grammar_data)
    headers = [""] + sorted(terminals)
    table = []

    for r in non_terminals:
        row = [r] + [parsing_table[r][c] for c in sorted(terminals)]
        table.append(row)

    print(tabulate(table, headers=headers, tablefmt="grid"))

    return parsing_table

def print_derivation(grammar_data, string):
    grammar = grammar_data['grammar']
    terminals = grammar_data['terminals'].copy()
    terminals.discard("ε")
    terminals.add("$")
    non_terminals = grammar_data['non_terminals']
    start_symbol = next(iter(grammar.keys()))

    parsing_table = create_parsing_table(grammar_data)
    input_string = string + "$"
    stack = ["$", start_symbol]

    derivation_table = []

    while stack and input_string:
        stack_top = stack[-1]
        current_input = input_string[0]

        stack_str = "".join(stack)

        if stack_top == "$" and current_input == "$":
            derivation_table.append([stack_str, input_string, "Accept"])
            break

        elif stack_top in terminals:
            if stack_top == current_input:
                action = f"Match '{stack_top}'"
                stack.pop()

                derivation_table.append([stack_str, input_string, action])
                input_string = input_string[1:]
            else:
                derivation_table.append([stack_str, input_string, "Reject"])
                break

        elif stack_top in non_terminals:
            if parsing_table[stack_top].get(current_input):
                production = parsing_table[stack_top][current_input]
                action = f"Derive {stack_top} → {production}"

                stack.pop()
                if production != "ε":
                    for symbol in reversed(production):
                        stack.append(symbol)

                derivation_table.append([stack_str, input_string, action])
            else:
                derivation_table.append([stack_str, input_string, "Reject"])
                break

        else:
            derivation_table.append([stack_str, input_string, "Reject"])
            break

    headers = ["Stack", "Input", "Action"]
    print(tabulate(derivation_table, headers=headers, tablefmt="grid"))


def parse_string(grammar_data, input_string, verbose=False):
    grammar = grammar_data['grammar']
    parsing_table = create_parsing_table(grammar_data)

    stack = ['$', list(grammar.keys())[0]]
    input_string = input_string + '$'
    input_pos = 0

    derivation_steps = []

    while stack[-1] != '$' or input_string[input_pos] != '$':
        stack_top = stack[-1]
        current_input = input_string[input_pos]

        stack_str = ''.join(stack[::-1])
        input_str = input_string[input_pos:]

        if stack_top in grammar_data['terminals']:
            if stack_top == current_input:
                action = f"Emparejar '{stack_top}'"
                stack.pop()
                input_pos += 1
            else:
                if verbose:
                    derivation_steps.append(
                        [stack_str, input_str, f"Error: Se esperaba '{stack_top}', se encontró '{current_input}'"])
                    print(tabulate(derivation_steps, headers=["Pila", "Entrada", "Acción"], tablefmt="grid"))
                return False
        else:
            if current_input in parsing_table[stack_top] and parsing_table[stack_top][current_input]:
                production = parsing_table[stack_top][current_input]
                action = f"{stack_top} -> {production}"

                stack.pop()
                if production != 'ε':
                    for symbol in reversed(production):
                        stack.append(symbol)
            else:
                if verbose:
                    derivation_steps.append(
                        [stack_str, input_str, f"Error: No hay producción para {stack_top} con '{current_input}'"])
                    print(tabulate(derivation_steps, headers=["Pila", "Entrada", "Acción"], tablefmt="grid"))
                return False

        if verbose:
            derivation_steps.append([stack_str, input_str, action])

    if stack[-1] == '$' and input_string[input_pos] == '$':
        if verbose:
            derivation_steps.append(['$', '$', "Aceptar"])
            print(tabulate(derivation_steps, headers=["Pila", "Entrada", "Acción"], tablefmt="grid"))
        return True

    return False

def is_ll1(grammar_data):
    for nt, productions in grammar_data['grammar'].items():
        for p1 in range(len(productions)-1):
            production1 = productions[p1]
            if nt == production1[0]:
                return False
            for p2 in range(p1 + 1, len(productions)):
                production2 = productions[p2]
                if not FIRST(grammar_data, production1).isdisjoint(FIRST(grammar_data, production2)):
                    return False
    return True





