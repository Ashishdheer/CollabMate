from typing import List, Dict
import numpy as np

def compute_skill_score(member: Dict, task: Dict) -> float:
    if not task.get('skills'): return 0.0
    total = 0.0
    for s, req in task['skills'].items():
        total += min(member.get('skills',{}).get(s,0) / max(1, req), 1.0)
    return total / len(task['skills'])

def compute_availability(member: Dict) -> float:
    cap = member.get('capacity_hours', 8)
    return max(0.0, 1 - (member.get('load_hours',0) / max(1, cap)))

def fairness_aware_assign(members: List[Dict], tasks: List[Dict]) -> Dict[int,int]:
    mems = [dict(m) for m in members]
    for m in mems: m['load_hours'] = 0.0
    prior_vals = np.array([m.get('prior_assignments',0) for m in mems], dtype=float)
    if prior_vals.max() == prior_vals.min():
        norm = np.zeros_like(prior_vals)
    else:
        norm = (prior_vals - prior_vals.min()) / (prior_vals.max() - prior_vals.min())
    for i, m in enumerate(mems): m['_prior_norm'] = float(norm[i])
    assignments = {}
    for t in tasks:
        best, best_score = None, -1.0
        for m in mems:
            sc = compute_skill_score(m, t); av = compute_availability(m)
            fairness_penalty = 1.0 - m['_prior_norm']
            combined = 0.6*sc + 0.25*av + 0.15*fairness_penalty
            if combined > best_score: best_score, best = combined, m
        assignments[t['id']] = best['id']; best['load_hours'] += t['estimate_hours']
    return assignments
