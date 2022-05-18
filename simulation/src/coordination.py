from intersection import Intersection, Car
from typing import *
import pygame


def get_location(light_crosses, intersections: List[Intersection], car: Car, column: int, row: int, car_length: int = 10,
                 max_dist: Union[int, float] = 10, screen_size_x: int = 800, screen_size_y: int = 800):
    try:
        location = [-1, -1]
        dis_betw_car = 2
        # find the crossroad location
        for count, node in enumerate(intersections):
            if node is car.path[0]:
                location[0] = count
                break
        # find the queue location
        for count, direction in enumerate(car.path[0].queue_all):
            if car.next_inter is direction:
                location[1] = count
                break
        print("Debug in car-coord:", location[0], location[1], car.path[0], car.arrived)

        # uses the cross to find the origin, the middle
        origin = pygame.Rect(light_crosses[location[0]].x + light_crosses[location[0]].width // 2 - car_length // 2,
                             light_crosses[location[0]].y + light_crosses[location[0]].height // 2 - car_length // 2, car_length,
                             car_length)
        # check if the car is in pass in progress
        if car in car.path[0].pass_in_prog:
            print("The car is passing in prog")
            print("the origin is", origin)
            return origin

        # find the location of the car if it is on one of the edges, the algo should be good
        # did not consider the not non-vertical/horizontal case
        if location[1] != -1:
            if location[1] == 0:
                # it is north
                if location[0] >= column:
                    dist_bw_two_cr = light_crosses[location[0]].y - light_crosses[location[0] - column].y - light_crosses[
                        location[0] - column].height
                    car_loc = dist_bw_two_cr * car.dist_to_intersection / max_dist  # car distance respect to the next crossroad
                    origin.y = light_crosses[location[0]].y - car_loc - car_length
                    return origin
                else:
                    # if the crossroad is on the bottommost
                    dist_bw_two_cr = light_crosses[location[0]].y - 0
                    car_loc = dist_bw_two_cr * car.dist_to_intersection / max_dist
                    origin.y = light_crosses[location[0]].y - car_loc - car_length
                    return origin
            elif location[1] == 1:
                # it is south
                if location[0] < len(light_crosses) - column:
                    dist_bw_two_cr = light_crosses[location[0] + column].y - light_crosses[location[0]].y - light_crosses[
                        location[0]].height
                    car_loc = dist_bw_two_cr * car.dist_to_intersection / max_dist  # car distance respect to the next crossroad
                    origin.y = light_crosses[location[0]].y + car_loc + light_crosses[
                        location[0]].height
                    return origin
                else:
                    # if the crossroad is on the bottommost
                    dist_bw_two_cr = screen_size_y - light_crosses[location[0]].y - light_crosses[location[0]].height
                    car_loc = dist_bw_two_cr * car.dist_to_intersection / max_dist  # car distance respect to the next crossroad
                    origin.y = light_crosses[location[0]].y + car_loc + light_crosses[
                        location[0]].height
                    return origin
            elif location[1] == 2:
                # it is west
                if location[0] % column != 0:
                    dist_bw_two_cr = light_crosses[location[0]].x - light_crosses[location[0] - 1].x - light_crosses[
                        location[0] - column].width
                    car_loc = dist_bw_two_cr * car.dist_to_intersection / max_dist  # car distance respect to the next crossroad
                    origin.x = light_crosses[location[0]].x - car_loc - car_length
                    return origin
                else:
                    # if the crossroad is on the leftmost
                    dist_bw_two_cr = light_crosses[location[0]].x - 0
                    car_loc = dist_bw_two_cr * car.dist_to_intersection / max_dist
                    origin.x = light_crosses[location[0]].x - car_loc - car_length
                    return origin
            elif location[1] == 3:
                # it is south
                if location[0] % column != location[0] - 1:
                    dist_bw_two_cr = light_crosses[location[0] + 1].x - light_crosses[location[0]].x - light_crosses[
                        location[0]].width
                    car_loc = dist_bw_two_cr * car.dist_to_intersection / max_dist  # car distance respect to the next crossroad
                    origin.x = light_crosses[location[0]].x + car_loc + light_crosses[
                        location[0]].width
                    return origin
                else:
                    # if the crossroad is on the bottommost
                    dist_bw_two_cr = screen_size_x - light_crosses[location[0]].x - light_crosses[location[0]].width
                    car_loc = dist_bw_two_cr * car.dist_to_intersection / max_dist  # car distance respect to the next crossroad
                    origin.x = light_crosses[location[0]].x + car_loc + light_crosses[
                        location[0]].width
                    return origin
        else:
            print("cant find which edge it is on")

    except IndexError:
        print("ACTION Index Error?")


if __name__ == "__main__":
    screen_sz = 800
