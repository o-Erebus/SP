
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
    return word.isidentifier()


def is_constant(word):
    try:
        float(word)
        return True
    except ValueError:
        return False


def is_operator(word):
    return word in operators


def is_delimiter(word):
    return word in delimiters

def lexical_analyzer(code):
    symbol_table = {}
    output = []
    line_number = 1
    symbol_counter = 0
    i = 0
    n = len(code)
    word = ""

    while i < n:
        char = code[i]
        
     
        if char in " \t\n":
            if char == "\n":
                line_number += 1
            i += 1
            continue
        
        
        if char.isalpha() or char == "_":
            word = char
            i += 1
            while i < n and (code[i].isalnum() or code[i] == "_"):
                word += code[i]
                i += 1
            
           
            if word in keywords:
                output.append(f"{line_number} | {word} | Keyword | {keywords.index(word)}")
            else:
                if word not in symbol_table:
                    symbol_table[word] = symbol_counter
                    symbol_counter += 1
                output.append(f"{line_number} | {word} | Identifier | {symbol_table[word]}")
        
        
        elif char.isdigit() or (char == "." and i+1 < n and code[i+1].isdigit()):
            word = char
            i += 1
            while i < n and (code[i].isdigit() or code[i] == "."):
                word += code[i]
                i += 1
            if is_constant(word):
                output.append(f"{line_number} | {word} | Constant | {word}")
            else:
                output.append(f"{line_number} | {word} | Error | Invalid Token")
        
        
        elif i+1 < n and code[i:i+2] in operators:
            word = code[i:i+2]
            i += 2
            if is_operator(word):
                output.append(f"{line_number} | {word} | Operator | {operators.index(word)}")
            else:
                output.append(f"{line_number} | {word} | Error | Invalid Token")
        
        
        elif char in operators or char in delimiters:
            word = char
            i += 1
            if is_operator(word):
                output.append(f"{line_number} | {word} | Operator | {operators.index(word)}")
            elif is_delimiter(word):
                output.append(f"{line_number} | {word} | Delimiter | {delimiters.index(word)}")
            else:
                output.append(f"{line_number} | {word} | Error | Invalid Token")
        
        else:
            output.append(f"{line_number} | {char} | Error | Invalid Token")
            i += 1

    return output, symbol_table


with open('input_lexical.txt', 'r') as file:
    code = file.read()

output, symbol_table = lexical_analyzer(code)


for line in output:
    print(line)


print("\nSymbol Table:")
for symbol, index in symbol_table.items():
    print(f"{index} | {symbol}")
