import math
import pandas as pd
import geo
import datetime


# 转换路网的类型
def turn_network(network_point):
    neighbor_info = {key: list(value.keys()) for key, value in network_point.items()}
    return neighbor_info


# 将数字编号类型的路径序列转换为坐标类型
def list2node(list, pointcoordlist):
    plist = []
    for i in list:
        plist.append(pointcoordlist[i])
    return plist


# 打印出坐标类型的序列的point的信息
def print_plist(plist, points):
    for p in plist:
        for point in points:
            if point.xy == p:
                # print(f"Point: ptype={point.ptype}, name={point.name}, xy={point.xy}")
                # print(f"Point: {point.ptype} {point.name} {point.xy}", end="++")
                print(f" {point.ptype} {point.name} {point.xy}", end="--")


# 打印出一个路网的中每个point的neighbor point信息
def print_neighbor_info(neighbor_info, points):
    # 遍历新字典
    for key_xy, value_xys in neighbor_info.items():
        # 找到与键匹配的点并打印属性
        for point in points:
            if point.xy == key_xy:
                print(f"Key: ptype={point.ptype}, name={point.name}, xy={point.xy}")
                break

        # 找到与值匹配的点并打印属性
        for value_xy in value_xys:
            for point in points:
                if point.xy == value_xy:
                    print(f"Value: ptype={point.ptype}, name={point.name}, xy={point.xy}")
                    break


def findpointtype(line1, line2, points):
    point_list_type = []
    point_list = [line1.xys[0], line1.xys[-1], line2.xys[0], line2.xys[-1]]
    for p in points:
        if p.xy in point_list:
            point_list_type.append(p.ptype)
    S = 'Stand'
    if S in point_list_type:
        return 1
    return 0


def blocknode(network, path, start_time):
    """

    """
    # start_time  # 此飞机的起始第一个点的时间
    # the current position of the obstacle
    block_timedict = {}
    path_cost = [0]

    for i in range(len(path) - 1):
        block_set = [start_time, start_time]

        path_cost.append(path_cost[-1] + network[path[i]][path[i + 1]])

        nextcost = network[path[i]][path[i + 1]]
        cost = 20 if nextcost > 20 else nextcost

        time1 = start_time + datetime.timedelta(seconds=path_cost[-2])  # block 开始时间
        time2 = time1 + datetime.timedelta(seconds=path_cost[-1]) + datetime.timedelta(seconds=cost)  # block 结束时间
        block_set[0] = time1
        block_set[1] = time2
        block_timedict[path[i]] = block_set

    return block_timedict


def blocknode2(network, path, start_time):
    """

    """
    # start_time  # 此飞机的起始第一个点的时间
    # the current position of the obstacle
    block_timedict2 = {}
    path_cost = [0]
    init_time = datetime.datetime(2023, 4, 17, 7, 0)
    s_t = (start_time - init_time).seconds
    # e_t = (start_time - init_time).seconds
    # block_set = [s_t, s_t]

    for i in range(len(path) - 1):
        block_set = [s_t, s_t]  # Initialize block_set as a new list with two elements

        path_cost.append(path_cost[-1] + network[path[i]][path[i + 1]])

        nextcost = network[path[i]][path[i + 1]]
        cost = 20 if nextcost > 20 else nextcost

        time1 = start_time + datetime.timedelta(seconds=path_cost[-2])  # block 开始时间
        time2 = time1 + datetime.timedelta(seconds=path_cost[-1]) + datetime.timedelta(seconds=cost)  # block 结束时间
        t1 = (time1 - init_time).seconds
        t2 = (time2 - init_time).seconds
        block_set[0] = t1
        block_set[1] = t2
        block_timedict2[i] = block_set

    return block_timedict2


def find_pushback_points(points, pointcoordlist):
    pushback_points = []
    for p in points:
        if p.ptype == 'pushback':
            # print(pointcoordlist.index(p.xy))
            pushback_points.append(pointcoordlist.index(p.xy))
        else:
            if p.xy[1] == 6522 and 20557 <= p.xy[0] <= 20750:
                pushback_points.append((pointcoordlist.index(p.xy)))
            elif p.xy[1] == 6715:
                if 20805 <= p.xy[0] <= 21015:
                    pushback_points.append((pointcoordlist.index(p.xy)))
                elif 21560 <= p.xy[0] <= 22092:
                    pushback_points.append((pointcoordlist.index(p.xy)))
                elif 22565 <= p.xy[0] <= 23018:
                    pushback_points.append((pointcoordlist.index(p.xy)))

            elif p.xy[1] == 7324:
                if 21150 <= p.xy[0] <= 21200:
                    pushback_points.append((pointcoordlist.index(p.xy)))
                elif p.xy[0] == 21759:
                    pushback_points.append((pointcoordlist.index(p.xy)))

            elif p.xy[1] == 7321 and p.xy[0] == 22098:
                pushback_points.append((pointcoordlist.index(p.xy)))
            elif p.xy[1] == 7689 and 22516 <= p.xy[0] <= 22570:
                pushback_points.append((pointcoordlist.index(p.xy)))
            elif p.xy[0] == 22622 and 7891 <= p.xy[1] <= 8111:
                pushback_points.append((pointcoordlist.index(p.xy)))
            elif p.xy[1] == 6533 and 21830 <= p.xy[0] <= 22060:
                pushback_points.append((pointcoordlist.index(p.xy)))

    # print("pushback_points", len(pushback_points))
    # print(pushback_points)
    pushback_points.append(1122)
    pushback_points.append(1121)
    pushback_points.append(1123)
    return pushback_points
