def FIRST(grammar_data, string):
    grammar = grammar_data['grammar']
    terminals = grammar_data['terminals']
    non_terminals = grammar_data['non_terminals']

    first = set()
    first_symbol = string[0]
    if first_symbol in terminals:
        first.add(first_symbol)
    elif first_symbol in non_terminals:
        for production in grammar[first_symbol]:
            first = first | FIRST(grammar_data, production)

    return first

def FOLLOW(grammar_data, symbol):
    grammar = grammar_data['grammar']
    terminals = grammar_data['terminals']
    non_terminals = grammar_data['non_terminals']

    start_symbol = next(iter(grammar.keys()))
    follow = set()
    if symbol == start_symbol:
        follow.add('$')
    for nt in non_terminals:
        for production in grammar[nt]:
            if symbol in production:
                index = production.index(symbol)
                if index + 1 < len(production):
                    next_symbol = production[index + 1]
                    if next_symbol in terminals:
                        follow.add(next_symbol)
                    elif next_symbol in non_terminals:
                        follow = follow | FIRST(grammar_data, next_symbol)
                else:
                    if nt != symbol:
                        follow = follow | FOLLOW(grammar_data, nt)

    return follow