from typing import List, Dict
import neal

def solve_grid_simulation(junctions: List[Dict]) -> Dict:
    results = {"classical": {}, "ai": {}, "quantum": {}}
    Q = {}
    
    MIN_GREEN_TIME = 15 # Ticks

    for j in junctions:
        score_ns = j["ns_cars"] + (j["ns_wait"] * 2.5)
        score_ew = j["ew_cars"] + (j["ew_wait"] * 2.5)
        
        lock_ns = j["ns_green"] and j["ns_green_time"] < MIN_GREEN_TIME and j["ns_cars"] > 0
        lock_ew = j["ew_green"] and j["ew_green_time"] < MIN_GREEN_TIME and j["ew_cars"] > 0

        # Classical Logic (Dumb Timer)
        if lock_ns:
            res_c_ns, res_c_ew = True, False
        elif lock_ew:
            res_c_ns, res_c_ew = False, True
        else:
            res_c_ns, res_c_ew = (True, False) if j["ns_wait"] > j["ew_wait"] else (False, True)
        results["classical"][j["id"]] = {"ns": res_c_ns, "ew": res_c_ew}
        
        # AI Logic (Greedy + Lock)
        if lock_ns:
            res_a_ns, res_a_ew = True, False
        elif lock_ew:
            res_a_ns, res_a_ew = False, True
        else:
            res_a_ns, res_a_ew = (True, False) if score_ns >= score_ew else (False, True)
        results["ai"][j["id"]] = {"ns": res_a_ns, "ew": res_a_ew}
        
        # Quantum QUBO
        if lock_ns: score_ns += 10000
        if lock_ew: score_ew += 10000

        P = max(score_ns, score_ew) * 2 + 10 
        ns_v = f"{j['id']}_ns"
        ew_v = f"{j['id']}_ew"
        
        Q[(ns_v, ns_v)] = -score_ns - P
        Q[(ew_v, ew_v)] = -score_ew - P
        Q[(ns_v, ew_v)] = 2.5 * P
        
    for i in range(len(junctions) - 1):
        j1 = junctions[i]["id"]
        j2 = junctions[i+1]["id"]
        Q[(f"{j1}_ns", f"{j2}_ns")] = -15  
        Q[(f"{j1}_ew", f"{j2}_ew")] = -5   

    sampler = neal.SimulatedAnnealingSampler()
    response = sampler.sample_qubo(Q, num_reads=1)
    best = response.first.sample
    
    for j in junctions:
        ns_v = f"{j['id']}_ns"
        ew_v = f"{j['id']}_ew"
        results["quantum"][j["id"]] = {"ns": bool(best.get(ns_v, 0)), "ew": bool(best.get(ew_v, 0))}
        
    return results
