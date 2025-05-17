def compute_first_sets(grammar_data):

    grammar = grammar_data['grammar']
    terminals = grammar_data['terminals']
    non_terminals = grammar_data['non_terminals']

    first_sets = {}

    for terminal in terminals:
        first_sets[terminal] = {terminal}

    for nt in non_terminals:
        first_sets[nt] = set()

    if 'ε' in terminals:
        first_sets['ε'] = {'ε'}

    changed = True
    while changed:
        changed = False

        for nt in non_terminals:
            for production in grammar[nt]:
                if production == 'ε':
                    if 'ε' not in first_sets[nt]:
                        first_sets[nt].add('ε')
                        changed = True
                    continue

                all_can_derive_epsilon = True
                for symbol in production:
                    if symbol not in first_sets:
                        if symbol in terminals:
                            first_sets[symbol] = {symbol}
                        else:
                            first_sets[symbol] = set()

                    if symbol in first_sets:
                        new_symbols = first_sets[symbol] - {'ε'}
                        old_size = len(first_sets[nt])
                        first_sets[nt].update(new_symbols)
                        if len(first_sets[nt]) > old_size:
                            changed = True

                        if 'ε' not in first_sets[symbol]:
                            all_can_derive_epsilon = False
                            break
                    else:
                        all_can_derive_epsilon = False
                        break

                if all_can_derive_epsilon and 'ε' not in first_sets[nt]:
                    first_sets[nt].add('ε')
                    changed = True

    return first_sets


def FIRST(grammar_data, string, first_sets=None):

    if first_sets is None:
        first_sets = compute_first_sets(grammar_data)

    if not string:
        return {'ε'}

    if len(string) == 1:
        return first_sets.get(string, {string})

    result = set()
    all_can_derive_epsilon = True

    for symbol in string:
        symbol_first = first_sets.get(symbol, {symbol})

        result.update(symbol_first - {'ε'})

        if 'ε' not in symbol_first:
            all_can_derive_epsilon = False
            break

    if all_can_derive_epsilon:
        result.add('ε')

    return result


def compute_follow_sets(grammar_data, first_sets=None):

    grammar = grammar_data['grammar']
    non_terminals = grammar_data['non_terminals']

    if first_sets is None:
        first_sets = compute_first_sets(grammar_data)

    follow_sets = {nt: set() for nt in non_terminals}

    start_symbol = list(grammar.keys())[0]
    follow_sets[start_symbol].add('$')

    changed = True
    while changed:
        changed = False

        for nt in non_terminals:
            for production in grammar[nt]:
                if production == 'ε':
                    continue

                for i, symbol in enumerate(production):

                    if symbol not in non_terminals:
                        continue

                    if i == len(production) - 1:
                        old_size = len(follow_sets[symbol])
                        follow_sets[symbol].update(follow_sets[nt])
                        if len(follow_sets[symbol]) > old_size:
                            changed = True
                    else:
                        rest = production[i + 1:]
                        first_of_rest = FIRST(grammar_data, rest, first_sets)

                        old_size = len(follow_sets[symbol])
                        follow_sets[symbol].update(first_of_rest - {'ε'})
                        if len(follow_sets[symbol]) > old_size:
                            changed = True

                        if 'ε' in first_of_rest:
                            old_size = len(follow_sets[symbol])
                            follow_sets[symbol].update(follow_sets[nt])
                            if len(follow_sets[symbol]) > old_size:
                                changed = True

    return follow_sets


def FOLLOW(grammar_data, symbol, follow_sets=None, first_sets=None):

    if symbol not in grammar_data['non_terminals']:
        return set()

    if follow_sets is None:
        if first_sets is None:
            first_sets = compute_first_sets(grammar_data)
        follow_sets = compute_follow_sets(grammar_data, first_sets)

    return follow_sets.get(symbol, set())