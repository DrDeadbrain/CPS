from intersection import nx, Intersection, Car
from typing import List

"""
toggle traffic light based on g_time
"""


def tl_global_const(G: nx.DiGraph, all_intersections: List[Intersection], all_cars: List[Car], g_time: int) -> None:
    if g_time % 15 < 1:
        for inter in all_intersections:
            inter.state_we = not inter.state_we
            inter.state_ns = not inter.state_ns
