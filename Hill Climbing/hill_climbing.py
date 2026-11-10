"""Hill climbing for the CVRPTW: plain hill climbing, VND, and Iterated Local Search.

A solution is a list of routes; a route is a list of customer numbers (the depot 0
is implicit at both ends). The objective is the total distance, plus a large
penalty for every route above the fleet size k.
"""
import math
import random
import time
from pathlib import Path

FLEET_PENALTY = 10_000.0
N_NEIGHBOURS = 20


# --------------------------------------------------------------------------- data
class Instance:
    """CVRPTW instance read from a Cordeau-format file (Solomon benchmark)."""

    def __init__(self, path, n_customers=None):
        lines = [l.split() for l in Path(path).read_text().splitlines() if l.strip()]
        # Header: "type k n days" then "max_duration capacity"; a few files break these
        # lines differently, so read the header tokens up to the depot row (id 0).
        first = next(i for i, l in enumerate(lines) if len(l) >= 9 and l[0] == "0")
        header = [float(t) for l in lines[:first] for t in l]
        rows = lines[first:]
        n = len(rows) - 1
        self.name = Path(path).name
        self.k = int(header[header.index(float(n)) - 1])
        self.capacity = header[-1]
        if n_customers is not None:
            rows = rows[:n_customers + 1]
        self.n = len(rows) - 1
        self.x = [float(r[1]) for r in rows]
        self.y = [float(r[2]) for r in rows]
        self.service = [float(r[3]) for r in rows]
        self.demand = [float(r[4]) for r in rows]
        self.ready = [float(r[-2]) for r in rows]
        self.due = [float(r[-1]) for r in rows]
        size = self.n + 1
        self.dist = [[math.hypot(self.x[i] - self.x[j], self.y[i] - self.y[j]) for j in range(size)]
                     for i in range(size)]
        # Granular neighbourhoods: moves only try to place a customer next to one of
        # its closest customers, which keeps every sweep linear in n.
        self.neighbours = [
            sorted((j for j in range(1, size) if j != i), key=lambda j: self.dist[i][j])[:N_NEIGHBOURS]
            for i in range(size)
        ]


# --------------------------------------------------------------------------- routes
class Route:
    """A route with cached data that makes most feasibility checks O(1).

    seq[p]     node at position p (seq[0] and seq[-1] are the depot)
    start[p]   earliest start of service at position p
    latest[p]  latest start of service at p that keeps the rest of the route feasible
    load[p]    total demand of seq[1..p]
    """

    def __init__(self, inst, customers):
        self.inst = inst
        self.set(customers)

    def set(self, customers):
        inst = self.inst
        d, s = inst.dist, inst.service
        seq = [0] + list(customers) + [0]
        m = len(seq)
        start, load = [0.0] * m, [0.0] * m
        start[0] = inst.ready[0]
        dist = 0.0
        for p in range(1, m):
            a, b = seq[p - 1], seq[p]
            start[p] = max(inst.ready[b], start[p - 1] + s[a] + d[a][b])
            load[p] = load[p - 1] + inst.demand[b]
            dist += d[a][b]
        latest = [0.0] * m
        latest[-1] = inst.due[0]
        for p in range(m - 2, -1, -1):
            a, b = seq[p], seq[p + 1]
            latest[p] = min(inst.due[a], latest[p + 1] - s[a] - d[a][b])
        self.seq, self.start, self.latest, self.load, self.distance = seq, start, latest, load, dist

    @property
    def customers(self):
        return self.seq[1:-1]

    def __len__(self):
        return len(self.seq) - 2


def route_is_feasible(inst, customers):
    """Full O(m) check of one route: capacity, time windows and return to the depot."""
    if sum(inst.demand[c] for c in customers) > inst.capacity + 1e-9:
        return False
    t, prev = inst.ready[0], 0
    for c in list(customers) + [0]:
        t = max(inst.ready[c], t + inst.service[prev] + inst.dist[prev][c])
        if t > inst.due[c] + 1e-9:
            return False
        prev = c
    return True


def route_distance(inst, customers):
    seq = [0] + list(customers) + [0]
    return sum(inst.dist[a][b] for a, b in zip(seq, seq[1:]))


# --------------------------------------------------------------------------- solution
class Solution:
    def __init__(self, inst, routes):
        self.inst = inst
        self.routes = [Route(inst, r) for r in routes if r]
        self.reindex()

    def reindex(self):
        self.routes = [r for r in self.routes if len(r) > 0]
        self.where = {}
        for ri, r in enumerate(self.routes):
            for p in range(1, len(r.seq) - 1):
                self.where[r.seq[p]] = (ri, p)

    def update(self, ri):
        r = self.routes[ri]
        for p in range(1, len(r.seq) - 1):
            self.where[r.seq[p]] = (ri, p)

    def distance(self):
        return sum(r.distance for r in self.routes)

    def n_routes(self):
        return sum(1 for r in self.routes if len(r) > 0)

    def cost(self):
        return self.distance() + FLEET_PENALTY * max(0, self.n_routes() - self.inst.k)

    def as_lists(self):
        return [r.customers for r in self.routes if len(r) > 0]

    def is_feasible(self, check_fleet=True):
        seen = sorted(c for r in self.as_lists() for c in r)
        if seen != list(range(1, self.inst.n + 1)):
            return False
        if check_fleet and self.n_routes() > self.inst.k:
            return False
        return all(route_is_feasible(self.inst, r) for r in self.as_lists())


def removal_bonus(sol, emptied):
    """Penalty saved when `emptied` routes disappear and the fleet is above k."""
    excess = sol.n_routes() - sol.inst.k
    return FLEET_PENALTY * min(emptied, max(0, excess))


# --------------------------------------------------------------------------- construction
def best_insertion(sol, u):
    """Cheapest feasible position for customer u: (extra distance, route index, position)."""
    inst = sol.inst
    d, s = inst.dist, inst.service
    best = (math.inf, None, None)
    for ri, r in enumerate(sol.routes):
        if r.load[-1] + inst.demand[u] > inst.capacity:
            continue
        seq, start, latest = r.seq, r.start, r.latest
        for q in range(len(seq) - 1):
            a, b = seq[q], seq[q + 1]
            extra = d[a][u] + d[u][b] - d[a][b]
            if extra >= best[0]:
                continue
            t = max(inst.ready[u], start[q] + s[a] + d[a][u])
            if t <= inst.due[u] and t + s[u] + d[u][b] <= latest[q + 1]:
                best = (extra, ri, q + 1)
    return best


def insert_customers(sol, customers):
    """Insert each customer at its cheapest feasible position, opening a new route if none fits."""
    for u in customers:
        extra, ri, pos = best_insertion(sol, u)
        if ri is None:
            sol.routes.append(Route(sol.inst, [u]))
            sol.update(len(sol.routes) - 1)
        else:
            r = sol.routes[ri]
            c = r.customers
            c.insert(pos - 1, u)
            r.set(c)
            sol.update(ri)
    return sol


def construct(inst):
    """Greedy start: customers sorted by the end of their time window, cheapest insertion."""
    sol = Solution(inst, [])
    order = sorted(range(1, inst.n + 1), key=lambda c: inst.due[c])
    return insert_customers(sol, order)


# --------------------------------------------------------------------------- moves
# Each move function scans the neighbours of customer u, applies the first move that
# lowers the cost, and returns True; it returns False if no improving move exists.

def move_relocate(sol, u):
    """Move u next to (before or after) one of its neighbours v, in another route or the same one."""
    inst = sol.inst
    d, s = inst.dist, inst.service
    ra, pa = sol.where[u]
    A = sol.routes[ra]
    a_prev, a_next = A.seq[pa - 1], A.seq[pa + 1]
    gain_remove = d[a_prev][u] + d[u][a_next] - d[a_prev][a_next]
    bonus = removal_bonus(sol, 1) if len(A) == 1 else 0.0
    for v in inst.neighbours[u]:
        rb, pb = sol.where[v]
        B = sol.routes[rb]
        for q in (pb - 1, pb):                      # insert between seq[q] and seq[q+1]
            b1, b2 = B.seq[q], B.seq[q + 1]
            if b1 == u or b2 == u:
                continue
            delta = d[b1][u] + d[u][b2] - d[b1][b2] - gain_remove
            if ra != rb:
                if delta - bonus >= -1e-9 or B.load[-1] + inst.demand[u] > inst.capacity:
                    continue
                t = max(inst.ready[u], B.start[q] + s[b1] + d[b1][u])
                if t > inst.due[u] or t + s[u] + d[u][b2] > B.latest[q + 1]:
                    continue
                newA = A.customers
                newA.remove(u)
                newB = B.customers
                newB.insert(q, u)
                A.set(newA)
                B.set(newB)
                sol.update(ra)
                sol.update(rb)
                if len(A) == 0:
                    sol.reindex()
                return True
            else:
                if delta >= -1e-9:
                    continue
                c = A.customers
                c.remove(u)
                c.insert(q - 1 if q > pa else q, u)
                if route_is_feasible(inst, c):
                    A.set(c)
                    sol.update(ra)
                    return True
    return False


def move_swap(sol, u):
    """Exchange u with a neighbour v that lies in another route."""
    inst = sol.inst
    d, s, dem = inst.dist, inst.service, inst.demand
    ra, pa = sol.where[u]
    A = sol.routes[ra]
    a1, a2 = A.seq[pa - 1], A.seq[pa + 1]
    for v in inst.neighbours[u]:
        rb, pb = sol.where[v]
        if rb == ra:
            continue
        B = sol.routes[rb]
        b1, b2 = B.seq[pb - 1], B.seq[pb + 1]
        delta = (d[a1][v] + d[v][a2] - d[a1][u] - d[u][a2]
                 + d[b1][u] + d[u][b2] - d[b1][v] - d[v][b2])
        if delta >= -1e-9:
            continue
        if A.load[-1] - dem[u] + dem[v] > inst.capacity or B.load[-1] - dem[v] + dem[u] > inst.capacity:
            continue
        tv = max(inst.ready[v], A.start[pa - 1] + s[a1] + d[a1][v])
        if tv > inst.due[v] or tv + s[v] + d[v][a2] > A.latest[pa + 1]:
            continue
        tu = max(inst.ready[u], B.start[pb - 1] + s[b1] + d[b1][u])
        if tu > inst.due[u] or tu + s[u] + d[u][b2] > B.latest[pb + 1]:
            continue
        newA, newB = A.customers, B.customers
        newA[pa - 1], newB[pb - 1] = v, u
        A.set(newA)
        B.set(newB)
        sol.update(ra)
        sol.update(rb)
        return True
    return False


def move_two_opt_star(sol, u):
    """Exchange route tails so that u is followed by its neighbour v (2-opt*).

    A = a[..u] + a[after u..],  B = b[..before v] + b[v..]
    becomes A' = a[..u] + b[v..] and B' = b[..before v] + a[after u..].
    """
    inst = sol.inst
    d, s = inst.dist, inst.service
    ra, pa = sol.where[u]
    A = sol.routes[ra]
    a_next = A.seq[pa + 1]
    for v in inst.neighbours[u]:
        rb, pb = sol.where[v]
        if rb == ra:
            continue
        B = sol.routes[rb]
        b_prev = B.seq[pb - 1]
        delta = d[u][v] + d[b_prev][a_next] - d[u][a_next] - d[b_prev][v]
        emptied = 1 if (pb == 1 and a_next == 0) else 0
        if delta - removal_bonus(sol, emptied) >= -1e-9:
            continue
        if A.load[pa] + B.load[-1] - B.load[pb - 1] > inst.capacity:
            continue
        if B.load[pb - 1] + A.load[-1] - A.load[pa] > inst.capacity:
            continue
        if A.start[pa] + s[u] + d[u][v] > B.latest[pb]:
            continue
        if B.start[pb - 1] + s[b_prev] + d[b_prev][a_next] > A.latest[pa + 1]:
            continue
        newA = A.seq[1:pa + 1] + B.seq[pb:-1]
        newB = B.seq[1:pb] + A.seq[pa + 1:-1]
        A.set(newA)
        B.set(newB)
        sol.update(ra)
        sol.update(rb)
        if len(B) == 0:
            sol.reindex()
        return True
    return False


NEIGHBOURHOODS = {
    "relocate": move_relocate,
    "swap": move_swap,
    "2-opt*": move_two_opt_star,
}


# --------------------------------------------------------------------------- local search
def hill_climb(sol, moves, rng):
    """First-improvement hill climbing: sweep the customers in random order and apply
    the first improving move found; stop when a full sweep finds no improvement."""
    improved_any = False
    customers = list(range(1, sol.inst.n + 1))
    improved = True
    while improved:
        improved = False
        rng.shuffle(customers)
        for u in customers:
            for move in moves:
                if move(sol, u):
                    improved = improved_any = True
                    break
    return improved_any


def vnd(sol, rng, order=("relocate", "swap", "2-opt*")):
    """Variable Neighbourhood Descent: hill climb in the first neighbourhood; when it is
    stuck, try the next one; after any improvement, go back to the first."""
    i = 0
    while i < len(order):
        if hill_climb(sol, [NEIGHBOURHOODS[order[i]]], rng) and i > 0:
            i = 0
        else:
            i += 1
    return sol


# --------------------------------------------------------------------------- perturbation
def perturb(sol, rng, min_remove=5, max_remove=15):
    """Ruin and recreate: remove a group of nearby customers (or, when the fleet is too
    large, the smallest route) and reinsert them greedily in random order."""
    inst = sol.inst
    if sol.n_routes() > inst.k and rng.random() < 0.5:
        removed = min(sol.routes, key=len).customers
    else:
        seed = rng.randint(1, inst.n)
        size = rng.randint(min_remove, min(max_remove, inst.n))
        removed = [seed] + inst.neighbours[seed][:size - 1]
    removed_set = set(removed)
    routes = [[c for c in r.customers if c not in removed_set] for r in sol.routes]
    new = Solution(inst, routes)
    rng.shuffle(removed)
    return insert_customers(new, removed)


def copy_solution(sol):
    return Solution(sol.inst, sol.as_lists())


# --------------------------------------------------------------------------- algorithms
def solve(inst, method="ils", time_limit=30.0, seed=0, max_iterations=None, removal=(5, 15)):
    """Run one of the three variants and return (best solution, history, iterations).

    method: "hc"  plain hill climbing (relocate only)
            "vnd" hill climbing with several neighbourhoods (VND)
            "ils" Iterated Local Search around VND, until the time limit
                  (or until max_iterations perturbations, if given)
    removal: (min, max) number of customers removed by each perturbation.
    history: (seconds, distance, number of routes) each time the best solution improves.
    """
    rng = random.Random(seed)
    t0 = time.perf_counter()

    def record(s):
        history.append((time.perf_counter() - t0, s.distance(), s.n_routes()))

    history = []
    sol = construct(inst)
    record(sol)
    if method == "hc":
        hill_climb(sol, [move_relocate], rng)
        record(sol)
        return sol, history, 0
    vnd(sol, rng)
    record(sol)
    if method == "vnd":
        return sol, history, 0

    current, best = sol, copy_solution(sol)
    best_cost = current_cost = sol.cost()
    iterations = 0
    while time.perf_counter() - t0 < time_limit:
        if max_iterations is not None and iterations >= max_iterations:
            break
        candidate = vnd(perturb(current, rng, *removal), rng)
        iterations += 1
        cand_cost = candidate.cost()
        if cand_cost < current_cost - 1e-9:
            current, current_cost = candidate, cand_cost
        if cand_cost < best_cost - 1e-9:
            best, best_cost = copy_solution(candidate), cand_cost
            record(best)
    return best, history, iterations
