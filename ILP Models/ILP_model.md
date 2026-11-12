## Integer Linear Programming model

### Decision variables

| Variable | Domain | Meaning |
|---|---|---|
| $x_{ij}$, $(i,j)\in V^-\times V^+$, $i\ne j$ | $\{0,1\}$ | 1 if some truck drives directly from $i$ to $j$ (the arc $(0,n+1)$ is not defined) |
| $z_{ip}$, $i\in C$, $p\in P$ | $\{0,1\}$ | 1 if the truck **departs** from $i$ during slot $p$ |
| $A_i$ | $\ge 0$ | arrival time at customer $i$ |
| $S_i$ | $[a_i,b_i]$ | start of service at $i$ |
| $d_i$ | $[0,H)$ | departure time from $i$ (the depot departs at time 0) |
| $\ell_i$ | $[q_i,Q]$ | cumulative load delivered on the route up to and including $i$ |
| $E_i$ | $[0,T_{\max}]$ | return time to the depot **if $i$ is the last customer of its route**, 0 otherwise |

Waiting time at $i$ is $w_i=S_i-A_i\ge0$.

### Objective

$$
\min \sum_{i\in C} E_i \qquad (O)
$$

Only the last customer of each route has $E_i>0$, so (O) is the sum of the return times, i.e. the total duration (A4).

### Constraints
**Routing structure (basic)**

$$
\sum_{i\in V^-\setminus\{j\}}x_{ij}=1\quad\forall j\in C \qquad (C1)
$$

$$
\sum_{l\in V^+\setminus\{j\}}x_{jl}=1\quad\forall j\in C \qquad (C2)
$$

$$
\sum_{j\in C}x_{0j}\le k \qquad (C3)
$$

(C1)–(C2): every customer has exactly one predecessor and one successor, i.e. is visited once. (C3): at most $k$ routes leave the depot. Flow conservation at the depot is implied: the number of arcs entering $n+1$ equals the number leaving $0$.

**Capacity (basic)**

$$
\ell_j\ \ge\ \ell_i+q_j-Q\,(1-x_{ij})\quad\forall i,j\in C,\ i\ne j,\qquad q_j\le \ell_j\le Q \qquad (C4)
$$

If $j$ follows $i$, the load grows by $q_j$; otherwise the constraint is slack. Since $\ell_j\ge q_j$, the first customer of a route needs no special case.

**Time-dependent travel (basic)**

$$
\sum_{p\in P}z_{ip}=1\quad\forall i\in C \qquad (C5a)
$$

$$
\sum_{p}\theta_{p-1}z_{ip}\ \le\ d_i\ \le\ \sum_p(\theta_p-\varepsilon)\,z_{ip}\quad\forall i\in C \qquad (C5b)
$$

$$
d_i\ \ge\ S_i+s_i\quad\forall i\in C \qquad (C6)
$$

$$
A_j\ \ge\ \tau^{1}_{0j}\,x_{0j}\quad\forall j\in C \qquad (C7)
$$

$$
A_j\ \ge\ d_i+\sum_{p}\tau^{p}_{ij}\,z_{ip}-M_{ij}(1-x_{ij})\quad\forall i,j\in C,\ i\ne j \qquad (C8)
$$

(C5) selects the slot of departure; $\varepsilon>0$ is the time resolution, which makes slots half-open and removes the ambiguity at slot boundaries. (C6): a truck leaves after finishing the service. (C7): the truck leaves the depot at time 0, hence in slot 1. (C8): arrival at $j$ is at least departure time plus the travel time of the slot of departure. The product $\tau^p_{ij}\,z_{ip}$ is **linear** because $\tau^p_{ij}$ is a constant. Because $d_i$ and not the arrival is used, waiting before leaving is allowed, so the model stays valid without FIFO.

**Time windows and waiting (advanced)**

$$
S_i\ \ge\ A_i,\qquad a_i\le S_i\le b_i\quad\forall i\in C \qquad (C9)
$$

$S_i\ge A_i$ and $S_i\ge a_i$ let the truck **wait** until the window opens; $S_i\le b_i$ **forbids** serving after the window closes.

**Return to the depot and maximum duration**

$$
E_i\ \ge\ d_i+\sum_p\tau^p_{i,n+1}\,z_{ip}-M_i\,(1-x_{i,n+1}),\qquad E_i\le T_{\max}\,x_{i,n+1}\quad\forall i\in C \qquad (C10)
$$

If $i$ is the last customer, $E_i$ is at least the return time and at most $T_{\max}$; otherwise $E_i=0$.

Time windows and waiting (advanced)

$$S_i\ \ge\ A_i,\qquad a_i\le S_i\le b_i\quad\forall i\in C \qquad (C9)$$

$S_i\ge A_i$ and $S_i\ge a_i$ let the truck wait until the window opens; $S_i\le b_i$ forbids serving after the window closes.

Return to the depot and maximum duration

$$E_i\ \ge\ d_i+\sum_p\tau^p_{i,n+1}\,z_{ip}-M_i\,(1-x_{i,n+1}),\qquad E_i\le T_{\max}\,x_{i,n+1}\quad\forall i\in C \qquad (C10)$$

If $i$ is the last customer, $E_i$ is at least the return time and at most $T_{\max}$; otherwise $E_i=0$.
