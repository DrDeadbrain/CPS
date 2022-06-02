import json
import threading

import pygame
import paho.mqtt.client as mqtt

import coordination
import generator
from intersection import nx, World, Intersection, Car, cargroup
from typing import *

import os
import time

global NTWRK
NTWRK = True
COORDINATED = False

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

last_mwt = 0  # last max waiting time
global emergency_activated
emergency_activated = False
global rush_hour_activated
rush_hour_activated = False
global emergency_path_sent
emergency_path_sent = False
rushhour_path_sent = False


def on_connect_button(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    print("Simulation connected to Broker")
    client.subscribe(f"button/emergency", 1)
    client.subscribe(f"button/rush_hour", 1)
    client.subscribe(f"switch/coordinated", 1)


def on_connect_car(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    print("Simulation connected to Broker")


def on_connect_intersection(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    print("Intersection {id} connected to Broker")


def on_message_intersection(client, userdata, message):
    intersection_list = json.loads(message.payload)
    for i in intersection_list:
        if i == client.id:
            previous = intersection_list[i - 1]
            next = intersection_list[i + 1]
            if (previous == (i - 3)) or (previous == (i + 3)):
                if message.topic == f"intersection/{i}/emergency":
                    client.state_ns = True
                    client.cycle_time = 10000
                    client.publish(f"intersection/{next}/emergency", message.payload, qos=2)
                if message.topic == f"intersection/{i}/rushhour":
                    client.state_ns = True
                    client.cycle_time = 20
                    client.publish(f"intersection/{next}/emergency", message.payload, qos=2)
            if (previous == (i - 1)) or (previous == (i + 1)):
                if message.topic == f"intersection/{i}/emergency":
                    client.state_we = True
                    client.cycle_time = 10000
                    client.publish(f"intersection/{next}/emergency", message.payload, qos=2)
                if message.topic == f"intersection/{i}/rushhour":
                    client.state_we = True
                    client.cycle_time = 20
                    client.publish(f"intersection/{next}/emergency", message.payload, qos=2)

def on_message_button(client, userdata, message):
    global emergency_activated
    global rush_hour_activated
    if message.topic == "button/emergency":
        if not emergency_activated:
            emergency_activated = True
            print("*****************************")
            print("EMERGENCY ACTIVATED")
            print("*****************************")
            emergency_car_thread.start()
        else:
            emergency_activated = False
            global emergency_path_sent
            emergency_path_sent = False
            print("*****************************")
            print("EMERGENCY DEACTIVATED")
            print("*****************************")
            emergency_car_thread.join()
    if message.topic == "button/rush_hour":
        if not rush_hour_activated:
            rush_hour_activated = True
            print("*****************************")
            print("RUSH HOUR ACTIVATED")
            print("*****************************")
            generator.rush_hour_active = True
            rush_hour_thread.start()
        else:
            rush_hour_activated = False
            global rushhour_path_sent
            rushhour_path_sent = False
            print("*****************************")
            print("RUSH HOUR DEACTIVATED")
            print("*****************************")
            rush_hour_thread.join()
            generator.rush_hour_active = False
    if message.topic == "switch/coordinated":
        converted = message.payload.decode("utf-8")
        if converted == "true":
            print("*****************************")
            print("SWITCH TO COORDINATED")
            print("*****************************")
            global COORDINATED
            COORDINATED = True
        else:
            print("*****************************")
            print("SWITCH TO UNCOORDINATED")
            print("*****************************")
            COORDINATED = False


if NTWRK:
    try:
        os.environ["DISPLAY"]
    except:
        os.environ["SDL_VIDEODRIVER"] = "dummy"

    mqttAddr = os.getenv('MQTT_ADDR', 'localhost')

    publish_client = mqtt.Client("Sim Publisher")
    publish_client.connect(host=mqttAddr, port=1883)

    button_client = mqtt.Client("Simulation buttons")
    button_client.on_connect = on_connect_button
    button_client.on_message = on_message_button
    button_client.connect(host=mqttAddr, port=1883)

    car_client = mqtt.Client("Car Client")
    car_client.on_connect = on_connect_car
    car_client.connect(host=mqttAddr, port=1883)

    # for each intersection
    inter1_client = mqtt.Client("Intersection1 Client")
    inter1_client.on_connect = on_connect_intersection
    inter1_client.on_message = on_message_intersection
    inter1_client.connect(host=mqttAddr, port=1883)

    inter2_client = mqtt.Client("Intersection2 Client")
    inter2_client.on_connect = on_connect_intersection
    inter2_client.on_message = on_message_intersection
    inter2_client.connect(host=mqttAddr, port=1883)

    inter3_client = mqtt.Client("Intersection3 Client")
    inter3_client.on_connect = on_connect_intersection
    inter3_client.on_message = on_message_intersection
    inter3_client.connect(host=mqttAddr, port=1883)

    inter4_client = mqtt.Client("Intersection4 Client")
    inter4_client.on_connect = on_connect_intersection
    inter4_client.on_message = on_message_intersection
    inter4_client.connect(host=mqttAddr, port=1883)

    inter5_client = mqtt.Client("Intersection5 Client")
    inter5_client.on_connect = on_connect_intersection
    inter5_client.on_message = on_message_intersection
    inter5_client.connect(host=mqttAddr, port=1883)

    inter6_client = mqtt.Client("Intersection6 Client")
    inter6_client.on_connect = on_connect_intersection
    inter6_client.on_message = on_message_intersection
    inter6_client.connect(host=mqttAddr, port=1883)

    inter7_client = mqtt.Client("Intersection7 Client")
    inter7_client.on_connect = on_connect_intersection
    inter7_client.on_message = on_message_intersection
    inter7_client.connect(host=mqttAddr, port=1883)

    inter8_client = mqtt.Client("Intersection8 Client")
    inter8_client.on_connect = on_connect_intersection
    inter8_client.on_message = on_message_intersection
    inter8_client.connect(host=mqttAddr, port=1883)

    inter9_client = mqtt.Client("Intersection9 Client")
    inter9_client.on_connect = on_connect_intersection
    inter9_client.on_message = on_message_intersection
    inter9_client.connect(host=mqttAddr, port=1883)

    time.sleep(5)
    publish_client.loop_start()
    button_client.loop_start()
    car_client.loop_start()

    inter1_client.loop_start()
    inter2_client.loop_start()
    inter3_client.loop_start()
    inter4_client.loop_start()
    inter5_client.loop_start()
    inter6_client.loop_start()
    inter7_client.loop_start()
    inter8_client.loop_start()
    inter9_client.loop_start()

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
    global last_mwt
    pygame.init()
    font = pygame.font.SysFont('Arial', 10)
    clock = pygame.time.Clock()
    world = World(G, intersections, cargroup)

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
                if car.emergency:
                    car_num = font.render(str(num), True, blue)
                    screen.fill(blue, location)
                    screen.blit(car_num, location)
                else:
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
        id = -1
        for i in intersections:
            id += 1
            queue = 0
            for j in i.queue_all:
                queue += len(j)
            print("Intersection " + str(id) + ": " + str(queue))
            queue_dict[str(id)] = str(queue)
        json_string = json.dumps(queue_dict)
        print(json_string)

        # average waiting time
        avg_waiting_time = world.get_avg_waiting_time()
        print("Avg. waiting time: {}".format(avg_waiting_time))

        # max waiting time
        max_waiting_time = world.get_max_waiting_time()
        curr_mwt = max(max_waiting_time, last_mwt)
        last_mwt = curr_mwt
        print("Max waiting time: {}".format(curr_mwt))

        # emergency car waiting time
        emergency_waiting_time = world.get_emergency_waiting_time()
        print("Emergency waiting time: {}".format(emergency_waiting_time))

        # publishing via MQTT
        if NTWRK:
            publish_client.publish(f"simulation/intersection_queues", json_string, qos=2)
            publish_client.publish(f"simulation/max_waiting_time", max_waiting_time, qos=2) # max value of currently driving cars
            # publish_client.publish(f"simulation/max_waiting_time", curr_mwt, qos=2)  # all time max value
            publish_client.publish(f"simulation/avg_waiting_time", avg_waiting_time, qos=2)
            publish_client.publish(f"simulation/emergency_waiting_time", emergency_waiting_time, qos=2)

            if COORDINATED:
                if emergency_activated:
                    intersection_list = world.get_emergency_car_path()
                    path = []
                    for i in intersection_list:
                        path.append(i.id)
                    intersection_id = path[0]
                    converted_path = json.dumps(path)
                    if len(path) > 0:
                        print("#############################################################################")
                        print("EMERGENCY" + str(intersection_id) + str(converted_path))
                    if not emergency_path_sent:
                        publish_client.publish(f"intersection/{intersection_id}/emergency", converted_path, qos=2)
                        global emergency_path_sent
                        emergency_path_sent = True
                if rush_hour_activated:
                    intersection_list = world.get_rushhour_car_path()
                    path = []
                    for i in intersection_list:
                        path.append(i.id)
                    intersection_id = path[0]
                    converted_path = json.dumps(path)
                    if len(path) > 0:
                        print("#############################################################################")
                        print("RUSH HOUR" + str(intersection_id) + str(converted_path))
                    if not rushhour_path_sent:
                        publish_client.publish(f"intersection/{intersection_id}/rushhour", converted_path, qos=2)
                        global rushhour_path_sent
                        rushhour_path_sent = True
                    print("gesdfdsf")

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
    row = 3
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

    car_thread = threading.Thread(name="cargen", target=generator.car_generator, args=(inter_nodes, G, column, row, 5))
    car_thread.daemon = True
    car_thread.start()

    # on message (from dashboard button)
    # activate thread and stop it if button is pressed again
    rush_hour_thread = threading.Thread(name="rush hour generation", target=generator.car_generator_rushhour,
                                        args=(inter_nodes, G, column, row, 5))
    rush_hour_thread.daemon = True

    emergency_car_thread = threading.Thread(name="Emergency car generation", target=generator.emergency_car_generator,
                                            args=(inter_nodes, G, column, row, 5))
    emergency_car_thread.daemon = True

    # rush_hour_thread.start()
    # emergency_car_thread.start()

    main(screen, column, row, G, inter_nodes, intersections, streets, light_offset)


# TODO: 1 client for all cars -> rush hour cars get var set. If rush hour car triggers message -> activate green wave on their path for time x
# TODO: rush hour thread for time x when button is pressed
# TODO: cycle time for intersection
# TODO: update_intersection in world: for each intersection: if time_count == cycle_time -> toggle states, else: time_count++
# TODO: --> on message switch state to let rush hour cars pass

# ----------------------------- Intersection Setup -----------------------------
# -----   ------------ 6 -------------- 7 --------------- 8   ------------------
# -----                |                |                 |                 ----
# -----                |                |                 |                 ----
# -----   ------------ 3 -------------- 4 --------------- 5   ------------------
# -----                |                |                 |                 ----
# -----                |                |                 |                 ----
# -----   ------------ 0 -------------- 1 --------------- 2   ------------------
# ------------------------------------------------------------------------------


# Rush Hour Path --> init(7) -> (8) -> (5) -> (2)

