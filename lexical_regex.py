import re

keywords = [
    "auto", "break", "case", "char", "const", "continue", "default", "do",
    "double", "else", "enum", "extern", "float", "for", "goto", "if", "int",
    "long", "register", "return", "short", "signed", "sizeof", "static", "struct",
    "switch", "typedef", "union", "unsigned", "void", "volatile", "while"
]

operators = [
    "==", "&&", "||", "++", "--", "<=", "!", "%", "*", "+", "-", "/", "<", "!=",
    "=", ">", ">="
]

delimiters = [
    ";", ",", "(", ")", "{", "}", "[", "]"
]


def is_identifier(word):
    return bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", word))


def is_constant(word):
    return bool(re.match(r"^\d+(\.\d+)?$", word))


def is_operator(word):
    return word in operators


def is_delimiter(word):
    return word in delimiters


def lexical_analyzer(code):
    
    tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*|[0-9]+(?:\.[0-9]*)?|[^\w\s]", code)
    
    symbol_table = {}
    output = []
    line_number = 1
    symbol_counter = 0

    for token in tokens:
        
        if token in keywords:
            output.append(f"{line_number} | {token} | Keyword | {keywords.index(token)}")

        elif is_operator(token):
            output.append(f"{line_number} | {token} | Operator | {operators.index(token)}")

        elif is_delimiter(token):
            output.append(f"{line_number} | {token} | Delimiter | {delimiters.index(token)}")

        elif is_identifier(token):
            if token not in symbol_table:
                symbol_table[token] = symbol_counter
                symbol_counter += 1
            output.append(f"{line_number} | {token} | Identifier | {symbol_table[token]}")

        elif is_constant(token):
            output.append(f"{line_number} | {token} | Constant | {token}")

        else:
            output.append(f"{line_number} | {token} | Error | Invalid Token")
        
        if token == "\n":
            line_number += 1

    return output, symbol_table


with open('input_lexical.txt', 'r') as file:
    code = file.read()


output, symbol_table = lexical_analyzer(code)


for line in output:
    print(line)


print("\nSymbol Table:")
for symbol, index in symbol_table.items():
    print(f"{index} | {symbol}")
