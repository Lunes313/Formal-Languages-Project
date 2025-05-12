from dateutil.rrule import parser

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
                terminals = set()
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
                            parse_strings(grammars[choice - 1], ll1.parse_string, parser_choice)
                        elif parser_choice == 'B':
                            slr1.print_slr_table(grammars[choice - 1])
                            parse_strings(grammars[choice - 1], slr1.parse_string, parser_choice)
                        else:
                            print("Invalid option. Please try again.")

                elif is_grammar_ll1:
                    print("Grammar is LL(1).")
                    ll1.print_ll_table(grammars[choice - 1])
                    parse_strings(grammars[choice - 1], ll1.parse_string)

                elif is_grammar_slr1:

                    print("Grammar is SLR(1).")
                    slr1.print_slr_table(grammars[choice - 1])
                    parse_strings(grammars[choice - 1], slr1.parse_string)
                else:

                    print("Grammar is neither LL(1) nor SLR(1).")

                break
            else:
                print("Invalid choice. Please enter a number between 1 and", len(grammars))
        except ValueError:
            print("Invalid input. Please enter a number.")

def parse_strings(grammar_data, parse_function, parser_choice):
    while True:
        try:

            print("\nEnter a string to parse (or press Enter to exit):")
            input_string = input().strip()

            if not input_string:
                break

            if parser_choice == 'T':
                ll1.print_derivation(grammar_data, input_string)

            if parse_function(grammar_data, input_string):
                print("yes")
            else:
                print("no")

        except EOFError:
            break


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
            pass
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    read_grammars()
    menu()