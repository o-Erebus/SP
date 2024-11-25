import re

MOT = {
    'MOV': {'opcode': '10', 'length': 1, 'operands': 2},
    'ADD': {'opcode': '11', 'length': 1, 'operands': 2},
    'SUB': {'opcode': '12', 'length': 1, 'operands': 2},
    'JMP': {'opcode': '13', 'length': 1, 'operands': 1},
    'RET': {'opcode': '14', 'length': 1, 'operands': 0}
}

assembly_code = open("input_assembler.txt", "r").read()
symbol_table = []
intermediate_code = []
errors = []
lc = 0

lines = assembly_code.strip().split('\n')
for line in lines:
    line = line.strip()
    if not line: continue
    
    parts = line.replace(',', ' ').split()
    
    if parts[0] == 'START':
        lc = int(parts[1])
        continue
        
    if ':' in line:
        label = line.split(':')[0]
        if label in [x[0] for x in symbol_table]:
            print(label)
            for i, (sym, _) in enumerate(symbol_table):
                if sym == label:
                    symbol_table[i] = (label, lc)
        else:
            symbol_table.append((label, lc))
        line = line.replace(",", "")
        parts = line.split(':')[1].strip().split()

    if parts[0] == 'DS':
        intermediate_code.append((lc, f"(AD,1) (C,{parts[1]})"))
        lc += int(parts[1])
    elif parts[0] == 'DC':
        intermediate_code.append((lc, f"(AD,2) (C,{parts[1]})"))
        lc += 1
    elif parts[0] != 'END':
        if parts[0] not in MOT:
            errors.append(f"Error at LC {lc}: Unknown mnemonic {parts[0]}")
        else:
            parts[0] = f"(IS,{MOT[parts[0]]['opcode']})"
        for part in parts[1:]:
            if part not in [x[0] for x in symbol_table] and not part.isdigit() and part not in ['AX', 'BX', "CX", "DX"]:
                symbol_table.append((part, ""))
        for i in range(len(parts)):
            print(parts[i])
            if parts[i].isdigit():
                parts[i] = f"(C,{parts[i]})"
        instr = ' '.join(parts)
        
        for i, reg in enumerate(['AX', 'BX', "CX", "DX"]):
            instr = instr.replace(reg, f"(R,{i})")

        for i, (sym, _) in enumerate(symbol_table):
            instr = instr.replace(sym, f"(S,{i})")
        intermediate_code.append((lc, instr))
        lc += 1
        
print("\nSymbol Table:")
print("Index | Symbol | Address")
print("-" * 30)
for i, (sym, addr) in enumerate(symbol_table):
    print(f"{i:5} | {sym:6} | {addr}")

print("\nIntermediate Code:")
print("LC   | Instruction")
print("-" * 30)
for lc, instr in intermediate_code:
    print(f"{lc:4} | {instr}")

if errors:
    print("\nErrors Found:")
    print("-" * 30)
    for error in errors:
        print(error)

machine_code = []
for inst in intermediate_code: 
    parts = inst[1].split()
    p1 = f"{inst[0]} |"
    for i, part in enumerate(parts):
        part = part.replace("(", "")
        part = part.replace(")", "")
        if "IS," in part:
            p1 += f"{part.replace('IS,', '')} "
        elif "S," in part:
            p1 += f"[{symbol_table[int(part.split(',')[1])][1]}] "
        elif "R," in part:
            p1 += f"{part.replace('R,', '')} "
        elif "AD,1" in part:
            p1 += "-"
            parts[i + 1] = ""
        elif "AD,2" in part:
            p1 += part.replace('AD,2', "")
        elif "C,":
            p1 += f"{part.replace('C,', '')}"
    machine_code.append(p1)    

print("\nMachine Code:\n")
print("LC   | Machine Code")
print("-" * 30)
for line in machine_code:
    print(line)
