import os
import time
import tracemalloc
import csv

def parse_dimacs(dimacs_input):
    clauses = []
    variable_map = {}
    reverse_map = {}
    next_id = 1

    for line in dimacs_input.split('\n'):
        line = line.strip()
        if not line or line.startswith(('c', '%')):
            continue
        if line.startswith('p'):
            continue
        literals = []
        for x in line.split():
            try:
                literal = int(x)
                if literal != 0:
                    literals.append(literal)
            except ValueError:
                continue
        clause = set()
        for lit in literals:
            var = abs(lit)
            if var not in variable_map:
                variable_map[var] = f'x{next_id}'
                reverse_map[f'x{next_id}'] = var
                next_id += 1
            var_name = variable_map[var]
            literal = var_name if lit > 0 else f'-{var_name}'
            clause.add(literal)
        clauses.append(frozenset(clause))
    return clauses, variable_map, reverse_map

def resolve(clause1, clause2):
    for literal in clause1:
        negation = ('-' + literal) if literal[0] != '-' else literal[1:]
        if negation in clause2:
            resolvent = (clause1 - {literal}) | (clause2 - {negation})
            return frozenset(resolvent)
    return None

def resolution(dimacs_input):
    clauses, variable_map, reverse_map = parse_dimacs(dimacs_input)
    new = set()

    while True:
        pairs = [(clauses[i], clauses[j]) for i in range(len(clauses)) for j in range(i + 1, len(clauses))]
        for (ci, cj) in pairs:
            resolvent = resolve(ci, cj)
            if resolvent is not None:
                if not resolvent:
                    return False  
                new.add(resolvent)

        if not new:
            return True  

        new_clauses = set(clauses) | new
        if new_clauses == set(clauses):
            return True 

        clauses = list(new_clauses)
        new = set()

def test_all_cnf_files(folder_path, output_csv):
    write_header = not os.path.exists(output_csv)

    for filename in os.listdir(folder_path):
        if filename.endswith(".cnf"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, "r") as f:
                    dimacs_input = f.read()

                tracemalloc.start()
                start = time.perf_counter()

                result = resolution(dimacs_input)

                elapsed = time.perf_counter() - start
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                with open(output_csv, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    if write_header:
                        writer.writerow(["filename", "time_sec", "peak_mem_kb", "result"])
                        write_header = False
                    writer.writerow([filename, f"{elapsed:.4f}", peak // 1024, "UNSAT" if result is False else "SAT"])

                print(f"{filename}: {'UNSAT' if result is False else 'SAT'} in {elapsed:.4f}s, {peak // 1024} KB peak memory")

            except Exception as e:
                with open(output_csv, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    if write_header:
                        writer.writerow(["filename", "time_sec", "peak_mem_kb", "result"])
                        write_header = False
                    writer.writerow([filename, "ERROR", "ERROR", f"ERROR: {e}"])

                print(f"{filename}: ERROR - {e}")

if __name__ == "__main__":
    test_folder = "benchmarks"  
    output_file = "resolution_results.csv" 
    test_all_cnf_files(test_folder, output_file)
