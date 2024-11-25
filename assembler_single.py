MOT = {
    'MOV': {'opcode': '10', 'length': 1, 'operands': 2},
    'ADD': {'opcode': '11', 'length': 1, 'operands': 2},
    'SUB': {'opcode': '12', 'length': 1, 'operands': 2},
    'JMP': {'opcode': '13', 'length': 1, 'operands': 1},
    'RET': {'opcode': '14', 'length': 1, 'operands': 0}
}

assembly_code = open("input_assembler.txt", "r").read()

symbol_table = {}
machine_code = []
incomplete_instructions = []
errors = []
lc = 0

lines = assembly_code.strip().split('\n')
for line_no, line in enumerate(lines):
    line = line.strip()
    if not line:
        continue
    line = line.replace(","," ")
    parts = line.replace(',', ' ').split()
    
    if parts[0] == 'START':
        lc = int(parts[1])
        continue
    
    if ':' in line:
        label, instruction = line.split(':')
        label = label.strip()
        if label in symbol_table:
            errors.append(f"Error on line {line_no + 1}: Duplicate label '{label}'")
        else:
            symbol_table[label] = lc
        parts = instruction.strip().split()
    
    if parts[0] == 'DS':
        machine_code.append((lc,f"-"))
        lc += int(parts[1])
    
    elif parts[0] == 'DC':
        machine_code.append((lc, f"{parts[1]}"))
        lc += 1
    
    elif parts[0] in MOT:
        opcode = MOT[parts[0]]['opcode']
        operands = parts[1:]
        instruction = f"{opcode} "
        for operand in operands:
            if operand in ['AX', 'BX', 'CX', 'DX']:
                instruction += f"{['AX', 'BX', 'CX', 'DX'].index(operand)} "
            elif operand in symbol_table:
                instruction += f"[{symbol_table[operand]}] "
            elif operand.isdigit():
                instruction += f"{operand} "
            else:
                incomplete_instructions.append((lc, operand))
                instruction += "??? "
        machine_code.append((lc, instruction.strip()))
        lc += 1
    
    elif parts[0] == 'END':
        break
    
    else:
        errors.append(f"Error on line {line_no + 1}: Unknown mnemonic '{parts[0]}'")

for lc, symbol in incomplete_instructions:
    if symbol in symbol_table:
        for i, (mc_lc, code) in enumerate(machine_code):
            if mc_lc == lc:
                machine_code[i] = (mc_lc, code.replace("???", f"[{str(symbol_table[symbol])}]"))
                
    else:
        errors.append(f"Error: Undefined symbol '{symbol}' at LC {lc}")

print("\nSymbol Table:")
print("Index | Symbol | Address")
print("-" * 30)
for i, (symbol, address) in enumerate(symbol_table.items()):
    print(f"{i:5} | {symbol:6} | {address}")

print("\nTable of Incomplete Instructions")
print("LC   | Symbol")
print("-" * 30)
for lc,symbol in incomplete_instructions:
    print(f"{lc:4} | {symbol}")

print("\nMachine Code:")
print("LC   | Machine Code")
print("-" * 30)
for lc, code in machine_code:
    print(f"{lc:4} | {code}")

if errors:
    print("\nErrors:")
    print("-" * 30)
    for error in errors:
        print(error)
