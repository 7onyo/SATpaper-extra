
import os
import time
import tracemalloc
import csv
import re
from itertools import product

def parse_dimacs(file_content):
    clauses = []
    num_vars = 0
    lines = file_content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith(('c', '%')):
            continue
        if line.startswith('p'):
            match = re.match(r'p\s+cnf\s+(\d+)\s+(\d+)', line)
            if match:
                num_vars = int(match.group(1))
            continue
        literals = []
        for x in line.split():
            try:
                literal = int(x)
                if literal != 0:
                    literals.append(literal)
            except ValueError:
                continue
        if literals:
            clauses.append(literals)
    return clauses, num_vars

def unit_propagation(clauses, assignment):
    while True:
        unit_clause = None
        literal = None
        for clause in clauses:
            unassigned = [lit for lit in clause if abs(lit) not in assignment]
            if len(unassigned) == 0 and not any(assignment.get(abs(lit), False) == (lit > 0) for lit in clause):
                return None, None
            if len(unassigned) == 1:
                unit_clause = clause
                literal = unassigned[0]
                break
        if unit_clause is None:
            break
        assignment[abs(literal)] = literal > 0
        clauses = [c for c in clauses if c != unit_clause]
        clauses = [[lit for lit in clause if lit != -literal] for clause in clauses]
        clauses = [clause for clause in clauses if literal not in clause]
    return clauses, assignment

def pure_literal_elimination(clauses, assignment):
    literals = set()
    for clause in clauses:
        for lit in clause:
            literals.add(lit)
    pure_literals = [lit for lit in literals if -lit not in literals]
    for lit in pure_literals:
        assignment[abs(lit)] = lit > 0
    clauses = [clause for clause in clauses if not any(lit in clause for lit in pure_literals)]
    return clauses, assignment

def resolution(clauses, var):
    pos_clauses = [c for c in clauses if var in c]
    neg_clauses = [c for c in clauses if -var in c]
    other_clauses = [c for c in clauses if var not in c and -var not in c]
    new_clauses = []
    for pos, neg in product(pos_clauses, neg_clauses):
        resolvent = [lit for lit in set(pos + neg) if lit != var and lit != -var]
        if resolvent and not any(lit in resolvent and -lit in resolvent for lit in resolvent):
            if resolvent not in new_clauses:
                new_clauses.append(resolvent)
    return other_clauses + new_clauses

def davis_putnam(clauses, assignment=None):
    if assignment is None:
        assignment = {}

    if not clauses:
        return assignment
    if any(not clause for clause in clauses):
        return None

    clauses, assignment = unit_propagation(clauses, assignment)
    if clauses is None:
        return None
    if not clauses:
        return assignment

    clauses, assignment = pure_literal_elimination(clauses, assignment)
    if not clauses:
        return assignment
    if any(not clause for clause in clauses):
        return None

    literals = set(abs(lit) for clause in clauses for lit in clause)
    if not literals:
        return assignment
    var = min(literals)
    clauses = resolution(clauses, var)
    return davis_putnam(clauses, assignment)

def solve_dimacs(file_content):
    clauses, num_vars = parse_dimacs(file_content)
    assignment = davis_putnam(clauses)
    return "UNSAT" if assignment is None else "SAT"

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

                result = solve_dimacs(dimacs_input)

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
    folder = "benchmarks"        
    output_file = "dp_results.csv"
    test_all_cnf_files(folder, output_file)
