from tqdm import tqdm
import airport
import os.path
import geo
import Cst
import QPPTW
import random
import helpfunction
import json

APT_FILE = Cst.APT_FILE
airport_cepo = airport.load2(APT_FILE)
airport_init = airport.load(APT_FILE)
turn_lines = {}
thrust_level = [0.101, 0.128, 0.155, 0.182, 0.209, 0.236, 0.263, 0.291]
def calculate_cost(length, speed, fuel_rate):
    """
    Calculate the time and fuel cost for a segment at a given speed.

    :param length: Length of the segment in meters.
    :param speed: Speed in m/s.
    :param fuel_rate: Fuel consumption rate in liters per second.
    :return: Tuple of time cost (in seconds) and fuel cost (in liters).
    """
    time_cost = abs(length / speed)  # Time to travel the segment
    fuel_cost = time_cost * fuel_rate  # Total fuel consumed
    return time_cost, fuel_cost


def initial_network(airport_cepo):
    graph = {}
    weights = {}
    network = {}
    in_angles = {}
    out_angles = {}
    time_windows = {}
    init_l = {}
    # print("the number of points", len(airport_cepo.points))
    # points, lines, runways = [], [], []
    points = airport_cepo.points
    runways = airport_cepo.runways
    lines = airport_cepo.lines
    init_lines = airport_init.lines
    points0 = airport_init.points
    pushback_edges = []

    for (i, point) in enumerate(points):
        network[point.xy] = {}
        in_angles[point.xy] = {}
        out_angles[point.xy] = {}
        graph[point.xy] = []
    for (i, line) in enumerate(lines):
        line_init = init_lines[i]
        length = geo.length(line_init.xys)
        # print(line.speed)

        length_cepo = abs(length / line.speed)
        # if line.speed != 10:
        #     length_cepo = abs(length / 3)

        p11 = line_init.xys[0]
        p22 = line_init.xys[1]
        p33 = line_init.xys[-2]
        p44 = line_init.xys[-1]
        p1 = line.xys[0]
        p4 = line.xys[-1]

        if line.speed != 10:
            if (p4, p1) not in turn_lines:
                turn_lines[(p1, p4)] = line.speed
                turn_lines[(p4, p1)] = line.speed
                length = -length
        init_l[(p1, p4)] = length
        init_l[(p4, p1)] = length

        if length == 0.0:
            print('Line = 0', line.oneway, line.taxiway)

        while length != 0.0:  # ignore the line with length '0'
            # network[p1][p4] = length_cepo
            # network[p4][p1] = length_cepo
            if (p1, p4) not in graph[p1]:
                graph[p1].append((p1, p4))
            if (p4, p1) not in graph[p4]:
                graph[p4].append((p4, p1))

            weights[(p1, p4)] = length_cepo
            weights[(p4, p1)] = length_cepo
            time_windows[(p1, p4)] = [(0, 24 * 60 * 60 * 1.5)]
            time_windows[(p4, p1)] = [(0, 24 * 60 * 60 * 1.5)]
            if line.speed < 0:  # Give the angle of every arc and reverse the pushback's outangle
                in_angles[p1][p4] = geo.angle_2p(p11, p22)
                out_angles[p1][p4] = geo.angle_2p(p44, p33)
                in_angles[p4][p1] = geo.angle_2p(p44, p33)
                out_angles[p4][p1] = geo.angle_2p(p22, p11)
                pushback_edges.append((p1, p4))
            else:
                in_angles[p1][p4] = geo.angle_2p(p11, p22)
                out_angles[p1][p4] = geo.angle_2p(p33, p44)
                in_angles[p4][p1] = geo.angle_2p(p44, p33)
                out_angles[p4][p1] = geo.angle_2p(p22, p11)
            length = 0.0  # 注意浮点型
            if line.oneway:  # 处理路网单向路
                # print(line.oneway)
                # time_windows[(p4, p1)] = [(0, 0)]
                graph[p4].remove((p4, p1))

    for (i, runway) in enumerate(runways):
        p1 = runway.xys[0]
        p2 = runway.xys[1]
        # graph[p1] = {}
        # graph[p2] = {}
        if (p1, p2) not in graph[p1]:
            graph[p1].append((p1, p2))
        if (p2, p1) not in graph[p2]:
            graph[p2].append((p2, p1))
        length = float('inf')
        # init_l[(p1, p2)] = length
        # init_l[(p2, p1)] = length
        weights[(p1, p2)] = length
        weights[(p2, p1)] = length
        time_windows[(p1, p2)] = [(0, 24 * 60 * 60 * 1.5)]
        time_windows[(p2, p1)] = [(0, 24 * 60 * 60 * 1.5)]

        in_angles[p1][p2] = geo.angle_2p(p1, p2)
        out_angles[p1][p2] = geo.angle_2p(p1, p2)
        in_angles[p2][p1] = geo.angle_2p(p2, p1)
        out_angles[p2][p1] = geo.angle_2p(p2, p1)

    # Initialize the cost matrix for each segment
    costs = {}

    # Assuming speeds and fuel_consumption_rate are defined
    V1 = 1
    V2 = 0.75
    V3 = 0.5
    X = 0.101

    # print(fuel_rates)
    speeds = [V1, V2, V3]  # Replace with actual values
    fuel_consumption_rate = X  # Replace with actual value
    fuel_consumption_rates = [0.291, 0.291*0.75, 0.291*0.5]


    for (i, line) in enumerate(lines):
        line_init = init_lines[i]
        p1 = line.xys[0]
        p4 = line.xys[-1]
        edge = (p1, p4)
        length = geo.length(line_init.xys)  # Assuming this is the length of the segment
        rates = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

        # if edge in turn_lines:
        #     speed = abs(line.speed)  # Speed = -3
        #     # speed = 3
        #     costs[(p4, p1)] = costs[(p1, p4)] = calculate_cost(length, speed, fuel_consumption_rate)
        # else:
        #     costs[(p4, p1)] = costs[(p1, p4)] = calculate_cost(length, line.speed, 0.291)

        if line.speed < 0:
        # if edge in turn_lines:
            speed = abs(line.speed)  # Speed = -3
            costs[(p4, p1)] = costs[(p1, p4)] = calculate_cost(length, speed, fuel_consumption_rate)
        else:
            # Calculate cost for each speed
            fuel_rates = thrust_level[:line.speed-2]
            rates = rates[:line.speed-2]

            costs[(p4, p1)] = costs[(p1, p4)] = [calculate_cost(length, 10 * rate, fuel_consumption_rate) for
                                                 rate, fuel_consumption_rate in zip(rates, fuel_rates)]
            # # print(speed)
            # costs[(p4, p1)] = costs[(p1, p4)] = calculate_cost(length, line.speed, 0.291)
            # print(length, costs[(p4, p1)])
            # costs[(p4, p1)] = costs[(p1, p4)] = [calculate_cost(length, 10 * rate, fuel_consumption_rate) for
            #                                      rate, fuel_consumption_rate in zip(speeds, fuel_consumption_rates)]
            # print(costs)

    # Now, `costs` dictionary contains the time and fuel costs for each segment at different speeds
    return graph, weights, time_windows, in_angles, out_angles, costs, pushback_edges, init_l, turn_lines


# Initial_cost of the all points, and the cost is the smallest weight between the two points
def initial_cost(graph, weights, time_windows, in_angles, out_angles, Stand):
    # points = airport_init.points
    start_time = 0
    points0 = airport_cepo.points
    runway_points = [p for p in points0 if p.ptype == 'Stand' or p.ptype == 'Runway']
    # stand_points = [p for p in points0 if p.ptype == 'Stand' or p.ptype == 'Runway']
    cost_of_path = {}
    path_list = {}
    # with open('cost_of_path.json', 'r') as file:
    #     cost_of_path = json.load(file)
    for s in tqdm(points0, ncols=100):
        # if s.ptype == 'Stand':
        #     continue
        source = s.xy
        ss = str(s.xy)
        cost_of_path[ss] = {}
        path_list[ss] = {}
        for d in runway_points:
            target = d.xy
            tt = str(d.xy)
            _, path1, new_time_windows, time_cost = QPPTW.QPPTW_algorithm(graph, weights, time_windows, source, target,
                                                                        start_time, in_angles, out_angles, Stand)
            _, path2, new_time_windows, time_cost2 = QPPTW.QPPTW_algorithm(graph, weights, time_windows, target, source,
                                                                      start_time, in_angles, out_angles, Stand)
            if time_cost < 3000:
                fuel_cost = 0
                for i in range(1, len(path1)):
                    current_vertex = path1[i - 1]
                    next_vertex = path1[i]
                    edge = (current_vertex, next_vertex)
                    # fuel_cost = 0
                    if edge in turn_lines:
                        # print( Initial_network.thrust_level[abs(Initial_network.turn_lines[edge]) - 3])
                        fuel_cost = fuel_cost + weights[edge] * thrust_level[abs(turn_lines[edge]) - 3]
                    else:
                        fuel_cost = fuel_cost + weights[edge] * 0.291
            else:
                fuel_cost = float('inf')
            if tt not in cost_of_path.keys():
                cost_of_path[tt] = {}
                path_list[tt] = {}
            if d == s:
                cost_of_path[ss][tt] = cost_of_path[tt][ss] = 0
                path_list[ss][tt] = path_list[tt][ss] = None
                continue
            # print(time_cost)
            if time_cost == time_cost2:
                cost_of_path[ss][tt] = (time_cost, fuel_cost)
                cost_of_path[tt][ss] = (time_cost2, fuel_cost)
            elif time_cost2 < 3000:
                cost_of_path[ss][tt] = (time_cost, fuel_cost)
                cost_of_path[tt][ss] = (time_cost2, fuel_cost)
            else:
                cost_of_path[ss][tt] = (time_cost, fuel_cost)
                cost_of_path[tt][ss] = (time_cost2, float('inf'))
            path_list[ss][tt] = path1
            path_list[tt][ss] = path1.reverse()

    with open('cost_of_path.json', 'w') as file:
        json.dump(cost_of_path, file, indent=4)
    with open('path_list.json', 'w') as file:
        json.dump(path_list, file, indent=4)

# with open('cost_of_path.json', 'r') as file:
#     cost_of_path = json.load(file)
# 调用函数
# initial_cost(graph, weights, time_windows, source, target, start_time, in_angles, out_angles, Stand)


