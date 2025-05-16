import sys
import os
import csv
import time
import tracemalloc
from collections import defaultdict
from typing import List, Dict, Set, Optional, Tuple

def parse_dimacs(filename: str) -> Tuple[List[List[int]], int]:
    clauses = []
    num_vars = 0
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(('c', '%')):
                continue
            if line.startswith('p'):
                parts = line.split()
                if len(parts) >= 4:
                    num_vars = int(parts[2])
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

def unit_propagation(clauses: List[List[int]], assignment: Dict[int, bool]) -> Tuple[bool, List[List[int]]]:
    new_clauses = [clause[:] for clause in clauses]
    unit_clauses = [c for c in new_clauses if len(c) == 1]
    
    while unit_clauses:
        unit = unit_clauses.pop(0)
        literal = unit[0]
        var = abs(literal)
        value = literal > 0
        
        assignment[var] = value
        
        i = 0
        while i < len(new_clauses):
            clause = new_clauses[i]
            if literal in clause:
                new_clauses.pop(i)
                unit_clauses = [c for c in new_clauses if len(c) == 1]
                continue
            if -literal in clause:
                new_clauses[i] = [x for x in clause if x != -literal]
                if not new_clauses[i]:
                    return False, []
                if len(new_clauses[i]) == 1:
                    unit_clauses.append(new_clauses[i])
                i += 1
            else:
                i += 1
                
    return True, new_clauses

def find_pure_literals(clauses: List[List[int]], assigned: Set[int]) -> List[int]:
    literal_count = defaultdict(set)
    for clause in clauses:
        for lit in clause:
            if abs(lit) not in assigned:
                literal_count[lit].add(lit)
    
    pure_literals = []
    for lit in literal_count:
        var = abs(lit)
        if -lit not in literal_count and var not in assigned:
            pure_literals.append(lit)
            
    return pure_literals

def dpll(clauses: List[List[int]], assignment: Dict[int, bool], num_vars: int) -> Optional[Dict[int, bool]]:
    if not clauses:
        return assignment
    if any(len(clause) == 0 for clause in clauses):
        return None
    
    success, new_clauses = unit_propagation(clauses, assignment)
    if not success:
        return None
    if not new_clauses:
        return assignment
        
    assigned = set(assignment.keys())
    pure_literals = find_pure_literals(new_clauses, assigned)
    for lit in pure_literals:
        var = abs(lit)
        assignment[var] = lit > 0
        new_clauses = [c for c in new_clauses if lit not in c]
    
    if not new_clauses:
        return assignment
        
    for clause in new_clauses:
        for lit in clause:
            var = abs(lit)
            if var not in assignment:
                new_assignment = assignment.copy()
                new_assignment[var] = True
                result = dpll([c[:] for c in new_clauses if lit not in c or -lit in c], new_assignment, num_vars)
                if result is not None:
                    return result
                
                new_assignment = assignment.copy()
                new_assignment[var] = False
                result = dpll([c[:] for c in new_clauses if -lit not in c or lit in c], new_assignment, num_vars)
                if result is not None:
                    return result
                break
        if var not in assignment:
            break
            
    return None

def solve_sat(filename: str) -> Optional[Dict[int, bool]]:
    clauses, num_vars = parse_dimacs(filename)
    assignment = {}
    return dpll(clauses, assignment, num_vars)

def main():
    directory = './benchmarks'  
    output_csv = 'sat_results.csv'
    
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        sys.exit(1)
    
    files = [f for f in os.listdir(directory) if f.endswith('.cnf')]
    
    write_header = not os.path.exists(output_csv)
    
    for filename in files:
        filepath = os.path.join(directory, filename)
        print(f"Processing {filename}...")
        
        start_time = time.perf_counter()
        tracemalloc.start()
        
        result = solve_sat(filepath)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        end_time = time.perf_counter()
        
        time_taken = end_time - start_time
        peak_memory = peak // 1024
        
        result_str = 'SAT' if result else 'UNSAT'
        print(f"Result: {result_str}, Time: {time_taken:.4f}s, Peak Memory: {peak_memory} KB")
        
        with open(output_csv, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if write_header:
                writer.writerow(['filename', 'time_sec', 'peak_mem_kb', 'result'])
                write_header = False
            writer.writerow([filename, f"{time_taken:.4f}", peak_memory, result_str])

if __name__ == "__main__":
    main()


