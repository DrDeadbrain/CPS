import random
from intersection import *
import time


def car_generator(intersections: List[Intersection], G: nx.DiGraph, col: int = 2, row: int = -1,
                  max_dist: int = 5):
    row = col if row == -1 else row

    ini_fi_points = [i for i in range(0, col)]
    ini_fi_points.extend([i * col for i in range(1, row - 1)])
    ini_fi_points.extend([(i + 1) * col - 1 for i in range(1, row - 1)])
    ini_fi_points.extend([i for i in range(col * (row - 1), col * row)])

    num_init_points = len(ini_fi_points)

    while True:
        inf = random.sample(range(0, num_init_points), 2)
        ini = ini_fi_points[inf[0]]
        fi = ini_fi_points[inf[1]]
        path = nx.shortest_path(G, intersections[ini], intersections[fi])

        if ini < col:
            destination = intersections[ini].queue_north
        elif col * (row - 1) <= ini < col * row:
            destination = intersections[ini].queue_south
        elif ini in [i * col for i in range(1, row - 1)]:
            destination = intersections[ini].queue_west
        else:
            destination = intersections[ini].queue_east

        Car(random.randint(0, max_dist), destination, path)
        time.sleep(0.75)


def car_generator_rushhour(intersections: List[Intersection], G: nx.DiGraph, col: int = 2, row: int = -1,
                           max_dist: int = 5):
    row = col if row == -1 else row

    ini_fi_points = [i for i in range(0, col)]
    ini_fi_points.extend([i * col for i in range(1, row - 1)])
    ini_fi_points.extend([(i + 1) * col - 1 for i in range(1, row - 1)])
    ini_fi_points.extend([i for i in range(col * (row - 1), col * row)])

    num_init_points = len(ini_fi_points)

    while True:
        inf = [1, 7]
        ini = ini_fi_points[inf[0]]
        fi = ini_fi_points[inf[1]]
        path = nx.shortest_path(G, intersections[ini], intersections[fi])

        if ini < col:
            destination = intersections[ini].queue_north
        elif col * (row - 1) <= ini < col * row:
            destination = intersections[ini].queue_south
        elif ini in [i * col for i in range(1, row - 1)]:
            destination = intersections[ini].queue_west
        else:
            destination = intersections[ini].queue_east

        Car(random.randint(0, max_dist), destination, path)
        time.sleep(0.75)


def generate_node(col: int = 2, row: int = -1, red_prob: float = 0.5) -> List[Intersection]:
    # TODO: remove random red/ green light , make var for green light accesible
    row = col if row == -1 else row
    red = True if random.random() > red_prob else False
    return [Intersection(red, not red) for i in range(col * row)]


def generate_edge(intersections: list, col: int = 2, row: int = -1, len_lb: int = 10, len_ub: int = 10) -> nx.DiGraph:
    row = col if row == -1 else row
    hori_len = [random.randint(len_lb, len_ub) for i in range(0, col - 1)]
    verti_len = [random.randint(len_lb, len_ub) for i in range(0, row - 1)]

    graph = nx.DiGraph()

    for i in range(col * row):
        if (i + 1) % col == 0 and i // col == row - 1:
            pass
        elif col - i % col == 1:
            # rightmost
            graph.add_edge(intersections[i], intersections[i + col], length=verti_len[i // col],
                           dest=intersections[i + col].queue_north)
            graph.add_edge(intersections[i + col], intersections[i],
                           length=verti_len[i // col], dest=intersections[i].queue_south)
        elif i // col == row - 1:
            # bottom
            graph.add_edge(intersections[i], intersections[i + 1],
                           length=hori_len[i % col], dest=intersections[i + 1].queue_west)
            graph.add_edge(intersections[i + 1], intersections[i],
                           length=hori_len[i % col], dest=intersections[i].queue_east)
        else:
            graph.add_edge(intersections[i], intersections[i + 1],
                           length=hori_len[i % col], dest=intersections[i + 1].queue_west)
            graph.add_edge(intersections[i + 1], intersections[i],
                           length=hori_len[i % col], dest=intersections[i].queue_east)
            graph.add_edge(intersections[i], intersections[i + col], length=verti_len[i // col],
                           dest=intersections[i + col].queue_north)
            graph.add_edge(intersections[i + col], intersections[i],
                           length=verti_len[i // col], dest=intersections[i].queue_south)
    return graph
