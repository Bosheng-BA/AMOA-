import math
import QPPTW
import json
import Initial_network
import Cst

# weight = Cst.weight

def read_cost_vector(n, m, costs):
    # This should read the cost vector from the database or data structure
    C_n_m = costs[n, m]
    return C_n_m


def check_time_windows(segment, time_windows, c_n_m_l, G_op, G_cl, start_time):
    # This should check time windows for all edges within the segment
    check = False
    holding_enabled = False
    # holding_cost = 0
    for window_start, window_end in time_windows[segment]:
        n = segment[0]

        if n in G_op and G_op[n]:
            # print("n in G_op ")
            current_time = start_time + next(iter(G_op[n]))[0]
        elif n in G_cl and G_cl[n]:
            # print('n in G_cl')
            current_time = start_time + next(iter(G_cl[n]))[0]

        if c_n_m_l[0] + current_time > window_end:
            check = False
            break
        elif current_time < window_start and window_end - window_start >= c_n_m_l[0]:
            check = True
            holding_enabled = True
            holdcost = window_start - current_time
            # print(window_start, current_time)
            holding_cost = (holdcost, holdcost * 0.0355)
        elif window_start <= c_n_m_l[0] + current_time <= window_end:
            check = False
            holding_enabled = True
            holding_cost = (0, 0)

    return check, holding_enabled, holding_cost, c_n_m_l


def add_holding_cost(c_n_m_l, holding_cost):
    # This should add the cost of holding to the cost vector
    # print(c_n_m_l, holding_cost)
    c_n_m_l = tuple(sum(x) for x in zip(c_n_m_l, holding_cost))
    return c_n_m_l


def is_dominated(c, c_prime):
    """
    Determine if cost vector c is dominating cost vector c_prime.

    :param c: A cost vector (tuple of integers).
    :param c_prime: Another cost vector (tuple of integers).
    :return: True if c is dominating c_prime, False otherwise.
    """
    # Check if all elements in c are less than or equal to corresponding elements in c_prime
    # and c is not equal to c_prime
    dominated = False
    if isinstance(c, set):
        # 将集合中的所有非 None 子集合扁平化为一个列表
        # print('ccccc')
        c = [item for sublist in c if sublist is not None for item in sublist]

    if c and c_prime:
        # print("c", c, "C_prime", c_prime)
        if all(c_j <= c_prime_j for c_j, c_prime_j in zip(c, c_prime)) and c != c_prime:

            dominated = True
    # else:
    #     dominated = False
    return dominated


def reconstruct_paths(SG, end, start):
    # Placeholder for the path reconstruction process from the search graph SG
    path = []
    current_node = end
    i = 0
    # print(SG)

    while current_node is not start:
        # print("i:", i)
        i += 1
        path.append(current_node)
        current_node = SG.get(current_node)  # 获取父节点
    path.append(start)
    return path[::-1]  # 反转路径


def eliminate_dominated(m, g_m, G_op, G_cl, OPEN):
    """
    Eliminate dominated vectors from G_op_m and G_cl_m.
    Also, remove corresponding entries from OPEN.

    :param g_m: The new cost vector.
    :param G_op_m: The set of cost vectors in G_op for node m.
    :param G_cl_m: The set of cost vectors in G_cl for node m.
    :param OPEN: The set of open alternatives.
    :return: Updated G_op_m, G_cl_m, and OPEN.
    """
    # Remove dominated vectors from G_op_m and G_cl_m
    # G_op_m = G_op.get(m, set())
    # G_cl_m = G_cl.get(m, set())
    new_G_op = G_op
    new_G_cl = G_cl
    new_G_op_m = []  # 创建一个新的空字典
    new_G_cl_m = []  # 创建一个新的空字典

    # 收集要从 G_op 删除的键
    keys_to_remove_op = []
    for key, value in new_G_op.items():  # 遍历 G_op 中的每个键值对
        if key == m:
            V_list = list(value)
            # print(m, V_list)
            if V_list and is_dominated(g_m, V_list[0]):  # 检查值是否没有被 g_m 支配
                keys_to_remove_op.append(key)  # 收集要删除的键

    # 删除收集到的键
    for key in keys_to_remove_op:
        new_G_op_m = list(G_op[key])
        G_op.pop(key)


    # 收集要从 G_cl 删除的键
    keys_to_remove_cl = []
    for key, value in new_G_cl.items():  # 遍历 G_cl 中的每个键值对
        if key == m:
            V_list = list(value)
            # print(V_list)
            if V_list and is_dominated(g_m, V_list[0]):  # 检查值是否没有被 g_m 支配
                keys_to_remove_cl.append(key)  # 收集要删除的键

    # 删除收集到的键
    # print(keys_to_remove_cl, keys_to_remove_op)
    for key in keys_to_remove_cl:
        new_G_cl_m = list(G_cl[key])
        G_cl.pop(key)

    # Remove corresponding entries from OPEN
    # 收集要从 OPEN 删除的元素
    elements_to_remove = []
    for open_element in OPEN:
        if open_element[0] == m:
            if open_element[1] in new_G_op_m or new_G_cl_m:
                # print("2222222222")
                elements_to_remove.append(open_element)

    # 删除收集到的元素
    # print(elements_to_remove)
    for element in elements_to_remove:
        OPEN.remove(element)

    # OPEN = [alt for alt in OPEN if not is_dominated(g_m, alt[1])]
    return G_op, G_cl, OPEN


def select_from_open(OPEN, weight):
    """
    Select the alternative from OPEN with the smallest sum of the first elements of gn and fn.

    :param OPEN: A list of tuples, where each tuple is of the form (n, gn, fn).
    :return: The tuple from OPEN with the smallest sum of the first elements of gn and fn.
    """
    # Find the alternative with the smallest sum of the first elements of gn and fn
    return min(OPEN, key=lambda x: x[2][0] * weight[0] + (x[2][1] * weight[1] * 8.06))
    # return min(OPEN, key=lambda x: x[2][0])


def heuristic_function(current_position, target_position, graph, weights, time_windows,start_time, in_angles, out_angles, Stand, cost_of_path):
    """
    Calculate a heuristic estimate from the current position to the target position.

    :param current_position: Tuple (x, y) representing the current position.
    :param target_position: Tuple (x, y) representing the target position.
    :param max_speed: Maximum speed in the network.
    :param min_fuel_rate: Minimum fuel consumption rate.
    :return: Tuple of heuristic time and fuel cost estimates.
    """
    # Calculate straight line distance
    # distance = (target_position[0] - current_position[0]) + (target_position[1] - current_position[1])
    # source = current_position
    # target = target_position
    #
    # graph_copy = graph
    # labelpath, path, new_time_windows, time_cost = QPPTW.QPPTW_algorithm(graph_copy, weights, time_windows, source, target,
    #                                                                 start_time, in_angles, out_angles, Stand)
    # if time_cost < 3000:
    #     fuel_cost = 0
    #     for i in range(1, len(path)):
    #         current_vertex = path[i - 1]
    #         next_vertex = path[i]
    #         edge = (current_vertex, next_vertex)
    #         # fuel_cost = 0
    #         if edge in Initial_network.turn_lines:
    #             # print( Initial_network.thrust_level[abs(Initial_network.turn_lines[edge]) - 3])
    #             # print(Initial_network.turn_lines[edge])
    #             fuel_cost = fuel_cost + weights[edge] * Initial_network.thrust_level[abs(Initial_network.turn_lines[edge]) - 3]
    #             # fuel_cost = fuel_cost + weights[edge] * Initial_network.thrust_level[0]
    #         else:
    #             fuel_cost = fuel_cost + weights[edge] * Initial_network.thrust_level[-1]
    # else:
    #     # print(time_cost)
    #     fuel_cost = time_cost
    # # print(time_cost, source, target)
    # # fuel_cost = 0
    # h_m = (time_cost, fuel_cost)

    source = str(current_position)
    target = str(target_position)
    # Fuel estimate based on minimum fuel rate and time estimate

    if cost_of_path[source][target] == 0:
        time_estimate = 0
        fuel_estimate = 0
    else:
        time_estimate = cost_of_path[source][target][0]
        fuel_estimate = cost_of_path[source][target][1]
    h_m = (time_estimate * 1, fuel_estimate * 1)
    # print(h_m)
    return h_m


def AMOA_star(start, end, costs, graph, time_windows, start_time, out_angles, in_angles, Stand, weights, cost_of_path, W):
    SG = {}  # Acyclic search graph
    G_op = {start: {(0, 0)}}
    G_cl = {start: set()}
    OPEN = [(start, (0, 0), (0, 0))]
    COSTS = set()
    holding_time = 0

    while OPEN:
        n, g_n, f_n = select_from_open(OPEN, W)
        # print(W)
        OPEN.remove((n, g_n, f_n))
        OPEN = [item for item in OPEN if not any(math.isinf(x) for x in item[2])]

        exists_in_G_op = any(g_n in value_set for value_set in G_op.values())
        if exists_in_G_op:
            key_to_remove = [k for k, v in G_op.items() if g_n in v][0]  # 假设 g_n 只在一个键的值集合中
            # print("key_to:", key_to_remove)
            G_op.pop(key_to_remove)

        if n in G_cl:
            G_cl[n].add(g_n)
        else:
            G_cl[n] = {g_n}

        if n == end:
            COSTS.add(g_n)
            OPEN = [alt for alt in OPEN if is_dominated(alt[2], g_n)]
            if not OPEN:
                path = reconstruct_paths(SG, end, start)
                return path, COSTS, holding_time
        else:
            for segment in graph[n]:
                m = segment[1]  # Assuming segment identifies the end node

                # 检查next_vertex是否在Stand中，并且不是目标点
                if m in Stand and m != end:
                    continue

                if len(SG) >= 1:
                    s = SG[n]
                    ang_rad = out_angles[s][n] - in_angles[n][m]
                    delta = math.cos(ang_rad)  # if len(path) > 1 else 1
                    if (ang_rad / 3.141592653589793) == 1.5:
                        delta = 0  # 控制有1.5pi 等于0 实际为负数
                else:
                    delta = 1
                if 0 <= delta:
                    # C_n_m = read_cost_vector(n, m, costs)
                    if (n, m) in costs:
                        C_n_m = costs[(n, m)]

                    if len(C_n_m) == 2 and isinstance(C_n_m, tuple):  # Turn segment
                        c_n_m_l = C_n_m
                        n, m, g_n, f_n, SG, G_op, G_cl, OPEN, COSTS, end, costs, graph, time_windows, start_time, C_n_m, c_n_m_l, segment, holding_time = \
                            expand(n, m, g_n, f_n, SG, G_op, G_cl, OPEN, COSTS, end, costs, graph, time_windows,
                                   start_time, C_n_m, c_n_m_l, segment, weights,  in_angles, out_angles, Stand, cost_of_path, holding_time)
                    elif len(C_n_m) >= 1 and isinstance(C_n_m, list):  # Normal segment
                        for c_n_m_l in C_n_m:
                            n, m, g_n, f_n, SG, G_op, G_cl, OPEN, COSTS, end, costs, graph, time_windows, start_time, C_n_m, c_n_m_l, segment, holding_time = \
                                expand(n, m, g_n, f_n, SG, G_op, G_cl, OPEN, COSTS, end, costs, graph, time_windows,
                                       start_time, C_n_m, c_n_m_l, segment, weights,  in_angles, out_angles, Stand, cost_of_path, holding_time)

    path = reconstruct_paths(SG, n, start)
    # path = None
    COSTS = None
    return path, COSTS, holding_time


def expand(n, m, g_n, f_n, SG, G_op, G_cl, OPEN, COSTS, end, costs, graph, time_windows, start_time, C_n_m, c_n_m_l,
           segment, weights,  in_angles, out_angles, Stand, cost_of_path, holding_time):
    check, holding_enabled, holding_cost, c_n_m_l = check_time_windows(segment, time_windows, c_n_m_l, G_op, G_cl,
                                                              start_time)
    # check = True
    if check:
        #  holding_enabled is Boolean type
        if holding_enabled:
            print("Holding_enable:", holding_cost)
            hoding_time = holding_time + holding_cost[0]
            c_n_m_l = add_holding_cost(c_n_m_l, holding_cost)
        else:
            # print("No_Holding_enable")
            return n, m, g_n, f_n, SG, G_op, G_cl, OPEN, COSTS, end, costs, graph, time_windows,start_time, C_n_m, c_n_m_l, segment, holding_time

    g_m = tuple(sum(x) for x in zip(g_n, c_n_m_l))
    if m not in SG:
        h_m = heuristic_function(m, end, graph, weights, time_windows,start_time, in_angles, out_angles, Stand, cost_of_path)
        f_m = tuple(sum(x) for x in zip(g_m, h_m))
        # f_m = (f_m[0], 0)
        # print("f_m:", f_m)
        # print("m not in SG")
        # if not is_dominated(f_m, COSTS):
        # print("COSTS:", COSTS, f_m)
        if not is_dominated(COSTS, f_m):
            # print('f_m is not dominated by COSTS')
            OPEN.append((m, g_m, f_m))
            G_op[m] = {g_m}
            SG[m] = n
    else:
        # print('22222')
        # print(n, SG[m])
        if g_m in G_op.get(m, set()).union(G_cl.get(m, set())):
            # print('g_m in G_op.get(m, set()) or g_m in G_cl.get(m, set())')
            # m = m
            SG[m] = n
        elif not any(is_dominated(other, g_m) for other in G_op.get(m, set()).union(G_cl.get(m, set()))):
            # print('not any(is_dominated(g_m, other) for other in G_op.get(m, set()).union(G_cl.get(m, set())))')
            # eliminate_dominated(g_m, G_op.get(m, set()).union(G_cl.get(m, set())))
            G_op, G_cl, OPEN = eliminate_dominated(m, g_m, G_op, G_cl, OPEN)
            # f_m = tuple(sum(x) for x in zip(g_m, heuristic_function(m, end)))
            h_m = heuristic_function(m, end, graph, weights, time_windows, start_time, in_angles, out_angles, Stand,
                                     cost_of_path)
            f_m = tuple(sum(x) for x in zip(g_m, h_m))
            # f_m = (f_m[0], 0)

            if not is_dominated(COSTS, f_m):
                # print('f_m is not dominated by COSTS')
                OPEN.append((m, g_m, f_m))
                G_op[m] = {g_m}
                # if n not in Stand:
                SG[m] = n
        # print(SG)
    return n, m, g_n, f_n, SG, G_op, G_cl, OPEN, COSTS, end, costs, graph, time_windows, start_time, C_n_m, c_n_m_l, segment, holding_time