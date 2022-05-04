from simulation import *

# create simulation
sim = Simulation()

# add some roads
sim.create_roads([
    ((300, 98), (0, 98)),

])

# start the simulation
win = Window(sim)
win.offset = (-150, -110)
win.simulate()
