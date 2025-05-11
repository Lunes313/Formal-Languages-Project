import LL1_PARSER
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
                if LL1_PARSER.is_ll1(grammars[choice - 1]):
                    print("The grammar is LL(1).")
                    LL1_PARSER.print_parsing_table(grammars[choice - 1])
                    string = input("Enter a string to parse: ")
                    LL1_PARSER.print_derivation(grammars[choice - 1], string)
                else:
                    print("The grammar is not LL(1).")

                break
            else:
                print("Invalid choice. Please enter a number between 1 and", len(grammars))
        except ValueError:
            print("Invalid input. Please enter a number.")


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