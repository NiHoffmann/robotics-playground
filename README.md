# robotics-playground
A playground of robotics concepts in the fields of - self-organizing systems, collective robotics, evolutionary robotics, and more. Everything here runs in simulation, so feel free to clone it, poke around, and play with it yourself.

**To give you an idea what this project collection is about** - Here we have a simulation with focus on Anti-Agent behaviour simple. Agents with no communication, only local sensing, self-organizing into clusters (and a small fraction of agents working *against* clustering can, counterintuitively, help form even larger ones):

| No anti-agents | 10% anti-agents |
|:---:|:---:|
| <img src="CollectiveRobotics/wood-chip-clustering/animation/clustering_no_anti_agents.gif" width="400"> | <img src="CollectiveRobotics/wood-chip-clustering/animation/clustering_with_anti_agents.gif" width="400"> |
| objects settle into many small, separate clusters | a small fraction of agents working "against" clustering locally ends up helping consolidate the objects into fewer, larger clusters |


Have a look at the Project: [wood-chip clustering](https://github.com/NiHoffmann/robotics-playground/tree/main/CollectiveRobotics/wood-chip-clustering).

## Projects
- [Collective Robotics](https://github.com/NiHoffmann/robotics-playground/tree/main/CollectiveRobotics)
  - [Firefly Synchronization](https://github.com/NiHoffmann/robotics-playground/tree/main/CollectiveRobotics/firefly-synchronization) - spontaneous sync from purely local coupling
  - [Locust Alignment](https://github.com/NiHoffmann/robotics-playground/tree/main/Self-Organizing%20Systems/locust-alignment) - swarm direction consensus, plus an empirical transition-probability model
  - [Wood Chip Clustering](https://github.com/NiHoffmann/robotics-playground/tree/main/CollectiveRobotics/wood-chip-clustering) - ant-aggregation clustering, and how "anti-agents" can improve it
