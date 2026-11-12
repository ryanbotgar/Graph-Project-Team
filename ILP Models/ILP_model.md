## Integer Linear Programming model

All symbols follow the shared notation sheet (`notations.md`, section 6).

### Sets and parameters

| Symbol | Meaning |
|---|---|
| $C=\{1,\dots,n\}$ | customers |
| $0$ | depot, as the **start** of a route |
| $n+1$ | copy of the depot, as the **end** of a route |
| $N=C\cup\{0\}$ | possible origins of an arc |
| $N^{+}=C\cup\{n+1\}$ | possible destinations of an arc |
| $\{1,\dots,K\}$, $s$ | time slots, slot $s=[\beta_{s-1},\beta_s)$, with $\beta_0=0$ and $\beta_K=T$ |
| $\tau^{s}_{ij}$ | travel time from $i$ to $j$ when **leaving $i$ during slot $s$**: shortest-path time in $G$ with the slot-$s$ speeds, $\tau^{s}_{ij}=\min_{P:\,i\to j}\sum_{a\in P} d_a/v^{s}_a$; $\tau^{s}_{i,n+1}=\tau^{s}_{i0}$ |
| $q_i$, $s_i$, $[a_i,b_i]$ | demand, service time, time window of customer $i$ |
| $k$, $Q$ | number of trucks, capacity of each truck |
| $T$ | planning horizon: every truck must be back at the depot by $T$ |
| $\varepsilon>0$ | time resolution (e.g. 1 second), used to make slots half-open |
| $M_{ij}=T+\max_s\tau^{s}_{ij}$, $M_i=T+\max_s\tau^{s}_{i0}$ | big-M constants, large enough to deactivate (C8) and (C10) |

**Modelling choices for this version** (assumptions A9 and A12 in C2.3):
- Every truck leaves the depot at time $0$. The route duration is then the return time, so the objective is the sum of return times.
- Travel time is fixed by the slot in which the truck **leaves** $i$ (departure-slot approximation). The exact travel-time model of Ichoua et al. (2003), where the speed changes when a slot boundary is crossed, will be used by the heuristic.

### Decision variables

| Variable | Domain | Meaning |
|---|---|---|
| $x_{ij}$, $i\in N$, $j\in N^{+}$, $i\ne j$ | $\{0,1\}$ | 1 if some truck drives directly from $i$ to $j$ (the arc $(0,n+1)$ is not defined) |
| $z^{s}_{i}$, $i\in C$, $s\in\{1,\dots,K\}$ | $\{0,1\}$ | 1 if the truck **leaves** $i$ during slot $s$ |
| $r_i$ | $\ge 0$ | arrival time at customer $i$ |
| $u_i$ | $[a_i,b_i]$ | start of service at $i$ |
| $t_i$ | $[0,T)$ | departure time from $i$ |
| $L_i$ | $[q_i,Q]$ | cumulative load delivered on the route up to and including $i$ |
| $f_i$ | $[0,T]$ | return time to the depot **if $i$ is the last customer of its route**, 0 otherwise |

Waiting time at $i$ is $w_i=u_i-r_i\ge0$.

### Objective

$$
\min \sum_{i\in C} f_i \qquad (O)
$$

Only the last customer of each route has $f_i>0$, so (O) is the sum of the return times. Since every route leaves the depot at time 0, this is the total duration of the routes (A10).

### Constraints
**Routing structure (basic)**

$$
\sum_{i\in N\setminus\{j\}}x_{ij}=1\quad\forall j\in C \qquad (C1)
$$

$$
\sum_{h\in N^{+}\setminus\{j\}}x_{jh}=1\quad\forall j\in C \qquad (C2)
$$

$$
\sum_{j\in C}x_{0j}\le k \qquad (C3)
$$

(C1)–(C2): every customer has exactly one predecessor and one successor, i.e. is visited once. (C3): at most $k$ routes leave the depot. Flow conservation at the depot is implied: the number of arcs entering $n+1$ equals the number leaving $0$.

**Capacity and subtour elimination (basic)**

$$
L_j\ \ge\ L_i+q_j-Q\,(1-x_{ij})\quad\forall i,j\in C,\ i\ne j,\qquad q_j\le L_j\le Q \qquad (C4)
$$

If $j$ follows $i$, the load grows by $q_j$; otherwise the constraint is slack (because $L_i\le Q$). Since $L_j\ge q_j$, the first customer of a route needs no special case.

(C4) is the capacity version of the Miller–Tucker–Zemlin constraints (Miller et al., 1960; Kulkarni & Bhave, 1985) and it also **eliminates subtours**. Suppose $x$ contains a cycle $i_1\to i_2\to\dots\to i_m\to i_1$ made only of customers. Adding (C4) along the cycle gives $0\ge\sum_{p=1}^{m}q_{i_p}>0$, because every $q_i>0$ (A4), which is impossible. So every chain of customers must start at $0$ and end at $n+1$. The time constraints (C8) eliminate subtours in the same way whenever travel times are positive.

**Time-dependent travel (basic)**

$$
\sum_{s=1}^{K}z^{s}_{i}=1\quad\forall i\in C \qquad (C5a)
$$

$$
\sum_{s=1}^{K}\beta_{s-1}z^{s}_{i}\ \le\ t_i\ \le\ \sum_{s=1}^{K}(\beta_s-\varepsilon)\,z^{s}_{i}\quad\forall i\in C \qquad (C5b)
$$

$$
t_i\ \ge\ u_i+s_i\quad\forall i\in C \qquad (C6)
$$

$$
r_j\ \ge\ \tau^{1}_{0j}\,x_{0j}\quad\forall j\in C \qquad (C7)
$$

$$
r_j\ \ge\ t_i+\sum_{s=1}^{K}\tau^{s}_{ij}\,z^{s}_{i}-M_{ij}(1-x_{ij})\quad\forall i,j\in C,\ i\ne j \qquad (C8)
$$

(C5) selects the slot of departure; $\varepsilon$ makes slots half-open and removes the ambiguity at slot boundaries. (C6): a truck leaves after finishing the service. (C7): the truck leaves the depot at time 0, hence in slot 1. (C8): arrival at $j$ is at least departure time plus the travel time of the slot of departure. The product $\tau^{s}_{ij}\,z^{s}_{i}$ is **linear** because $\tau^{s}_{ij}$ is a constant. Because $t_i$ (departure) and not the arrival is used, waiting before leaving is allowed, so the model stays valid even if the departure-slot approximation breaks FIFO at a slot boundary.

**Time windows and waiting (advanced)**

$$
u_i\ \ge\ r_i,\qquad a_i\le u_i\le b_i\quad\forall i\in C \qquad (C9)
$$

$u_i\ge r_i$ and $u_i\ge a_i$ let the truck **wait** until the window opens; $u_i\le b_i$ **forbids** serving after the window closes. For the basic version, set $a_i=0$ and $b_i=T$.

**Return to the depot and horizon**

$$
f_i\ \ge\ t_i+\sum_{s=1}^{K}\tau^{s}_{i0}\,z^{s}_{i}-M_i\,(1-x_{i,n+1}),\qquad f_i\le T\,x_{i,n+1}\quad\forall i\in C \qquad (C10)
$$

If $i$ is the last customer, $f_i$ is at least the return time and at most $T$ (A11); otherwise $f_i=0$.

### Full model (summary)

$$
\begin{aligned}
(O)\quad & \min\ \textstyle\sum_{i\in C} f_i\\
(C1)\quad & \textstyle\sum_{i\in N\setminus\{j\}}x_{ij}=1 \quad \forall j\in C\\
(C2)\quad & \textstyle\sum_{h\in N^{+}\setminus\{j\}}x_{jh}=1 \quad \forall j\in C\\
(C3)\quad & \textstyle\sum_{j\in C}x_{0j}\le k\\
(C4)\quad & L_j\ge L_i+q_j-Q(1-x_{ij}) \quad \forall i,j\in C,\ i\ne j\\
(C5a)\quad & \textstyle\sum_{s}z^{s}_{i}=1 \quad \forall i\in C\\
(C5b)\quad & \textstyle\sum_{s}\beta_{s-1}z^{s}_{i}\le t_i\le\sum_{s}(\beta_s-\varepsilon)z^{s}_{i} \quad \forall i\in C\\
(C6)\quad & t_i\ge u_i+s_i \quad \forall i\in C\\
(C7)\quad & r_j\ge\tau^{1}_{0j}x_{0j} \quad \forall j\in C\\
(C8)\quad & r_j\ge t_i+\textstyle\sum_{s}\tau^{s}_{ij}z^{s}_{i}-M_{ij}(1-x_{ij}) \quad \forall i,j\in C,\ i\ne j\\
(C9)\quad & u_i\ge r_i,\ \ a_i\le u_i\le b_i \quad \forall i\in C\\
(C10)\quad & f_i\ge t_i+\textstyle\sum_{s}\tau^{s}_{i0}z^{s}_{i}-M_i(1-x_{i,n+1}),\ \ f_i\le T\,x_{i,n+1} \quad \forall i\in C\\
& x_{ij}\in\{0,1\},\ z^{s}_{i}\in\{0,1\},\ r_i\ge0,\ t_i\in[0,T),\ q_i\le L_i\le Q,\ f_i\ge0
\end{aligned}
$$

**Size of the model.** $n(n+1)$ binary variables $x_{ij}$, $nK$ binary variables $z^{s}_{i}$, $5n$ continuous variables, and $2n(n-1)+O(n)$ constraints, dominated by (C4) and (C8). For $n=1000$ customers this is already about two million constraints with weak big-M relaxations, which is why the ILP is only expected to solve small instances exactly (see the complexity section).
