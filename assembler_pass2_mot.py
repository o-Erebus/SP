with open('input_intermediate_code.txt', 'r') as f:
    intermediate_code = [line.strip().split(" ",1) for line in f.readlines()]

with open('input_symbol_table.txt', 'r') as f:
    symbol_table = [line.strip().split() for line in f.readlines()]
    symbol_table = {int(line[0]): line[1:] for line in symbol_table}


machine_code=[]
for inst in intermediate_code: 
    parts = inst[1].split()
    p1 = f"{inst[0]} |"
    for i,part in enumerate(parts):
        part = part.replace("(","")
        part = part.replace(")","")
        if "AD,4" in part or "AD,0" in part:
            p1 = ""
            break
        elif "IS," in part:
            p1 += f"{part.replace("IS,","")} "
        elif "S," in part:
            p1 += f"[{symbol_table[int(part.split(',')[1])][1]}] "
        elif "R," in part:
            p1 += f"{part.replace("R,","")} "
        
        elif "AD,1" in part:
            p1 += "-"
            parts[i+1] = ""
        elif "AD,2" in part:
            p1 += part.replace("AD,2","")
        elif "C,":
            p1 += f"{part.replace("C,","")}"
        
    machine_code.append(p1)    

print("\nMachine Code:\n")
print("LC   | Machine Code")
print("-" * 30)
for line in machine_code:
    print(line)

