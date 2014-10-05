mondrian
========

Experiment with Artificial Societies and basic city generation. Visual inspired by Piet Mondrian's Broadway Boogie Woogie

![](snapshot.jpg)

Cities are generated from simple street pattens. Houses and markets are derived from streets. Each agent is allocated to a house, and move randomly in the city. Agents increasse their health finding food (i.e. in markets). 

A Floyd algorithm ensures real-time to orient each agent within a graph automatically deduced from the city structure. During motion, agents used also a simple avoidance technique.
