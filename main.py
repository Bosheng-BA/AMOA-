import sys
import airport
import Initial_network
import datetime
import Sour_and_Des
import json
import os
import Cst
import MOA
import QPPTW
import Draw_path
import copy
from tqdm import tqdm
import pandas as pd
import gaptraffic

# above imported library
""" Default airport and traffic files """
DATA_PATH = Cst.DATA_PATH
APT_FILE = os.path.join(DATA_PATH, "tianjin_new.txt")
# FPL_FILE = os.path.join(DATA_PATH, "ZBTJ_20210725_Manex_STD.B&B.sim")
FPL_FILE = os.path.join(DATA_PATH, "ZBTJ_20210725_Manex_16R.B&B.sim")


# 函数，将列表写入到json文件
def write_list_to_json(list_name, filename):
    with open(filename, 'w') as f:
        json.dump(list_name, f)


# 函数，将列表写入到文件
def write_list_to_file(list_name, filename):
    with open(filename, 'w') as f:
        for item in list_name:
            f.write("%s\n" % item)


def show_point_name(point, points):
    for p in points:
        if p.xy[0] == point[0] and p.xy[1] == point[1]:
            point_name = p.name
            return point_name


def show_point_coor(point, points):
    for p in points:
        if p.name == point:
            point_xy = p.xy
            return point_xy


if __name__ == "__main__":
    fpl_file = sys.argv[1] if 1 < len(sys.argv) else FPL_FILE
    # Load the airport and the traffic
    the_airport = airport.load(APT_FILE)
    the_airport2 = airport.load2(APT_FILE)
    points = the_airport2.points
    runways = the_airport2.runways

    stand_dict, runway_dict, stand_list, stand_dict2, runway_list, runway_dict2 \
        = Sour_and_Des.stand_and_runway_points(points=the_airport2.points)


    # 把路网中的cost信息提前预存，每次更换路网只需要运行一次
    # Initial_network.initial_cost(graph, weights, time_windows, in_angles, out_angles, Stand)

    """遍历一天"""
    flight_file_name_list = Cst.file
    # print(Cst.file)
    """一次性遍历十天"""
    # flight_file_name_list = Cst.flight_file_name_list

    COSTS = []
    Stand = []
    for p in points:
        if p.ptype == 'Stand' or p.ptype == 'Runway':
            Stand.append(p.xy)

    def suanfa(flights, file_name, W):
        graph, weights, time_windows, in_angles, out_angles, costs, pushback_edges, init_l, turn_lines = \
            Initial_network.initial_network(the_airport2)
        Failure_flight = []

        cost_of_path = {}
        with open('cost_of_path.json', 'r') as file:
            cost_of_path = json.load(file)

        Total_cost = 0
        graph_copy = copy.deepcopy(graph)
        init_Tcost = 0
        turn_times = 0
        Tcost_without_waiting = 0
        Lenth = 0
        totalholding_time = 0

        # for flightnum in list_def:
        # 使用tqdm来遍历航班列表，并设置进度条长度(ncols)为100
        # for flightnum in tqdm(range(len(flights)), ncols=100):
        # for flightnum in range(len(flights)):
        for flightnum in range(183, 184):
            # 多飞机规划路径：初始化开始时间
            init_time = datetime.datetime(2023, 4, 17, 7, 0)

            results = []
            paths = []
            COST_list = []
            flight = flights[flightnum]

            # 这里是选择确定飞机的推出的时间
            if flight.departure == 'ZBTJ':
                start_time = flight.ttot - 600
            else:
                start_time = flight.aldt

            # 这里是选择确定飞机的起飞与终点
            source, target = Sour_and_Des.find_the_sour_des(stands=stand_dict, pists=runway_dict, flight=flight)
            name1 = show_point_name(source, points=the_airport2.points)
            name2 = show_point_name(target, points=the_airport2.points)

            check = 0
            if len(graph[source]) > 1:  # Only one pushback do not think about this
                for edge in graph[source]:
                    if edge not in pushback_edges:  # Ensure the boolean value
                        continue
                    elif edge in pushback_edges:
                        check += 1

            list_edge = graph[source]
            if check >= 2:  # When the stand have two ways to pushback, we need choose one
                for e in list_edge:
                    if e in pushback_edges:
                        graph_copy[source].remove(e)
                        path, COST, holding_time= MOA.AMOA_star(source, target, costs, graph_copy, time_windows, start_time, out_angles,
                                                    in_angles, Stand, weights, cost_of_path, W)
                        graph_copy[source].append(e)
                        COST_list.append(COST)
                        paths.append(path)

                if COST_list:
                    # 将 COST_list 中的所有集合扁平化为一个包含所有成本向量的列表
                    # flattened_list = [item for sublist in COST_list if sublist is not None for item in sublist]
                    flattened_list = list(COST_list)
                    # 过滤掉所有的 None 元素
                    filtered_list = [x for x in flattened_list if x is not None]
                    # print(COST_list)

                    if filtered_list:
                        # 如果过滤后的列表不为空，则寻找最小成本向量
                        min_cost_vector = min(filtered_list, key=lambda x: list(x)[0][0])
                    else:
                        # 如果过滤后的列表为空，则设置 min_cost_vector 为 None 或其他适当的默认值
                        min_cost_vector = None

                    COST = min_cost_vector
                    # print(min_cost_vector)
                    # COST = min(COST_list, key=lambda x: x[0])
                    if min_cost_vector:
                        # print(COST_list, COST)
                        path = paths[COST_list.index(COST)]
                    else:
                        path = None
            else:  # the normal condition
                path, COST , holding_time= MOA.AMOA_star(source, target, costs, graph, time_windows, start_time, out_angles, in_angles,
                                            Stand, weights, cost_of_path, W)

            # path, COST = TEST.AMOA_star(source, target, costs, graph, time_windows, start_time, out_angles, in_angles,
            # Stand)

            if COST is None or path is None:
                Failure_flight.append(flightnum)
                # if path:
                    # Draw_path.create_matplotlib_figure(graph, path, name1, name2, flightnum)
            elif path:
                # label_path = QPPTW.construct_labeled_path(graph, weights, time_windows, source, start_time, path)
                # time_windows = QPPTW.Readjustment_time_windows(graph, weights, time_windows, label_path)
                # graph0, weights0, time_windows0, in_angles0, out_angles0, costs0, pushback_edges0 = \
                #     Initial_network.initial_network(the_airport)
                Draw_path.create_matplotlib_figure(graph, path, name1, name2, flightnum, turn_lines)

                # """记录每一个航班的成本"""
                # COSTS.append(list(COST)[0][0])
                Total_cost = Total_cost + list(COST)[0][0]
                init_Tcost = init_Tcost + list(COST)[0][1]
                # 用于结果处理原始路径以及转弯次数
                lenth = 0
                time_lenth = 0
                turn_time = 0
                for i in range(1, len(path)):
                    current_vertex = path[i - 1]
                    next_vertex = path[i]
                    edge = (current_vertex, next_vertex)
                    l = init_l[edge]
                    t = weights[edge]
                    if edge in turn_lines:
                        turn_time += 1
                    lenth = lenth + abs(l)
                    time_lenth = time_lenth + t
                turn_times = turn_times + turn_time
                Lenth = Lenth + lenth
                Tcost_without_waiting = Tcost_without_waiting + time_lenth
                # totalholding_time = totalholding_time + holding_time
            # print(COST, time_lenth)
            # print("fligt:", flightnum, "Path:", path)
            # print("Cost:",flightnum, COST, turn_time)
            # print("Cost:", flightnum, turn_time)
        cost_info = {
            "Date": file_name,
            "Total cost": Total_cost,
            "Fuel cost": init_Tcost,
            "Length": Lenth,
            "Tcost without waiting": Tcost_without_waiting,
            "Total turn times": turn_times,
            "False flight number": len(Failure_flight),
            "False": Failure_flight,
        }
        COSTS.append(cost_info)
        # print(cost_info)
        print("Total cost:", Total_cost, "Fuel_cost ", init_Tcost, W)
        # print("Lenth:", Lenth, "Tcost_without_waiting:", Tcost_without_waiting, "Total_turn_times ", turn_times)
        # 现在我们可以调用这些函数将列表写入到文本文件
        write_list_to_json(COSTS, 'Results/' + file_name + str(Cst.weight) + 'cost.json')
        # # 确保目录存在
        # file = Cst.file
        # os.makedirs(file, exist_ok=True)
        return COSTS

    for file_name in flight_file_name_list:
        W = Cst.weight
        # W = [0.1, 0,9]
        # print(file_name)
        if file_name == 'g':
            flights = gaptraffic.read_flights("Datas/traffic/" + flight_file_name_list)
            COSTS = suanfa(flights, flight_file_name_list, W)
            break
        else:
            flights = gaptraffic.read_flights("Datas/traffic/" + file_name)
            COSTS = suanfa(flights, file_name, W)
        write_list_to_json(COSTS, 'Results/' + 'Total_ten_days' + str(Cst.weight) + 'cost.json')

    # 在循环外初始化一个空的DataFrame
    # results = pd.DataFrame(columns=['Weight1', 'Weight2', 'TimeCost', 'FuelCost'])
    # n = 200
    # for i in tqdm(range(n+1), ncols=75):
    #     # 计算权重
    #     weight = [1 - 1/n * i, 0 + 1/n * i]
    #     flights = gaptraffic.read_flights("Datas/traffic/" + flight_file_name_list)
    #     COSTS = suanfa(flights, flight_file_name_list, weight)
    #     timecost = COSTS[i]['Total cost']
    #     fuelcost = COSTS[i]['Fuel cost']
    #
    #     # 将结果追加到DataFrame中
    #     results = results.append({
    #         'Weight1': weight[0],
    #         'Weight2': weight[1],
    #         'TimeCost': timecost,
    #         'FuelCost': fuelcost
    #     }, ignore_index=True)
    #
    # # 确保数据按照Weight1列排序
    # results.sort_values(by='Weight1', inplace=True)
    # # 将结果DataFrame保存到CSV文件中
    # results.to_csv('results单机.csv', index=False)


