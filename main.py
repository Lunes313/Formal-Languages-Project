import LL1_PARSER as ll1
import SLR1_PARSER as slr1
grammars = []


def read_grammars():
    try:
        with open("grammars.txt", 'r') as file:
            lines = [line.strip() for line in file if line.strip()]

            grammars.clear()

            num_grammars = int(lines[0])
            line_index = 1

            for g in range(num_grammars):
                num_productions = int(lines[line_index])
                line_index += 1

                grammar = {}
                symbols = set()
                non_terminals = set()

                for i in range(num_productions):

                    line = lines[line_index]
                    line_index += 1

                    left, right = line.split('->')
                    left = left.strip()
                    non_terminals.add(left)

                    productions = right.strip().split()
                    if left not in grammar:
                        non_terminals.add(left)
                        grammar[left] = []

                    productions = [prod.replace("/eps", "ε") for prod in productions]
                    grammar[left].extend(productions)

                    for prod in productions:
                        for symbol in prod:
                            symbols.add(symbol)

                terminals = symbols - non_terminals

                grammars.append({
                    'grammar': grammar,
                    'terminals': terminals,
                    'non_terminals': non_terminals
                })

    except FileNotFoundError:
        print(f"Error: The file 'grammars.txt' was not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")

def format_grammar_for_display(grammar):
    formatted_lines = []

    for nt, productions in grammar.items():
        line = f"{nt} -> {' | '.join(productions)}"
        formatted_lines.append(line)

    return formatted_lines

def display_grammars():
    print("\nChoose a grammar:\n")

    for i, g in enumerate(grammars):
        formatted_lines = format_grammar_for_display(g['grammar'])
        print(f"{i + 1}.  {formatted_lines[0]}")

        for line in formatted_lines[1:]:
            print(f"    {line}")
        print()

def print_grammars():
    while True:
        display_grammars()
        try:
            choice = int(input("Enter a number (0 to exit): "))
            if choice == 0:
                break
            elif 1 <= choice <= len(grammars):
                is_grammar_ll1 = ll1.is_ll1(grammars[choice - 1])
                is_grammar_slr1 = slr1.is_slr1(grammars[choice - 1])

                if is_grammar_ll1 and is_grammar_slr1:
                    while True:
                        parser_choice = input(
                            "Select a parser (T: for LL(1), B: for SLR(1), Q: quit): ").strip().upper()

                        if parser_choice == 'Q':
                            break
                        elif parser_choice == 'T':
                            ll1.print_ll_table(grammars[choice - 1])
                            parse_strings(grammars[choice - 1], ll1.print_derivation)
                        elif parser_choice == 'B':
                            slr1.print_slr_table(grammars[choice - 1])
                            parse_strings(grammars[choice - 1], slr1.print_reduction)
                        else:
                            print("Invalid option. Please try again.")

                elif is_grammar_ll1:
                    print("Grammar is LL(1).")
                    ll1.print_ll_table(grammars[choice - 1])
                    parse_strings(grammars[choice - 1], ll1.print_derivation)

                elif is_grammar_slr1:

                    print("Grammar is SLR(1).")
                    slr1.print_slr_table(grammars[choice - 1])
                    parse_strings(grammars[choice - 1], slr1.print_reduction)
                else:

                    print("Grammar is neither LL(1) nor SLR(1).")

                break
            else:
                print("Invalid choice. Please enter a number between 1 and", len(grammars))
        except ValueError:
            print("Invalid input. Please enter a number.")

def parse_strings(grammar_data, parse_function):
    while True:
        try:

            print("\nEnter a string to parse (or press Enter to exit):")
            input_string = input().strip()

            if not input_string:
                break

            if input_string == "/eps":
                input_string = ""

            if parse_function(grammar_data, input_string):
                print("yes")
            else:
                print("no")

        except EOFError:
            break


def add_grammar():

    print("\n=== Add New Grammar ===")
    print("Enter the production rules for the new grammar.")
    print("Format: NT -> P1 P2 P3")
    print("Use '/eps' for epsilon.")
    print("Enter an empty line to finish.")

    production_rules = []

    while True:
        rule = input("Enter a production rule (or empty line to finish): ").strip()
        if not rule:
            break

        # Validate the rule format
        if "->" not in rule:
            print("Invalid format. Please use the format 'NT -> P1 P2 P3'")
            continue

        # Check if the left side is a single non-terminal
        left_side = rule.split("->")[0].strip()
        if len(left_side) != 1 or not left_side.isalpha() or not left_side.isupper():
            print("Invalid non-terminal. Must be a single uppercase letter.")
            continue

        production_rules.append(rule)

    if not production_rules:
        print("No rules entered. Grammar not added.")
        return

    # Update the grammars.txt file
    try:
        # First read the current file to get the number of grammars
        with open("grammars.txt", 'r') as file:
            lines = [line.strip() for line in file if line.strip()]

        # Update the number of grammars
        if lines:
            current_num_grammars = int(lines[0])
            lines[0] = str(current_num_grammars + 1)
        else:
            # If the file is empty, start with 1 grammar
            lines = ["1"]

        # Add the new grammar
        lines.append(str(len(production_rules)))  # Number of production rules
        lines.extend(production_rules)

        # Write back to the file
        with open("grammars.txt", 'w') as file:
            for line in lines:
                file.write(line + "\n")

        print(f"Grammar successfully added! ({len(production_rules)} rules)")

        # Reload the grammars from the file
        read_grammars()

    except Exception as e:
        print(f"An error occurred while updating the file: {e}")

def menu():
    while True:
        print("\n=== Grammar Menu ===")
        print("1. Choose grammars")
        print("2. Add grammar")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == "1":
            print_grammars()
        elif choice == "2":
            add_grammar()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    read_grammars()
    menu()