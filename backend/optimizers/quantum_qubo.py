import dimod

def solve_junction_qubo(ns_cars: int, ew_cars: int, ns_wait: float, ew_wait: float) -> dict:
    # We assign weights: Cars are important, but Wait Time is heavily penalized to prevent starvation.
    # We want to maximize flow, which means minimizing the negative score of the green lane.
    
    score_ns = ns_cars + (ns_wait * 2.0)
    score_ew = ew_cars + (ew_wait * 2.0)
    
    P = max(score_ns, score_ew) * 2 # Penalty for turning both green
    
    Q = {
        ('q_NS', 'q_NS'): -score_ns - P,
        ('q_EW', 'q_EW'): -score_ew - P,
        ('q_NS', 'q_EW'): 2 * P
    }
    
    sampler = dimod.ExactSolver()
    response = sampler.sample_qubo(Q)
    best = response.first.sample
    
    return {
        "north_south_green": bool(best['q_NS']),
        "east_west_green": bool(best['q_EW']),
        "energy": response.first.energy
    }