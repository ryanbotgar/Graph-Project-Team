"""Run the experimental study in parallel and save the results as CSV/JSON files.

Usage: python experiments.py [main|variants|size|sensitivity|all]
"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

from hill_climbing import Instance, solve

HERE = Path(__file__).resolve().parent
INSTANCES = HERE.parent / "Instances" / "C-vrptw"
RESULTS = HERE / "results"

# Best known solutions (vehicles, distance) of the Solomon 100-customer instances, from
# SINTEF, https://www.sintef.no/projectweb/top/vrptw/100-customers/ (hierarchical
# objective: fewest vehicles first, then shortest distance).
BKS = {
    "c101": (10, 828.94), "c102": (10, 828.94), "c103": (10, 828.06), "c104": (10, 824.78),
    "c105": (10, 828.94), "c106": (10, 828.94), "c107": (10, 828.94), "c108": (10, 828.94),
    "c109": (10, 828.94),
    "c201": (3, 591.56), "c202": (3, 591.56), "c203": (3, 591.17), "c204": (3, 590.60),
    "c205": (3, 588.88), "c206": (3, 588.49), "c207": (3, 588.29), "c208": (3, 588.32),
    "r101": (19, 1650.80), "r102": (17, 1486.12), "r103": (13, 1292.68), "r104": (9, 1007.31),
    "r105": (14, 1377.11), "r106": (12, 1252.03), "r107": (10, 1104.66), "r108": (9, 960.88),
    "r109": (11, 1194.73), "r110": (10, 1118.84), "r111": (10, 1096.73), "r112": (9, 982.14),
    "r201": (4, 1252.37), "r202": (3, 1191.70), "r203": (3, 939.50), "r204": (2, 825.52),
    "r205": (3, 994.43), "r206": (3, 906.14), "r207": (2, 890.61), "r208": (2, 726.82),
    "r209": (3, 909.16), "r210": (3, 939.37), "r211": (2, 885.71),
    "rc101": (14, 1696.95), "rc102": (12, 1554.75), "rc103": (11, 1261.67), "rc104": (10, 1135.48),
    "rc105": (13, 1629.44), "rc106": (11, 1424.73), "rc107": (11, 1230.48), "rc108": (10, 1139.82),
    "rc201": (4, 1406.94), "rc202": (3, 1365.65), "rc203": (3, 1049.62), "rc204": (3, 798.46),
    "rc205": (4, 1297.65), "rc206": (3, 1146.32), "rc207": (3, 1061.14), "rc208": (3, 828.14),
}
ALL = sorted(BKS, key=lambda s: (s.rstrip("0123456789"), s))
SUBSET = ["c101", "c105", "c201", "c205", "r101", "r105", "r201", "r205", "rc101", "rc105", "rc201", "rc205"]
SEEDS = [0, 1, 2]


def instance_class(name):
    """Solomon class: letter part (C, R, RC) + series (1 = tight windows, 2 = wide windows)."""
    letters = name.rstrip("0123456789").upper()
    return letters + name[len(letters)]


def run_one(job):
    name, method, seed, time_limit, n_customers, max_iterations, removal = job
    inst = Instance(INSTANCES / name, n_customers)
    t = time.perf_counter()
    sol, history, iterations = solve(inst, method, time_limit, seed, max_iterations, tuple(removal))
    elapsed = time.perf_counter() - t
    bks_routes, bks_dist = BKS[name]
    return {
        "instance": name, "class": instance_class(name), "n": inst.n, "method": method,
        "seed": seed, "time_limit": time_limit, "max_iterations": max_iterations,
        "removal": f"{removal[0]}-{removal[1]}", "k": inst.k,
        "routes": sol.n_routes(), "distance": round(sol.distance(), 2),
        "feasible": sol.is_feasible(check_fleet=False), "fleet_ok": sol.n_routes() <= inst.k,
        "bks_routes": bks_routes, "bks_distance": bks_dist,
        "gap": round(100 * (sol.distance() - bks_dist) / bks_dist, 3) if inst.n == 100 else None,
        "time": round(elapsed, 3), "iterations": iterations,
        "history": history, "routes_list": sol.as_lists(),
    }


def run(jobs, out_name, processes=10):
    RESULTS.mkdir(exist_ok=True)
    t = time.perf_counter()
    with Pool(processes) as pool:
        rows = pool.map(run_one, jobs, chunksize=1)
    (RESULTS / f"{out_name}.json").write_text(json.dumps(rows))
    print(f"{out_name}: {len(rows)} runs in {time.perf_counter() - t:.0f}s")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("variants", "all"):
        run([(i, m, s, 0, None, None, (5, 15)) for i in ALL for m in ("hc", "vnd") for s in SEEDS], "variants")
    if which in ("main", "all"):
        run([(i, "ils", s, 60, None, None, (5, 15)) for i in ALL for s in SEEDS], "main")
    if which in ("size", "all"):
        jobs = [(i, m, s, 600, n, 200 if m == "ils" else None, (5, 15))
                for i in SUBSET for n in (25, 50, 100) for m in ("vnd", "ils") for s in SEEDS]
        run(jobs, "size")
    if which in ("sensitivity", "all"):
        jobs = [(i, "ils", s, 30, None, None, r)
                for i in SUBSET for r in ((2, 5), (5, 15), (15, 30)) for s in SEEDS[:2]]
        run(jobs, "sensitivity")
