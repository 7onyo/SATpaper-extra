import random
import time
import os
import csv
import tracemalloc

def parse_cnf_file(filepath):
    clauses = []
    num_variables = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c') or line.startswith('%'):
                continue
            if line.startswith('p'):
                parts = line.split()
                if parts[1] != 'cnf':
                    raise ValueError("File is not in CNF format")
                num_variables = int(parts[2])
                continue
            try:
                literals = [int(x) for x in line.split() if x != '0']
                if literals: 
                    clauses.append(frozenset(literals))  
            except ValueError:
                continue
    
    return clauses, num_variables

def walksat(clauses, num_variables, max_flips, p=0.5):
    assignment = [random.choice([True, False]) for _ in range(num_variables + 1)]
    
    for _ in range(max_flips):
        unsatisfied = []
        for clause in clauses:
            clause_satisfied = False
            for literal in clause:
                var = abs(literal)
                value = assignment[var] if literal > 0 else not assignment[var]
                if value:
                    clause_satisfied = True
                    break
            if not clause_satisfied:
                unsatisfied.append(clause)
        
        if not unsatisfied:
            return assignment[1:], 'SAT'
        
        clause = random.choice(unsatisfied)
        
        if random.random() < p:
            literal = random.choice(list(clause))
            var = abs(literal)
        else:
            best_var = None
            best_unsat_count = float('inf')
            for literal in clause:
                var = abs(literal)
                assignment[var] = not assignment[var]
                unsat_count = 0
                for c in clauses:
                    clause_satisfied = False
                    for lit in c:
                        v = abs(lit)
                        value = assignment[v] if lit > 0 else not assignment[v]
                        if value:
                            clause_satisfied = True
                            break
                    if not clause_satisfied:
                        unsat_count += 1
                assignment[var] = not assignment[var]
                
                if unsat_count < best_unsat_count:
                    best_unsat_count = unsat_count
                    best_var = var
            
            var = best_var
        
        assignment[var] = not assignment[var]
    
    return None, 'UNSAT'

def test_all_cnf_files(folder_path, output_csv, max_flips=10000, p=0.5):
    write_header = not os.path.exists(output_csv)
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".cnf"):
            file_path = os.path.join(folder_path, filename)
            print(f"Processing {filename}...")
            
            try:
                clauses, num_variables = parse_cnf_file(file_path)
                
                tracemalloc.start()
                start = time.perf_counter()
                
                _, result = walksat(clauses, num_variables, max_flips, p)
                
                elapsed = time.perf_counter() - start
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                
                with open(output_csv, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    if write_header:
                        writer.writerow(["filename", "time_sec", "peak_mem_kb", "result"])
                        write_header = False
                    writer.writerow([filename, f"{elapsed:.4f}", peak // 1024, result])
                
                print(f"{filename}: {result} in {elapsed:.4f}s, {peak // 1024} KB peak memory")
            
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
    output_file = "walksat_results.csv"  
    max_flips = 10000
    probability = 0.5
    test_all_cnf_files(test_folder, output_file, max_flips, probability)