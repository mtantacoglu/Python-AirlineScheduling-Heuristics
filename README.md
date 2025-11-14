# Python-AirlineScheduling-Heuristics
This repository includes the implementation of three heuristic approaches developed for the Integrated Schedule Design and Fleet Assignment Problem (ISDFAP) in a single-hub, two-leg hub-and-spoke network. These heuristics aim to balance passenger demand, waiting time, seat availability, and aircraft operational constraints when constructing inbound and outbound flight schedules.

1. Heuristic 1 — Minimum Passenger Waiting Time

This heuristic assigns passengers based purely on minimizing waiting time between connecting flights. It does not consider seat capacity or aircraft-side constraints, serving as a baseline schedule optimized only for passenger time efficiency.

2. Heuristic 2 — Waiting Time + Seat Capacity Constraint

The second heuristic extends Heuristic 1 by adding seat availability constraints. Passenger assignments must respect aircraft capacity while still attempting to minimize waiting time. The study shows that including seat limits does not necessarily reduce total waiting time, but produces more realistic and operationally feasible schedules.

3. Heuristic 3 — Aircraft Buffer Time + Turnaround Constraints

The third heuristic incorporates aircraft buffer time and minimum stay (turnaround) requirements at the destination. This approach adjusts departure times and timetable structures to ensure feasible aircraft rotations. Its results demonstrate that schedule feasibility and passenger assignments depend heavily on buffer-time and turnaround constraints.

Related Publication
These heuristic approaches are part of a peer-reviewed research article that I authored:

Tacoglu, M., & Ornek, M. A. (2024). Heuristic methods for integrated incremental schedule design and fleet assignment problem for hub and spoke network.
International Journal of Sustainable Aviation. https://www.inderscienceonline.com/doi/abs/10.1504/IJSA.2024.140654

If you use these heuristics, algorithms, or code in your work, please reference this publication.
