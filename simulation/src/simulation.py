import json
import threading

import pygame
import paho.mqtt.client as mqtt

import coordination
import generator
from intersection import nx, World, Intersection, Car, cargroup
from policy import tl_global_const
from typing import *

import os
import time

pygame.init()

white = [255, 255, 255]
red = [255, 0, 0]
blue = [0, 0, 255]
yellow = [255, 255, 0]
dark_grey = [150, 150, 150]
black = [0, 0, 0]
green = [0, 255, 0]
pink = [255, 192, 203]
forest_green = [34, 139, 34]


try:
    os.environ["DISPLAY"]
except:
    os.environ["SDL_VIDEODRIVER"] = "dummy"


mqttAddr = os.getenv('MQTT_ADDR', 'localhost')
client = mqtt.Client("Simulation")
client.connect(host=mqttAddr, port=1883)
time.sleep(5)
client.loop_start()
print("Connected to MQTT broker: " + mqttAddr)


def create_intersection_crosses(row: int, column: int, cr_width: int, cr_height: int,
                                street_width_x: int, street_width_y: int) -> List[pygame.Rect]:
    """
    To get all the coordination of the crossroads in a list
    :return: a list contains all the crossroads coordinations
    """
    crosses = []
    for i in range(row):
        for j in range(column):
            crosses.append(pygame.Rect(
                street_width_x * (j + 1) + j * cr_width,
                street_width_y * (i + 1) + i * cr_height,
                cr_width, cr_height))
    return crosses


def create_streets(intersections: List[pygame.Rect], row: int, column: int,
                   screen_size_x: int, screen_size_y: int) -> List[pygame.Rect]:
    """
    To get all the coordination of the streets in a list.
    Use polygon to connect all adjacent crosses
    :return: a list contains all the streets coordinations
    """
    streets = []
    # draw all horizontal
    for inter_num in range(len(intersections)):
        if (inter_num + 1) % column == 1:
            # use polygon to draw all the leftmost sides of crossroads

            pointlist = [(0, intersections[inter_num].y),
                         (intersections[inter_num].x, intersections[inter_num].y),
                         (intersections[inter_num].x, intersections[inter_num].y +
                          intersections[inter_num].height),
                         (0, intersections[inter_num].y + intersections[inter_num].height)]
            streets.append(pygame.draw.polygon(screen, yellow, pointlist))

        if (inter_num + 1) % column == 0:
            # use polygon to draw all the rightmost side of crossroads

            pointlist = [(screen_size_x, intersections[inter_num].y),
                         (intersections[inter_num].x, intersections[inter_num].y),
                         (intersections[inter_num].x, intersections[inter_num].y +
                          intersections[inter_num].height),
                         (screen_size_x, intersections[inter_num].y + intersections[inter_num].height)]
            streets.append(pygame.draw.polygon(screen, yellow, pointlist))

        if (inter_num + 1) % column != 0:
            # use polygon to connect all horizontal crossroads inside

            pointlist = [(intersections[inter_num].x + intersections[inter_num].width, intersections[inter_num].y),
                         (intersections[inter_num + 1].x, intersections[inter_num + 1].y),
                         (intersections[inter_num + 1].x, intersections[inter_num +
                                                                        1].y + intersections[inter_num + 1].height),
                         (intersections[inter_num].x + intersections[inter_num].width,
                          intersections[inter_num].y + intersections[inter_num].height)]
            streets.append(pygame.draw.polygon(screen, yellow, pointlist))

    # draw all vertical
    for inter_num in range(len(intersections)):
        if inter_num < column:
            # use polygon to draw all the uppermost sides of crossroads

            pointlist = [(intersections[inter_num].x, 0),
                         (intersections[inter_num].x, intersections[inter_num].y),
                         (intersections[inter_num].x +
                          intersections[inter_num].width, intersections[inter_num].y),
                         (intersections[inter_num].x + intersections[inter_num].width, 0)]
            streets.append(pygame.draw.polygon(screen, yellow, pointlist))

        if inter_num >= column * (row - 1):
            # use polygon to draw all the lowermost sides of crossroads

            pointlist = [(intersections[inter_num].x, screen_size_y),
                         (intersections[inter_num].x, intersections[inter_num].y),
                         (intersections[inter_num].x +
                          intersections[inter_num].width, intersections[inter_num].y),
                         (intersections[inter_num].x + intersections[inter_num].width, screen_size_y)]
            streets.append(pygame.draw.polygon(screen, yellow, pointlist))

        if inter_num < column * (row - 1):
            # use polygon to connect all vertical crossroads inside

            pointlist = [(intersections[inter_num].x, intersections[inter_num].y + intersections[inter_num].height),
                         (intersections[inter_num].x + intersections[inter_num].width,
                          intersections[inter_num].y + intersections[inter_num].height),
                         (intersections[inter_num + column].x + intersections[inter_num + column].width,
                          intersections[inter_num + column].y),
                         (intersections[inter_num + column].x,
                          intersections[inter_num + column].y)]
            streets.append(pygame.draw.polygon(screen, yellow, pointlist))

    return streets


def draw_traffic_lights(screen: pygame.Surface, inter_rect: pygame.Rect, intersection: Intersection,
                        light_offset: List[int]) -> None:
    """
        Draw individual light according to each cross road status
        @return: None
    """
    light_ns = [light_offset[0], light_offset[1] // 3]
    light_we = [light_offset[0] // 3, light_offset[1]]
    if intersection.state_ns:
        screen.fill(green, inter_rect.inflate(*light_ns))
    else:
        screen.fill(red, inter_rect.inflate(*light_ns))
    if intersection.state_we:
        screen.fill(green, inter_rect.inflate(*light_we))
    else:
        screen.fill(red, inter_rect.inflate(*light_we))


def main(screen: pygame.Surface, column: int, row: int, G: nx.DiGraph, intersections: List[Intersection],
         light_crosses: List[pygame.Rect], streets: List[pygame.Rect],
         light_offset: List[int]) -> None:
    """
    main method
    entry point
    """
    pygame.init()
    font = pygame.font.SysFont('Arial', 10)
    clock = pygame.time.Clock()
    # all_cars = generator.generate_cars(inter_nodes, G, col=column, row=row, num_cars=60)
    world = World(G, intersections, cargroup, tl_global_const)

    while True:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            exit()
        screen.fill(forest_green)  # background
        for street in streets:
            screen.fill(dark_grey, street)  # streets
        for i, light_cross in enumerate(light_crosses):
            screen.fill(dark_grey, light_cross)  # intersections
            # draw lights according to state
            draw_traffic_lights(screen, light_cross, intersections[i], light_offset)

        for num, car in enumerate(cargroup, 1):  # all car locations
            if car.arrived:
                car.kill()
            else:
                location = coordination.get_location(light_crosses, intersections, car, column, row, car_length)

                car_num = font.render(str(num), True, [0, 0, 0])
                screen.fill(pink, location)
                screen.blit(car_num, location)

        pygame.display.flip()
        world.update_all(0.8)

        # remove_count = 0
        # while True:
        #     if car.arrived:
        #         car.kill()

        clock.tick(2)

        # Number of cars in queue per intersection
        queue_dict = {}
        id = 0
        for i in intersections:
            id += 1
            queue = 0
            for j in i.queue_all:
                queue += len(j)
            print("Intersection " + str(id) + ": " + str(queue))
            queue_dict[str(id)] = str(queue)
        json_string = json.dumps(queue_dict)
        print(json_string)
        client.publish(f"simulation/intersection_queues", json_string, qos=2)
        print("Avg. waiting time: {}".format(world.get_avg_waiting_time()))
        print("Max waiting time: {}".format(world.get_max_waiting_time()))
        avg_waiting_time = world.get_avg_waiting_time()
        client.publish(f"simulation/avg_waiting_time", avg_waiting_time, qos=2)
        max_waiting_time = world.get_max_waiting_time()
        client.publish(f"simulation/max_waiting_time", max_waiting_time, qos=2)
        print("*****************************")

    print("Simulation done")
    world.stats()

    while True:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            exit()


if __name__ == "__main__":
    """
    set params
    """

    screen_size_x = 800
    screen_size_y = 800
    column = 3
    row = 4
    screen = pygame.display.set_mode([screen_size_x, screen_size_y])
    inter_width = 50
    inter_height = 50
    light_offset = [-inter_width * 4 // 5, -inter_height * 4 // 5]
    street_width_x = (screen_size_x - column * inter_width) // (column + 1)
    street_width_y = (screen_size_y - row * inter_height) // (row + 1)
    car_length = 10
    car_num = 50

    # get location of intersections and streets in pygame.Rect -> ready to draw
    intersections = create_intersection_crosses(row, column, inter_width, inter_height, street_width_x, street_width_y)
    streets = create_streets(intersections, row, column, screen_size_x, screen_size_y)

    # generate intersection objects, graph and cars
    inter_nodes = generator.generate_node(col=column, row=row, red_prob=1)
    G = generator.generate_edge(inter_nodes, col=column, row=row)
    # all_cars = generator.generate_cars(inter_nodes, G, col=column, row=row, num_cars=car_num)

    car_thread = threading.Thread(name="cargen", target=generator.car_generator, args=(inter_nodes, G, column, row, 5))
    car_thread.daemon = True
    car_thread.start()

    main(screen, column, row, G, inter_nodes, intersections, streets, light_offset)



