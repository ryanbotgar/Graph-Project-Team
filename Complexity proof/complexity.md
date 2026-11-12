# X1 – Position of the problem in the literature

Our problem, **TD-CVRP-TW**, combines four features that each have a long history in Operations Research. Each line of the table adds one feature to the line above, so every problem in the table is a **special case** of the ones below it.

| Problem | Feature added | Reference |
|---|---|---|
| TSP | one vehicle, visit every city once, return to the start, minimize the length | Karp (1972), Garey & Johnson (1979) |
| CVRP | $k$ vehicles of capacity $Q$, each customer has a demand $q_i$ | Dantzig & Ramser (1959), Toth & Vigo (2014) |
| VRPTW | service times $s_i$ and time windows $[a_i,b_i]$, waiting allowed | Solomon (1987) |
| TDVRP | travel times depend on the departure time (traffic per slot) | Malandraki & Daskin (1992), Ichoua et al. (2003) |
| **TD-CVRP-TW** (ours) | all of the above, objective = total duration of the routes | Dabia et al. (2013), Gendreau et al. (2015) |

Two remarks place our problem more precisely:
- With time-dependent travel times, **minimizing duration is not the same as minimizing distance**. A shorter road taken at rush hour can be slower than a longer one, and a later departure can avoid a traffic peak. This is why we minimize duration (A10) rather than distance.
- The closest problem in the literature is the time-dependent VRP with time windows where the objective is the total route duration, studied by Dabia et al. (2013) with the Ichoua et al. (2003) travel-time model that we also use (A6).

The rest of this section proves that the decision version of TD-CVRP-TW is **NP-complete**, so the optimization problem is **NP-hard**. The proof uses the oldest problem of the table, the TSP.

# X2 – NP-hardness: reduction from the TSP

## X2.1 Decision version of our problem

Complexity classes are defined for yes/no questions, so we first state the decision version of the problem.

> **TD-CVRP-TW-D**
> *Instance:* road network $G=(V,A)$ with lengths $d_a$, time slots $\beta_0<\dots<\beta_K$ and speeds $v^{s}_a$; depot $0$, customers $C$ with demands $q_i$, service times $s_i$ and windows $[a_i,b_i]$; fleet size $k$, capacity $Q$, horizon $T$; a bound $B$.
> *Question:* is there a set of at most $k$ routes, each leaving the depot at time $0$ (A9), such that every customer is served exactly once, the load of every route is at most $Q$, every service starts inside its window, every truck is back by $T$, and the **total duration is at most $B$**?

If we could solve the optimization problem in polynomial time, we could answer TD-CVRP-TW-D in polynomial time by comparing the optimum with $B$. So proving that TD-CVRP-TW-D is NP-hard proves that the optimization problem is NP-hard too.

## X2.2 Source problem: metric TSP

> **$\Delta$-TSP-D**
> *Instance:* cities $\{0,\dots,m-1\}$, integer costs $c_{ij}=c_{ji}\ge1$ satisfying the triangle inequality $c_{ij}\le c_{ih}+c_{hj}$, a bound $B$.
> *Question:* is there a tour (a cycle visiting every city exactly once) of cost at most $B$?

$\Delta$-TSP-D is NP-complete (Garey & Johnson, 1979, problem ND22). The classical proof reduces Hamiltonian Cycle (NP-complete, Karp 1972) to it: give cost $1$ to the edges of the graph and cost $2$ to the non-edges, and ask for a tour of cost at most $m$. Costs in $\{1,2\}$ always satisfy the triangle inequality, since $c_{ij}\le2\le c_{ih}+c_{hj}$. The TSP is therefore NP-complete **even with the triangle inequality and costs in $\{1,2\}$** (Papadimitriou & Yannakakis, 1993).

**Why we need the triangle inequality.** In our problem a truck may drive through a node without serving it (A7), so the travel time between two customers is a **shortest-path** time. Shortest-path times always satisfy the triangle inequality. With metric costs, the direct road is already a shortest path, so the travel times in our instance are exactly the TSP costs.

## X2.3 The reduction

Given an instance $(m,c,B)$ of $\Delta$-TSP-D, we build the following instance of TD-CVRP-TW-D:

| Element of our instance | Value | Effect |
|---|---|---|
| Road network $G$ | $V=\{0,\dots,m-1\}$, an arc in each direction between every pair of cities, $d_{ij}=c_{ij}$ | one node per city |
| Time slots and speeds | $K=1$, $v^{1}_a=1$ km/min on every arc | $\tau_a(t)=d_a$ for all $t$: no traffic effect, FIFO holds |
| Depot and customers | depot $=$ city $0$, $C=\{1,\dots,m-1\}$, so $n=m-1$ | every city must be visited |
| Fleet | $k=1$, $q_i=1$, $Q=n$ | one truck that can carry everything |
| Service and windows | $s_i=0$, $a_i=0$, $b_i=T$ | windows never bind |
| Horizon | $T=m\cdot c_{\max}$, where $c_{\max}=\max c_{ij}$ | larger than the cost of any tour |
| Bound | $B$ (unchanged) | |

**Polynomial time.** The instance has $m$ nodes and $m(m-1)$ arcs, and its numbers are the costs $c_{ij}$, the constants $0$, $1$, $n$, and $T$, whose binary size is $O(\log m+\log c_{\max})$. The construction takes $O(m^2)$ time.

**Travel times.** With one slot and speed 1, $\tau_a(t)=d_a$ for every $t$. By the triangle inequality, the direct arc $(i,j)$ is a shortest path from $i$ to $j$, so $\tau_{ij}(t)=c_{ij}$ for every departure time $t$.

**What a solution looks like.** With $k=1$, a feasible solution is a single route $R=(0,\pi_1,\dots,\pi_n,0)$ where $(\pi_1,\dots,\pi_n)$ is an ordering of all the customers. The route leaves at time $0$, there is no service time, and waiting can only add time, so its duration is

$$
D(R)=c_{0\pi_1}+c_{\pi_1\pi_2}+\dots+c_{\pi_{n-1}\pi_n}+c_{\pi_n0}+(\text{total waiting})\ \ge\ c(0,\pi_1,\dots,\pi_n,0),
$$

with equality when the truck never waits, which is always allowed since $a_i=0$.

## X2.4 Correctness

**($\Rightarrow$) If the TSP instance is a yes-instance, so is ours.** Take a tour of cost at most $B$ and rotate it so that it starts at city $0$: $(0,\pi_1,\dots,\pi_n,0)$. Use it as the single route, with no waiting. Every customer is served once. The load is $n=Q$. Every arrival time is at most the tour cost, which is at most $m\cdot c_{\max}=T=b_i$, so all windows and the horizon are respected. The duration equals the tour cost, so it is at most $B$.

**($\Leftarrow$) If our instance is a yes-instance, so is the TSP instance.** Take a feasible solution of duration at most $B$. Because $k=1$, it is one route $(0,\pi_1,\dots,\pi_n,0)$ visiting every customer exactly once, so $(0,\pi_1,\dots,\pi_n)$ is a tour of all $m$ cities. By the inequality above, its cost is at most $D(R)\le B$.

So $\Delta\text{-TSP-D}\le_p\text{TD-CVRP-TW-D}$, and **TD-CVRP-TW-D is NP-hard**.

## X2.5 What the reduction tells us

- **The basic version is already NP-hard.** The instance built above has no binding time windows, no service times and a single slot, so TD-CVRP (the basic version) is NP-hard. The advanced constraints cannot make the problem easier, because the basic version is a special case of the advanced one.
- **The problem is strongly NP-hard.** Starting from TSP instances with costs in $\{1,2\}$, every number in our instance is at most $2m$. Hence the problem stays NP-hard even when all numbers are small, and no pseudo-polynomial algorithm exists unless P = NP (Garey & Johnson, 1979).
- **The result does not depend on our modelling choices.** The reduction uses one slot and constant speeds, so it holds whether the departure time from the depot is fixed or free (A9), and with either the departure-slot rule of the ILP or the exact Ichoua model (A12).

## X2.6 Even finding a feasible solution is NP-hard

For the CVRP alone, a feasible solution is easy to find when trucks are unlimited: one truck per customer. In our problem, the fleet size $k$ and the horizon $T$ are fixed, and then even **feasibility** is NP-complete.

- **Fleet size and capacity (Bin Packing).** Bin Packing asks whether items of sizes $w_1,\dots,w_n$ fit into $k$ bins of capacity $Q$, and it is strongly NP-complete (Garey & Johnson, 1979, problem SR1). Build an instance with one customer per item ($q_i=w_i$), the same $k$ and $Q$, all travel times equal to 1, $s_i=0$, $a_i=0$, $b_i=T$ and $T=n+1$. Any route of at most $n$ customers takes at most $n+1=T$ minutes, so time never binds. A feasible set of routes exists exactly when the items fit into $k$ bins.
- **Horizon and time windows.** In the reduction of X2.3, replace the horizon by $T=B$. The single route is then feasible exactly when the tour costs at most $B$, so deciding feasibility is as hard as the TSP. Savelsbergh (1985) proved the same result for the TSP with time windows: finding a feasible solution is strongly NP-complete.

As a consequence, unless P = NP, no polynomial-time algorithm can guarantee to return a feasible solution whenever one exists, and so no polynomial-time algorithm has a guaranteed approximation ratio. The solution method will have to deal with routes that break capacity or windows during the search.

# X3 – NP membership and conclusion

## X3.1 TD-CVRP-TW-D is in NP

A problem is in NP if every yes-instance has a certificate of polynomial size that can be checked in polynomial time.

**Certificate.** The list of at most $k$ routes, each given as the ordered list of its customers. Its size is $O(n\log n)$ bits.

**Verification.** For each route $R_\ell=(0,\pi_1,\dots,\pi_{m_\ell},0)$:
1. Check that every customer of $C$ appears in exactly one route and that there are at most $k$ routes: $O(n)$.
2. Check that the total demand of each route is at most $Q$: $O(n)$.
3. Compute the **earliest schedule**: leave the depot at $t=0$; at each customer $j$ reached from $i$, set $r_j=\alpha_{ij}(t_i)$, $u_j=\max(r_j,a_j)$, check $u_j\le b_j$, then set $t_j=u_j+s_j$. At the end, check that the return time $\alpha_{\pi_{m_\ell}0}(t_{\pi_{m_\ell}})$ is at most $T$.
4. Check that the sum of the return times is at most $B$.

**Why the earliest schedule is enough.** Under FIFO (A6), $\alpha_{ij}(t)$ is non-decreasing in $t$, and so are $\max(\cdot,a_j)$ and $+s_j$. Their composition is non-decreasing, so leaving as early as possible never makes a later arrival, service start or return time larger. If some schedule of these routes respects all windows and has total duration at most $B$, the earliest schedule does too.

**Why each step is polynomial.**
- *Travel times.* $\alpha_{ij}(t)$ is an earliest-arrival time in $G$. Under FIFO, it is computed by Dijkstra's algorithm adapted to time-dependent arcs (Dreyfus, 1969; Kaufman & Smith, 1993), which evaluates each arc once and runs in $O(\lvert A\rvert(K+\log\lvert V\rvert))$ time: one arc evaluation $\tau_a(t)$ in the Ichoua model walks through at most $K$ slots, so it costs $O(K)$.
- *Numbers.* All computed times are rationals obtained from the input by polynomially many additions, multiplications and divisions, so their binary size stays polynomial.

Step 3 makes $n+k$ such computations, so the whole check runs in $O\big((n+k)\,\lvert A\rvert(K+\log\lvert V\rvert)\big)$ time and **TD-CVRP-TW-D is in NP**.

**The ILP's travel-time rule.** With the departure-slot rule of the ILP (A12), leaving later can occasionally arrive earlier at a slot boundary, so FIFO may fail. The certificate then also gives the departure slot of each customer (the values $z^{s}_i$ of the ILP), and the verifier leaves at $t_i=\max(u_i+s_i,\beta_{s-1})$ and checks $t_i<\beta_s$. Inside a slot the travel time is constant, so leaving later in the same slot never helps. The check stays polynomial.

*Note:* membership for a **free** depot departure time (the planned refinement of A9) would need the departure times in the certificate, together with a proof that optimal departure times have polynomial size. We leave this for the final deliverable.

## X3.2 Conclusion

| Version | Complexity | Proof |
|---|---|---|
| TD-CVRP-TW-D (decision, advanced) | **NP-complete**, strongly | X2 (NP-hard) + X3.1 (in NP) |
| TD-CVRP-D (decision, basic) | **NP-complete**, strongly | same reduction, no windows used |
| TD-CVRP-TW and TD-CVRP (optimization) | **NP-hard** | an optimal solution answers the decision version |
| Finding any feasible solution ($k$ and $T$ fixed) | **NP-complete** | X2.6 (Bin Packing; TSP with $T=B$) |

**Consequences for the project.**
- Unless P = NP, no algorithm solves every instance optimally in polynomial time. The solve time of the ILP grows exponentially in the worst case, and even for the plain CVRP, state-of-the-art exact methods are limited to a few hundred customers (Toth & Vigo, 2014).
- Our target instances have several thousand customers. The ILP will therefore be used on small instances to obtain optimal solutions and bounds, and the large instances will need a heuristic or metaheuristic method (next deliverable).
- Since feasibility itself is hard when the fleet and the horizon are tight, the experiments should also measure how often the method finds a feasible solution, not only its cost.

# References for this section

- Dabia, S., Ropke, S., van Woensel, T., & de Kok, T. (2013). Branch and price for the time-dependent vehicle routing problem with time windows. *Transportation Science*, 47(3), 380–396.
- Dantzig, G. B., & Ramser, J. H. (1959). The truck dispatching problem. *Management Science*, 6(1), 80–91.
- Dreyfus, S. E. (1969). An appraisal of some shortest-path algorithms. *Operations Research*, 17(3), 395–412.
- Garey, M. R., & Johnson, D. S. (1979). *Computers and Intractability: A Guide to the Theory of NP-Completeness*. W. H. Freeman.
- Gendreau, M., Ghiani, G., & Guerriero, E. (2015). Time-dependent routing problems: A review. *Computers & Operations Research*, 64, 189–197.
- Ichoua, S., Gendreau, M., & Potvin, J.-Y. (2003). Vehicle dispatching with time-dependent travel times. *European Journal of Operational Research*, 144(2), 379–396.
- Karp, R. M. (1972). Reducibility among combinatorial problems. In R. E. Miller & J. W. Thatcher (Eds.), *Complexity of Computer Computations* (pp. 85–103). Plenum Press.
- Kaufman, D. E., & Smith, R. L. (1993). Fastest paths in time-dependent networks for intelligent vehicle-highway systems application. *IVHS Journal*, 1(1), 1–11.
- Kulkarni, R. V., & Bhave, P. R. (1985). Integer programming formulations of vehicle routing problems. *European Journal of Operational Research*, 20(1), 58–67.
- Malandraki, C., & Daskin, M. S. (1992). Time dependent vehicle routing problems: Formulations, properties and heuristic algorithms. *Transportation Science*, 26(3), 185–200.
- Miller, C. E., Tucker, A. W., & Zemlin, R. A. (1960). Integer programming formulation of traveling salesman problems. *Journal of the ACM*, 7(4), 326–329.
- Papadimitriou, C. H., & Yannakakis, M. (1993). The traveling salesman problem with distances one and two. *Mathematics of Operations Research*, 18(1), 1–11.
- Savelsbergh, M. W. P. (1985). Local search in routing problems with time windows. *Annals of Operations Research*, 4(1), 285–305.
- Solomon, M. M. (1987). Algorithms for the vehicle routing and scheduling problems with time window constraints. *Operations Research*, 35(2), 254–265.
- Toth, P., & Vigo, D. (Eds.). (2014). *Vehicle Routing: Problems, Methods, and Applications* (2nd ed.). SIAM.
