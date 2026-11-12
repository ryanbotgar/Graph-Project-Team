# C1 – Context and Problem Statement

## C1.1 Context
ADEME has issued a call for expressions of interest to support demonstrators and pilot projects for new mobility solutions for people and goods, adapted to different types of territories. CesiCDP is already active in *Smart Multimodal Mobility*, having led several studies with partners. New transport technologies (electric, low-emission vehicles) are cheaper to run and cleaner, but they raise new challenges, especially in **optimizing resource management**.

Transport logistics is therefore a major issue for the future, with many applications: mail delivery, parcel delivery, road-network management, waste collection. The environmental impact of better routing (less time on the road, less congestion exposure, less fuel or energy) is potentially large.

Our team (4 people) answers the call to secure new contracts with attractive funding. CesiCDP chose to focus on **delivery route management**.

## C1.2 Problem statement
A depot, a road network and a set of customers are given. Customers must each be visited once by one of $k$ identical trucks of capacity $Q$. Each truck leaves the depot, serves a subset of customers and returns to the depot. The time needed to traverse a road segment depends on the **time slot** (expected traffic). We must choose which customers go in which route, the order of visits and the departure times so as to **minimize the total duration of the routes**.

The method must come from **Operations Research** and scale to **several thousand customers**.

## C1.3 Scope
| Level | Content |
|---|---|
| Basic version | model, Python code for large instances, statistical study of experimental behavior, fleet of $k$ identical trucks |
| Added constraints (to be more realistic and attractive for ADEME) | customer time windows $[a_i,b_i]$; service times $s_i$ |

The added constraints make the problem more difficult, which is accepted: it shows the realism and ambition of the proposal. The resulting problem is called **TD-CVRP-TW**.

## C1.4 Why it matters (arguments for ADEME)
- Real travel times vary strongly over the day; ignoring this gives routes that are optimistic and late in practice.
- Shorter total duration means lower energy use and emissions, and a better use of the fleet and drivers.
- The same model covers several applications (delivery, mail, waste collection) by changing demands and windows.
- The formal model supports later extensions: emissions-aware objective, electric fleet, uncertain traffic.

## C1.5 Deliverable expected at this stage
Modeling check (Prosit 3, not assessed): context, formal data/problem/objective, link with classical problems and complexity proof, first ILP (variables, objective, constraints), bibliographic references. **No solution method is required yet.**

---

# C2 – Formalization of Data and Assumptions

## C2.1 Input data
| Data | Symbol | Type / unit | Possible source |
|---|---|---|---|
| Road network | $G=(V,A)$ | directed graph | OpenStreetMap |
| Arc length | $d_a>0$ | km | OpenStreetMap geometry |
| Time slots | $0=\beta_0<\dots<\beta_K=T$ | minutes | chosen by the team (e.g. 5 slots over 12 h) |
| Speed per slot | $v_a^{s}>0$ | km/min | historical or predicted traffic data (open data, floating-car data) or a synthetic profile |
| Depot | node $0$ | node of $V$ | client |
| Customers | $C$, $n=\lvert C\rvert$ | subset of $V\setminus\{0\}$ | client orders |
| Demand | $q_i>0$ | units | orders |
| Service time | $s_i\ge0$ | minutes | estimated per stop |
| Time window | $[a_i,b_i]$ | minutes | client delivery slots |
| Fleet | $k$, $Q$ | integer, units | client fleet |

For the experiments, instances are **generated** (random points, synthetic congestion profiles with morning and evening peaks) and, if possible, completed with real road data.

## C2.2 Derived data
- **Travel time** $\tau_a(t)$ from the speeds, with speed changes when a breakpoint is crossed (Ichoua et al., 2003). Beyond $T$ the last slot's speed applies.
- **Customer graph** $H=(N,E)$, $N=C\cup\{0\}$, with $\tau_{ij}(t)$ obtained by time-dependent shortest paths on $G$.
- **Slot travel times** for the ILP: $\tau^{s}_{ij}$, the travel time from $i$ to $j$ when leaving during slot $s$, computed with the slot-$s$ speeds (see the notation sheet S4, section 6). The ILP uses this simpler *departure-slot* rule, which keeps the model linear; the exact Ichoua model above will be used by the heuristic and to evaluate its routes.

## C2.3 Assumptions
| # | Assumption | Justification / consequence |
|---|---|---|
| A1 | One depot; all trucks start and end there | standard in delivery; simplifies the model |
| A2 | All trucks are identical (capacity $Q$) and at most $k$ are used | basic version required by the project |
| A3 | Each customer is visited exactly once by one truck (no split delivery) | realistic for parcels; keeps the model simple |
| A4 | Demands are deliveries from the depot; load decreases along a route; $q_i\le Q$ | otherwise the instance is trivially infeasible |
| A5 | Travel times are deterministic and known (predicted traffic per slot) | stochastic traffic is a later extension |
| A6 | Speeds are piecewise constant per slot and the travel time follows the model of Ichoua et al., so the **FIFO** property holds | avoids unrealistic "leave later, arrive earlier" |
| A7 | Trucks may pass through other nodes without serving them | the customer graph uses shortest paths |
| A8 | A truck may wait at a customer if it arrives before the window opens; service must **start** within $[a_i,b_i]$ | usual convention for time windows |
| A9 | All trucks leave the depot at time $0$ | the duration of a route is its return time, which keeps the ILP simple; a free departure time (not counting waiting at the depot) is a planned refinement |
| A10 | Objective: sum over trucks of (return time $-$ departure time) | matches "minimize the total duration of the route" |
| A11 | All routes must be completed before $T$ | finite horizon |
| A12 | In the ILP, the travel time of a trip is fixed by the slot in which the truck leaves ($\tau^{s}_{ij}$) | keeps the ILP linear; it approximates the exact Ichoua travel time, which the heuristic will use |
| A13 | A route has no maximum duration and drivers have no break constraints | possible future extension |
| A14 | Single speed profile for all vehicle types (no emission model yet) | possible future extension |

## C2.4 Data validity conditions (to check on every instance)
1. $d_a>0$ and $v_a^s>0$ for all $a,s$.
2. $0<q_i\le Q$ for all $i$; for feasibility with $k$ trucks, $\sum_i q_i\le kQ$.
3. $0\le a_i\le b_i\le T$.
4. $G$ strongly connected on the nodes used (every customer reachable from and back to the depot).
5. Window feasibility (necessary condition): each customer must be reachable in time, i.e. $\alpha_{0i}(0)\le b_i$, and the depot must be reachable again before $T$ after serving it, i.e. $\max(a_i,\alpha_{0i}(0))+s_i+\tau_{i0}(\cdot)\le T$.

## C2.5 Open questions to settle with the team and tutor
- Final choice of $K$ and $T$.
- Free departure time from the depot (A9) and exact Ichoua travel times inside the ILP (A12): worth the extra model complexity for the final deliverable?
- Real traffic data or synthetic profiles for the experiments?
- Keep the objective as total duration only, or add a vehicle fixed cost?
- Confirm that both added constraints (time windows and service times) are kept in the final scope.
