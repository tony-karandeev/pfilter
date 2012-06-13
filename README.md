pfilter
=======

Particle Filter algorithm implementation and testing

Particle Filter is used to estimate probability distribution 
of current state in Hidden Markov Models where state space 
is continuous. Density of discrete particles approximates 
probability distribution which is continuous function.


pfilter module
--------------
pfilter module gives universal Particle Filter implementation


robot module
--------------
robot module uses particle filter to localize robot named Paul 
in the maze. Paul is completely blind and the only two thing the knows 
on each step are:

1. Whether he ran into a wall or not. 

2. Distance to each beacon.


USAGE: python robot.py [PARTICLE_COUNT [BEACON_COUNT [SIGMA [MAZE_FILE]]]
