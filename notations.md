# S4 – Shared Notation Sheet
**Project:** Time-dependent delivery routing (CesiCDP, ADEME call) – **Problem name:** TD-CVRP-TW
*Single reference for all team members: every notebook section, the ILP and the code must use exactly these symbols.*

## 1. Conventions
- Sets: capital letters ($V, A, C, N, N^{+}$). Parameters: lowercase/Latin ($q_i, s_i, d_a$). Decision variables: $x, z, r, u, t, L, f$.
- Node `0` is always the depot. Customers are `1..n`. In the ILP, node `n+1` is a copy of the depot used as the end of a route.
- Time unit: **minute**. Distance unit: **km**. Speed unit: **km/min**. Demand unit: **parcel units** (or kg, to be fixed per instance).
- A generic instant is written $t$ (minutes), as in $\tau_a(t)$. With a customer index, $t_i$ is the departure-time variable of the ILP.
- Python variable names are given in the last column of each table so code and maths stay aligned.

## 2. Road network and traffic
| Symbol | Meaning | Python |
|---|---|---|
| $G=(V,A)$ | directed road network | `G` |
| $V$, $A$ | nodes (intersections, customer locations, depot) and arcs (road segments) | `V`, `A` |
| $a=(u,v)\in A$ | arc from $u$ to $v$ | `a` |
| $d_a>0$ | length of arc $a$ (km) | `length[a]` |
| $T$ | planning horizon end (min); horizon is $[0,T]$ | `T` |
| $K$ | number of time slots | `K` |
| $\beta_0=0<\beta_1<\dots<\beta_K=T$ | slot breakpoints (min) | `breakpoints` |
| $s\in\{1,\dots,K\}$ | slot index (slot $s$ = $[\beta_{s-1},\beta_s)$) | `s` |
| $v_a^{s}>0$ | speed on arc $a$ during slot $s$ (km/min) | `speed[a][s]` |
| $\tau_a(t)$ | travel time on arc $a$ when entering at time $t$ (min) | `tau_arc(a,t)` |
| $\alpha_a(t)=t+\tau_a(t)$ | arrival time on arc $a$ when entering at $t$ | `arrival_arc(a,t)` |
| FIFO | $t\mapsto\alpha_a(t)$ strictly increasing | – |

## 3. Customers, depot and fleet
| Symbol | Meaning | Python |
|---|---|---|
| $0$ | depot | `0` |
| $C\subset V\setminus\{0\}$, $n=\lvert C\rvert$ | set and number of customers to serve | `C`, `n` |
| $N=C\cup\{0\}$ | decision nodes | `N` |
| $q_i>0$ ($q_0=0$) | demand of customer $i$ | `demand[i]` |
| $s_i\ge0$ ($s_0=0$) | service duration at $i$ (min) | `service[i]` |
| $[a_i,b_i]\subseteq[0,T]$ | time window for the **start** of service at $i$ | `tw[i]` |
| $k$ | maximum number of trucks | `k` |
| $Q$ | capacity of each truck (identical), $q_i\le Q$ | `Q` |

## 4. Customer graph (reduced graph)
| Symbol | Meaning | Python |
|---|---|---|
| $H=(N,E)$ | complete directed graph on $N$ | `H` |
| $\tau_{ij}(t)$ | minimum travel time from $i$ to $j$ when leaving at $t$ (time-dependent shortest path in $G$) | `tau(i,j,t)` |
| $\alpha_{ij}(t)=t+\tau_{ij}(t)$ | earliest arrival at $j$ | `arrival(i,j,t)` |

## 5. Solution (route-based notation)
| Symbol | Meaning |
|---|---|
| $r\le k$ | number of routes used |
| $R_\ell=(0,i^\ell_1,\dots,i^\ell_{m_\ell},0)$ | route $\ell$, with $m_\ell$ customers |
| $t_0^\ell$ | departure time of route $\ell$ from the depot (fixed to $0$ in the current ILP, see A9; a free departure time is a planned refinement) |
| $u_p^\ell$ | start of service of the $p$-th customer of route $\ell$ |
| $u^\ell_{m_\ell+1}$ | return time to the depot |
| $D(R_\ell)=u^\ell_{m_\ell+1}-t_0^\ell$ | duration of route $\ell$ |
| **Objective** | $\min\sum_{\ell=1}^r D(R_\ell)$ |

## 6. ILP (slot-based formulation, `ILP Models/ILP_model.md`)
| Symbol | Meaning | Python |
|---|---|---|
| $n+1$ | copy of the depot, end of a route | `n + 1` |
| $N^{+}=C\cup\{n+1\}$ | possible destinations of an arc (origins are $N$) | `N_plus` |
| $\tau^{s}_{ij}$ | travel time from $i$ to $j$ when leaving $i$ during slot $s$ (shortest path in $G$ with slot-$s$ speeds); $\tau^{s}_{i,n+1}=\tau^{s}_{i0}$ | `tau_slot[i][j][s]` |
| $\varepsilon$ | time resolution making slots half-open | `eps` |
| $M_{ij}$, $M_i$ | big-M constants, $T+\max_s\tau^{s}_{ij}$ and $T+\max_s\tau^{s}_{i0}$ | `M[i][j]`, `M_ret[i]` |
| $x_{ij}\in\{0,1\}$ | a truck drives directly from $i\in N$ to $j\in N^{+}$ | `x[i, j]` |
| $z^{s}_{i}\in\{0,1\}$ | the truck leaves $i$ during slot $s$ | `z[i, s]` |
| $r_i\ge0$ | arrival time at $i$ | `r[i]` |
| $u_i\in[a_i,b_i]$ | start of service at $i$ | `u[i]` |
| $t_i\in[0,T)$ | departure time from $i$ | `t[i]` |
| $w_i=u_i-r_i$ | waiting time at $i$ (derived, not a variable) | – |
| $L_i\in[q_i,Q]$ | cumulative load delivered up to and including $i$ | `L[i]` |
| $f_i\in[0,T]$ | return time to the depot if $i$ is the last customer of its route, else $0$ | `f[i]` |

> **Note on collisions:** $H=(N,E)$ is only the customer graph (the time-expanded formulation, which also used $H$ as a time index, was dropped). $A$ is the arc set of $G$ and $d_a$ an arc length, so the ILP uses $r_i$ for arrival and $t_i$ for departure. $s$ is the slot index *and* $s_i$ the service time; slots are always written as a superscript ($v_a^{s}$, $\tau^{s}_{ij}$, $z^{s}_{i}$), service times always carry a customer index as a subscript.

## 7. Complexity vocabulary
| Symbol | Meaning |
|---|---|
| $\mathrm{P},\mathrm{NP}$ | classical complexity classes |
| $A\le_p B$ | polynomial-time reduction from $A$ to $B$ |
| HC | Hamiltonian Cycle |
| TSP, CVRP, VRPTW | travelling salesman, capacitated VRP, VRP with time windows |
| $\Delta$-TSP-D | decision TSP whose costs satisfy the triangle inequality |
| BP-D | decision Bin Packing |
| TD-CVRP | basic version (no time windows, no service times) |
| TD-CVRP-TW | full problem with time windows and service times |
| TD-CVRP-TW-D | decision version (is there a solution of duration $\le B$?) |
| $B$ | duration bound of the decision version |

## 8. Instance sizes (for the statistical study later)
| Symbol | Meaning |
|---|---|
| $n$ | number of customers (up to several thousand) |
| $\lvert V\rvert,\lvert A\rvert$ | size of the road network |
| $k,Q$ | fleet size and capacity |
| $\rho=\sum_i q_i/(kQ)$ | fleet load ratio (tightness of capacity), proposed instance parameter |
