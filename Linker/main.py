import os

# Define tables
reloc_tabs = []  # RELOCTAB for each module
link_tabs = []  # LINKTAB for each module
global_ntab = {}  # NTAB for global Public symbols, labels, and linked addresses
combined_code = []  # Combined code with LC values for display
module_symbol_tables = []  # Store symbol tables for each module globally
module_start_addresses = []  # Store start address of each module


def read_module(filename):
    """
    Read a module file and extract address-sensitive instructions,
    public, extern symbols, and labels.
    """
    with open(filename, 'r') as file:
        lines = file.readlines()

    instructions = []
    public_symbols = []
    extern_symbols = []
    local_symbol_table = {}  # To store variable and label addresses
    labels = []  # Store all labels separately
    lc = 0  # Location Counter for each module

    for line in lines:
        line = line.strip()
        if not line or line.startswith(';'):  # Ignore empty lines and comments
            continue
        if line.startswith('START') or line.startswith('END'):
            continue


        if line.startswith("ENTRY"):
            symbol = line.split()[1]
            public_symbols.append(symbol)

        elif line.startswith("EXTERN"):
            symbol = line.split()[1]
            extern_symbols.append(symbol)
        elif ":" in line:  # Handle labels and variable definitions
            parts = line.split(":", 1)
            name = parts[0].strip()
            rest = parts[1].strip() if len(parts) > 1 else ""

            # Store in local symbol table
            local_symbol_table[name] = lc

            # If it's a label (not a variable definition)
            if not rest.startswith(("DC", "DS")):
                labels.append(name)

            # Add the full line to instructions
            instructions.append((lc, line))
            if rest.startswith("DS"):
                lc = int(rest.split()[1])
            else:
                lc += 1
        else:
            instructions.append((lc, line))
            lc += 1  # Increment LC for each line

    return instructions, public_symbols, extern_symbols, local_symbol_table, labels, lc


def process_module(filename, base_address):
    """
    Process a module file, creating RELOCTAB, LINKTAB, and updating NTAB.
    """
    reloc_tab = []
    link_tab = []

    # Store the module's start address
    module_start_addresses.append(base_address)

    # Read module data
    instructions, public_symbols, extern_symbols, local_symbol_table, labels, module_length = read_module(filename)

    # Store the local symbol table globally
    module_symbol_tables.append(local_symbol_table)

    # Process relocatable instructions
    for lc, instr in instructions:
        # Check for address-sensitive instructions
        if any(keyword in instr for keyword in ["VAR", "JMP", "CALL", "BR"]):
            reloc_tab.append(base_address + lc)

    # Track symbol references
    symbol_references = {}
    for lc, instr in instructions:
        instr_cleaned = instr.split(';')[0].strip()

        # Skip START and END directives
        if instr_cleaned.startswith(("START", "END")):
            continue

        # Add to combined code
        combined_code.append((base_address + lc, instr_cleaned))

        # Check for symbol references in instruction
        for symbol in public_symbols + extern_symbols + labels:
            if symbol in instr_cleaned and not instr_cleaned.startswith(f"{symbol}:"):
                symbol_references[symbol] = base_address + lc

    # Update LINKTAB with all symbol references
    for symbol in public_symbols:
        if symbol in local_symbol_table:
            global_ntab[symbol] = base_address + local_symbol_table[symbol]
        if symbol in symbol_references:
            link_tab.append((symbol, "Public", symbol_references[symbol]))

    for symbol in extern_symbols:
        if symbol in symbol_references:
            link_tab.append((symbol, "EXTERN", symbol_references[symbol]))

    # Add labels to NTAB and LINKTAB
    for label in labels:
        if label in local_symbol_table and label not in global_ntab.keys():
            global_ntab[label] = base_address + local_symbol_table[label]
            if label in symbol_references:
                link_tab.append((label, "Public", symbol_references[label]))

    return reloc_tab, link_tab, module_length


def linker(modules, link_origin):
    """
    Perform linking and relocation for the modules starting from link_origin.
    """
    base_address = link_origin

    for module_file in modules:
        # Process module and update tables
        reloc_tab, link_tab, module_length = process_module(module_file, base_address)

        reloc_tabs.append(reloc_tab)
        link_tabs.append(link_tab)

        base_address += module_length


def display_output():
    """
    Display the linker output in a well-formatted, organized way.
    """

    # Helper function to create headers
    def print_header(text, char='='):
        width = 60
        print(f"\n{char * width}")
        print(f"{text.center(width)}")
        print(f"{char * width}\n")



    # Module Start Addresses
    print_header("MODULE START ADDRESSES", '=')
    for i, start_addr in enumerate(module_start_addresses, 1):
        print(f"│ Module {i:<2} │ Start Address: {(start_addr):<8} │")

    # Combined Code Display
    print_header("COMBINED CODE WITH LOCATIONS", '=')
    print("╔══════════╦════════════════════════════════════════════════╗")
    print("║   LC     ║                 Instruction                    ║")
    print("╠══════════╬════════════════════════════════════════════════╣")

    for lc, instr in combined_code:
        # Process instruction
        modified_instr = instr
        if ":" in modified_instr:
            label, content = modified_instr.split(":", 1)
            modified_instr = content.strip()

        # Replace symbols with their addresses
        for symbol, addr in global_ntab.items():
            modified_instr = modified_instr.replace(symbol, f"[{(addr)}]")

        if "DC" in modified_instr:
            modified_instr = modified_instr.replace("DC", "").strip()
        if "DS" in modified_instr:
            modified_instr = "-"

        # Format and print the instruction line
        print(f"║ {(lc):<8} ║ {modified_instr:<46} ║")

    print("╚══════════╩════════════════════════════════════════════════╝")

    # Display Module Details
    for i, (reloc_tab, link_tab) in enumerate(zip(reloc_tabs, link_tabs), start=1):
        print_header(f"MODULE {i} DETAILS", '=')
        print(f"Start Address: {(module_start_addresses[i - 1])}")

        # RELOCTAB
        print("\n┌─ RELOCTAB ───┐")
        print("│   Address    │")
        print("├──────────────┤")
        for addr in reloc_tab:
            print(f"│     {(addr):<8} │")
        print("└──────────────┘")

        # LINKTAB
        print("\n┌─ LINKTAB ─────────────────────────────────────────────┐")
        print("│ Symbol      Type        Definition Address            │")
        print("├───────────────────────────────────────────────────────┤")
        for symbol, type_, ref_addr in link_tab:
            addr = global_ntab.get(symbol, "Unresolved")
            print(f"│ {symbol:<11} {type_:<11} {(addr):<29} │")
        print("└───────────────────────────────────────────────────────┘")

    # Global NTAB
    print_header("GLOBAL NTAB (ALL SYMBOLS)", '=')
    k = 0
    print("┌─────────────────────────────────────────┐")
    print("│ Symbol            Address               │")
    print("├─────────────────────────────────────────┤")
    for symbol, addr in global_ntab.items():
        if k<5 and addr >= module_start_addresses[k] :
            print(f"│ Module {k+1:<11} {(module_start_addresses[k]):<20} │")
            k +=1
        print(f"│ {symbol:<18} {(addr):<20} │")
    print("└─────────────────────────────────────────┘")

# Main execution
if __name__ == "__main__":
    link_origin = int(input("Enter the link origin (starting address): "))
    modules = ["module1.txt", "module2.txt", "module3.txt", "module4.txt", "module5.txt"]

    linker(modules, link_origin)
    display_output()