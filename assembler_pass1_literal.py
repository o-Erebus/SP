import re

MOT = {
    'MOV': {'opcode': '10', 'length': 1, 'operands': 2},
    'ADD': {'opcode': '11', 'length': 1, 'operands': 2},
    'SUB': {'opcode': '12', 'length': 1, 'operands': 2},
    'JMP': {'opcode': '13', 'length': 1, 'operands': 1},
    'RET': {'opcode': '14', 'length': 1, 'operands': 0}
}

assembly_code = open("input_assembler_literal.txt", "r").read()

literal_table = []
pool_table = []
literal_pool = []
intermediate_code = []
errors = []
lc = 0

lines = assembly_code.strip().split('\n')
for line in lines:
    line = line.strip()
    if not line: continue
    
    parts = line.replace(',', ' ').split()
    
    if parts[0] == 'START':
        intermediate_code.append((lc, f"(AD,0) (C,{parts[1]})"))
        lc = int(parts[1])
        continue

    if parts[0] == 'LTORG':
        intermediate_code.append((lc, "(AD,3)"))
        pool_table.append(lc)
        for literal in literal_pool:
            literal_table.append((literal, lc, len(pool_table) - 1))
            lc += 1
        literal_pool.clear()
        continue

    if parts[0] == 'END':
        intermediate_code.append((lc, "(AD,4)"))
        if literal_pool:
            pool_table.append(lc)
            for literal in literal_pool:
                literal_table.append((literal, lc, len(pool_table) - 1))
                lc += 1
        literal_pool.clear()
        continue

    for part in parts:
        if part.startswith('"') and part.endswith('"') and part not in literal_pool:
            literal_pool.append(part)

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
        
        for i in range(1, len(parts)):
            if parts[i].isdigit():
                parts[i] = f"(C,{parts[i]})"
            elif parts[i] in literal_pool:
                parts[i] = f"(L,{len(literal_table)+literal_pool.index(parts[i])})"
        
        instr = ' '.join(parts)
        for i, reg in enumerate(['AX', 'BX', "CX", "DX"]):
            instr = instr.replace(reg, f"(R,{i})")
        intermediate_code.append((lc, instr))
        lc += 1

print("\nLiteral Table:")
print("Index | Literal | Address | Pool Index")
print("-" * 45)
for i, (lit, addr, pool_index) in enumerate(literal_table):
    print(f"{i:5} | {lit:7} | {addr} | {pool_index}")

print("\nPool Table:")
print("Pool Index | Pool Start Address")
print("-" * 30)
for i, addr in enumerate(pool_table):
    print(f"{i:10} | {addr}")

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
