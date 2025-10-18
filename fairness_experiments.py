
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
from collections import defaultdict

OUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT_DIR, exist_ok=True)

def generate_members(rng, n_members=6):
    members = []
    for i in range(n_members):
        skills = {k:int(rng.integers(0,5)) for k in ["python","react","ml"]}
        capacity_hours = int(rng.choice([6,8,9,10]))
        prior_assignments = int(rng.integers(0,10))
        members.append({"id": i+1, "skills": skills, "capacity_hours": capacity_hours, "load_hours": 0.0, "prior_assignments": prior_assignments})
    return members

def generate_tasks(rng, n_tasks=100):
    tasks = []
    for t in range(n_tasks):
        k = rng.choice([1,1,2])
        chosen = rng.choice(["python","react","ml"], size=k, replace=False)
        required_skills = {s:int(rng.integers(1,4)) for s in chosen}
        estimate = float(rng.choice([1,2,3,4,5]))
        tasks.append({"id": t+1, "skills": required_skills, "estimate_hours": estimate})
    return tasks

def compute_skill_score(member, task):
    if not task["skills"]: return 0.0
    total = 0.0
    for s, req in task["skills"].items():
        total += min(member["skills"].get(s,0) / max(1, req), 1.0)
    return total / len(task["skills"])

def compute_availability(member):
    cap = member.get("capacity_hours", 8)
    return max(0.0, 1 - (member.get("load_hours",0) / max(1, cap)))

def assign_fairness_aware(members, tasks):
    mems = [dict(m) for m in members]
    for m in mems: m["load_hours"] = 0.0
    prior_vals = np.array([m["prior_assignments"] for m in mems], dtype=float)
    if prior_vals.max() == prior_vals.min():
        norm = np.zeros_like(prior_vals)
    else:
        norm = (prior_vals - prior_vals.min()) / (prior_vals.max() - prior_vals.min())
    for i, m in enumerate(mems): m["_prior_norm"] = float(norm[i])
    assignments = {}
    for t in tasks:
        best, best_score = None, -1.0
        for m in mems:
            sc = compute_skill_score(m, t)
            av = compute_availability(m)
            fairness_penalty = 1.0 - m["_prior_norm"]
            combined = 0.6*sc + 0.25*av + 0.15*fairness_penalty
            if combined > best_score: best_score, best = combined, m
        assignments[t['id']] = best['id']
        best['load_hours'] += t['estimate_hours']
    return assignments

def evaluate_assignments(members, tasks, assignments):
    assigned_hours = defaultdict(float)
    skill_matches = 0
    id2member = {m['id']: m for m in members}
    for t in tasks:
        mid = assignments[t['id']]
        assigned_hours[mid] += t['estimate_hours']
    for t in tasks:
        mid = assignments[t['id']]; mem = id2member[mid]; ok = True
        for s, req in t['skills'].items():
            if mem['skills'].get(s,0) < req: ok = False; break
        if ok: skill_matches += 1
    assigned_list = np.array(list(assigned_hours.values()), dtype=float)
    std_load = float(np.std(assigned_list)) if assigned_list.size>0 else 0.0
    mean_match_frac = skill_matches / len(tasks) if tasks else 0.0
    return {'std_load': std_load, 'mean_match_frac': mean_match_frac}

def run_experiments(n_runs=50, n_members=6, n_tasks=100):
    records = []
    for seed in range(n_runs):
        rng = np.random.default_rng(seed)
        members = generate_members(rng, n_members)
        tasks = generate_tasks(rng, n_tasks)
        af = assign_fairness_aware(members, tasks); ev_f = evaluate_assignments(members, tasks, af)
        records.append({'seed': seed, 'method': 'fairness_aware', 'std_load': ev_f['std_load'], 'mean_match_frac': ev_f['mean_match_frac']})
    df = pd.DataFrame(records)
    return df

if __name__ == '__main__':
    df = run_experiments(n_runs=50, n_members=6, n_tasks=100)
    OUT = os.path.join(OUT_DIR, 'agg_metrics.csv')
    df.to_csv(OUT, index=False)
    print('Saved', OUT)
