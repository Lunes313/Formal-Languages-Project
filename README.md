

# LL(1) and SLR(1) Parsers

This project implements LL(1) (Top-Down) and SLR(1) (Bottom-Up) parsers for context-free grammars, following the specifications from the book *"Compilers: Principles, Techniques, and Tools"* (2nd Edition) by Aho et al., sections 4.4 and 4.6.

## Group Members

* Laura Restrepo
* Johan Rico

## Development Environment

* Operating System: Windows 10
* Programming Language: Python 3.10+
* Libraries: `tabulate` (for formatting tables in the output)

## Usage Instructions

### Prerequisites

1. Python 3.8 or higher
2. `tabulate` library (install with `pip install tabulate`)

### Running the Program

```bash
python main.py
```

The program will read the grammar from standard input and determine whether it is LL(1) and/or SLR(1). It will then prompt for input strings to analyze.

### Input Format

The input must follow this format:

1. An integer `n` indicating the number of non-terminals in the grammar.
2. `n` lines with the productions of each non-terminal, in the format:

   ```
   <non-terminal> -> <derivation alternatives separated by spaces>
   ```

Where:

* Non-terminals are uppercase letters.
* Terminals are any symbol that is not an uppercase letter.
* The empty string (ε) is represented by the letter `e`.
* All strings must end with the `$` symbol.

### Input Examples

#### Example 1

```
3
S -> S+T T
T -> T*F F
F -> (S) i
```

#### Example 2

```
3
S -> AB
A -> aA d
B -> bBc e
```

## Project Structure

* `main.py`: Main program that reads the grammar and coordinates the analysis.
* `first_follow.py`: Implementation of the algorithms for computing FIRST and FOLLOW sets.
* `ll1_parser.py`: Implementation of the LL(1) parser (Top-Down).
* `slr1_parser.py`: Implementation of the SLR(1) parser (Bottom-Up).

## Implemented Features

* Computation of FIRST and FOLLOW sets for any context-free grammar.
* Construction of LL(1) parsing table and verification of LL(1) conditions.
* Construction of SLR(1) parsing table and verification of SLR(1) conditions.
* String analysis using both parsing methods.
* Conflict detection and reporting in parsing tables.