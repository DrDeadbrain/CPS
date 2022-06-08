import random
import networkx as nx
import numpy as np
from typing import *
import pygame

cargroup = pygame.sprite.Group()


# python json to list pythonexamples

class Car(pygame.sprite.Sprite):
    def __init__(self, init_distance: Union[int, float], init_dest: list, path: list, emergency: bool, rush: bool, id=0):
        """
            Attributes: own time, previous intersection node,
                        current intersection queue, length of the edge it is on
                        sequence of the nodes it has to reach,
                        whether it is in the waiting queue/pass in progress queue,
                        the time it passes through a intersection, whether it has arrived.
            @param init_distance: The length of the edge it is on
            @param init_dest: The current intersection queue
            @param path: A list containing the reference to intersections that this car will pass
        """
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.emergency = emergency
        self.rush = rush
        self.waiting_time: Union[int, float] = 0  # waiting time
        self.next_inter: List[Car] = init_dest  # reference to next intersection queue
        self.prev_inter: Optional[object] = None  # reference to prev intersection queue
        self.dist_to_intersection = init_distance  # distance to next intersection
        self.path = path
        self.crossing_time = 2  # time required to pass intersection
        self.updated = False  # whether status is already updated by update_intersection method
        self.arrived = False  # has the car reached its destination

        cargroup.add(self)


class Intersection:
    def __init__(self, state_ns: bool, state_we: bool, id=0):
        """
            Attributes: waiting queue, pass in progress queue, light signal boolean
            @param state_ns: A boolean which determine if it is green light for the north-south direction
            @param state_we: A boolean which determine if it is green light for the west-east direction
        """
        self.id = id + 1
        self.queue_north: List[Car] = []  # queue on the north side
        self.queue_south: List[Car] = []  # queue on the south side
        self.queue_east: List[Car] = []  # queue on the east side
        self.queue_west: List[Car] = []  # queue on the west side
        self.queue_all = [self.queue_north, self.queue_south,
                          self.queue_west, self.queue_east]  # all queues
        # pass in progress queue (cars that are currently passing the intersection)
        self.pass_in_prog: Dict[Car, Union[int, float]] = {}
        self.cycle_time = 50
        self.time_count = 0
        self.state_ns = state_ns
        self.state_we = state_we
        # TODO: separate cycle time für die phasen


class World:
    def __init__(self, Graph: nx.DiGraph, all_intersections: List[Intersection], cargroup):
        self.G = Graph
        self.all_intersections = all_intersections
        self.cargroup = cargroup
        self.time: Union[int, float] = 0

    def update_intersection(self, time: Union[int, float]):
        """
            @param time: global time stamp
            @return: None
        """
        for intersection in self.all_intersections:
            # update pass in progress (assuming it has unlimited capacity)
            for car in list(intersection.pass_in_prog.keys()):
                # increase car time spent in intersection
                intersection.pass_in_prog[car] += time
                car.updated = True

                # if time spent > crossing_time -> car has passed intersection
                if intersection.pass_in_prog[car] >= car.crossing_time:
                    time_at_intersection = intersection.pass_in_prog.pop(car)

                    # if the car has not reached it's final destination:
                    # place it on way to next intersection
                    # passing previous intersection
                    car.prev_inter = car.path.pop(0)
                    if len(car.path) > 0:
                        # get edge from past to next intersection
                        edge = self.G[intersection][car.path[0]]

                        # update distance to next intersection
                        car.dist_to_intersection = edge['length'] - time_at_intersection + car.crossing_time

                        # update reference to next intersection queue
                        car.next_inter = edge['dest']
                    else:
                        car.arrived = True

            # update queue of cars waiting to pass the intersection
            # if queue_ns and light is green
            if intersection.state_ns:
                for queue in intersection.queue_all[:2]:
                    if len(queue) == 0:
                        continue

                    # compute each cars distance to the intersection
                    for car in queue:
                        car.dist_to_intersection -= time
                        car.updated = True

                        # negative distance -> car arrived at next intersection
                        if car.dist_to_intersection <= 0:
                            # add car to pass in prog dict
                            intersection.pass_in_prog[car] = -car.dist_to_intersection
                            car.dist_to_intersection = 0

                    # remove cars that already in pass_in_prog
                    queue[:] = [car for car in queue if car.dist_to_intersection > 0]

            # if the traffic light is not green -> make sure that cars will not acquire negative
            # distance_to_next_inter value
            else:
                for queue in intersection.queue_all[:2]:
                    if len(queue) == 0:
                        continue

                    dist_move_back: Union[int, float] = 0
                    front_car = queue[-1]

                    # if front car passes stop line
                    if front_car.dist_to_intersection < 0:
                        dist_move_back = -front_car.dist_to_intersection

                        # move it back
                        front_car.dist_to_intersection = 0

                    # shift all other cars by that distance
                    for car in queue[:len(queue) - 1]:
                        car.dist_to_intersection += dist_move_back

            # if queue_we and green light:
            if intersection.state_we:
                for queue in intersection.queue_all[2:]:
                    if len(queue) == 0:
                        continue

                    for car in queue:
                        car.dist_to_intersection -= time
                        car.updated = True

                        if car.dist_to_intersection <= 0:
                            intersection.pass_in_prog[car] = -car.dist_to_intersection
                            car.dist_to_intersection = 0

                    queue[:] = [car for car in queue if car.dist_to_intersection > 0]

            else:
                for queue in intersection.queue_all[2:]:
                    if len(queue) == 0:
                        continue

                    dist_move_back = 0
                    front_car = queue[-1]
                    if front_car.dist_to_intersection < 0:
                        dist_move_back = -front_car.dist_to_intersection
                        front_car.dist_to_intersection = 0
                    for car in queue[:len(queue) - 1]:
                        car.dist_to_intersection -= dist_move_back

            for queue in intersection.queue_all:
                for car in queue:
                    car.updated = True

    def update_cars(self, time: Union[int, float]) -> bool:
        """
            @param time: the global time step
            @return:
            Assumption: All cars' velocities are 1
                        The length of each car is 1
                        The length of the street is measured using car length
        """
        all_arrived = True
        for car in self.cargroup:
            if car.arrived:
                continue

            all_arrived = False
            # if car has not been updated by update_intersection
            # -> car is not in waiting or pass_in_prog queue
            if not car.updated:
                # car is on the way to next queue
                # update distance by amount of time
                car.dist_to_intersection -= time

                # if car distance to next intersection is < length of queue
                # -> car has reached tail of the queue -> append car
                if car.dist_to_intersection <= len(car.next_inter) and car not in car.next_inter:
                    car.next_inter.append(car)

            # clear flag for next update
            car.updated = False
            car.waiting_time += time

        return all_arrived

    def update_traffic_light(self):
        for inter in self.all_intersections:
            if inter.time_count == inter.cycle_time:
                inter.state_we = not inter.state_we
                inter.state_ns = not inter.state_ns
                inter.time_count = 0
            else:
                inter.time_count += 1

    def update_all(self, time: Union[int, float]) -> bool:
        all_arrived = self.update_cars(time)
        self.update_intersection(time)
        self.time += time
        self.update_traffic_light()
        return all_arrived

    def stats(self):
        wait_times = [car.waiting_time for car in self.cargroup]
        total_wait_time = sum(wait_times)
        avg_wait_time = total_wait_time / len(self.cargroup)
        std_wait_time = np.std(wait_times)
        max_wait_time = max(wait_times)

        stat_str = "Total waiting time {}\nAverage waiting time {}\nMaximum waiting time {}\nstd. of waiting time {}\n".format(
            total_wait_time, avg_wait_time,
            max_wait_time, std_wait_time)
        print(stat_str)

    def get_avg_waiting_time(self):
        wait_times = [car.waiting_time for car in self.cargroup]
        total_wait_time = sum(wait_times)
        if len(self.cargroup) == 0:
            avg_wait_time = 0
        else:
            avg_wait_time = total_wait_time / len(self.cargroup)
        return avg_wait_time

    def get_max_waiting_time(self):
        wait_times = [car.waiting_time for car in self.cargroup]
        if len(self.cargroup) == 0:
            max_wait_time = 0
        else:
            max_wait_time = max(wait_times)
        return max_wait_time

    def get_emergency_waiting_time(self):
        waiting_time = 0
        for car in self.cargroup:
            if car.emergency:
                waiting_time = car.waiting_time
        return waiting_time

    def get_emergency_car_path(self):
        path = []
        for car in self.cargroup:
            if car.emergency:
                path = car.path
        return path

    def get_rushhour_car_path(self):
        path = []
        for car in self.cargroup:
            if car.rush:
                path = car.path
        return path

    def get_curr_intersection(self, id):
        curr_intersection = -1
        for i in self.all_intersections:
           if i.id == id:
               curr_intersection = i
        return curr_intersection

        # TODO: send values via MQTT to dashboard + add max cars per crossing
