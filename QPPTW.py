from heapdict import heapdict
import math
import heapq
import Cst
# fib_heap = heapdict()


def Readjustment_time_windows(graph, weights, time_windows, path):
    updated_time_windows = time_windows.copy()  # Create a copy of the original time windows

    for i, reservation in enumerate(path):
        if i == len(path)-1:
            break
        edge = (reservation[0], path[i+1][0])
        if reservation[0] == path[i+1][0]:
            continue
        for i, time_window in enumerate(updated_time_windows[edge]):
            aj_e, bj_e = time_window
            timein_f, timeout_f = reservation[1]

            if timeout_f <= aj_e:
                # Time-window is too late, move to the next conflicting edge
                break
            elif timein_f < bj_e:
                # Time-window is too early, move to the next conflicting edge
                continue
            elif timein_f < aj_e + weights[edge]:
                if bj_e - weights[edge] < timeout_f:
                    # Remove Fj_e from F(e)
                    updated_time_windows[edge].pop(i)
                else:
                    # Shorten the start of the time-window
                    updated_time_windows[edge][i] = (timeout_f, bj_e)
            else:
                if bj_e - weights[edge] < timeout_f:
                    # Shorten the end of the time-window
                    updated_time_windows[edge][i] = (aj_e, timein_f)
                else:
                    # Split the time-window
                    updated_time_windows[edge][i] = (aj_e, timein_f)
                    updated_time_windows[edge].insert(i + 1, (timeout_f, bj_e))
        # for edge in conflicting_edges[reservation]:

    return updated_time_windows


def QPPTW_algorithm(graph, weights, time_windows, source, target, start_time, in_angles, out_angles, Stand):
    # 初始化一个空的斐波那契堆
    # fib_heap = heapdict()
    global new_label
    heap = []

    # heap = []
    labels = {v: [] for v in graph.keys()}

    # Create initial label for the source vertex
    time_i = start_time = 0
    initial_label = (source, (start_time, float('inf')), None)
    # heapq.heappush(heap, (start_time, initial_label))
    labels[source].append(initial_label)

    heapq.heappush(heap, (start_time, initial_label))

    # 创建一个节点并插入堆中，使用时间作为键值
    # fib_heap[time_i] = initial_label
    pathlist = []

    while heap:
        # 分解标签 L 中的元素
        # min_time, min_label_L = heap.popitem()
        min_time, min_label_L = heapq.heappop(heap)
        # time_cost = 0

        current_time = min_time
        (current_vertex, (current_start, current_end), prev_label) = min_label_L

        # If the current vertex is the target, reconstruct the path and return
        if current_vertex == target:
            label_path = []
            label_path.append((current_vertex, (current_start, current_end), prev_label))
            time_cost = current_start - start_time
            while prev_label:
                label_path.append(prev_label)
                current_vertex, _, prev_label = prev_label
                # starttime = _[0]
                # print(starttime)
            label_path.reverse()
            # new_time_windows = Readjustment_time_windows(graph, weights, time_windows, path)
            path = [label[0] for label in label_path]
            return label_path, path, time_windows, time_cost

        if current_vertex != target:
            path_for_test = []
            path_for_test.append((current_vertex, (current_start, current_end), prev_label))
            new_prev = prev_label
            while new_prev:
                path_for_test.append(new_prev)
                current_vertex_, _, new_prev = new_prev
            path_for_test.reverse()
        path = [label[0] for label in path_for_test]
        pathlist.append(path)

        # Explore outgoing edges from the current vertex
        for edge in graph[current_vertex]:
            _, next_vertex = edge  # looking for the next vertex

            # 检查next_vertex是否在Stand中，并且不是目标点
            if next_vertex in Stand and next_vertex != target:
                continue

            if len(path_for_test) > 1:
                path = [label[0] for label in path_for_test]
                # print(path, current_vertex, next_vertex)
                ang_rad = out_angles[path[-2]][current_vertex] - in_angles[current_vertex][next_vertex]
                delta = math.cos(ang_rad)  # if len(path) > 1 else 1
                if (ang_rad / 3.141592653589793) == 1.5:
                    delta = 0  # 控制有1.5pi 等于0 实际为负数
            else:
                delta = 1
            if 0 <= delta:
                # 加入角度约束
                for window_start, window_end in time_windows[edge]:
                    if current_end < window_start:
                        break
                    new_start = max(window_start, current_start)  # Use edge as key
                    new_end = new_start + weights[edge]  # Use edge as key

                    # Create a new label
                    if new_end <= window_end:
                        new_label = (
                            next_vertex, (new_end, window_end),
                            (current_vertex, (current_start, current_end), prev_label))

                    # Check dominance with existing labels
                    dominated = False
                    for existing_label in labels[next_vertex]:
                        existing_start = existing_label[1][0]
                        existing_end = existing_label[1][1]
                        if existing_start < new_end and window_end <= existing_end:
                            dominated = True
                            break

                        if new_end <= existing_start and existing_end <= window_end:
                            labels[next_vertex].remove(existing_label)

                            if existing_label[1][0] in heap:
                                del heap[existing_label[1][0]]
                            break

                    if not dominated:
                        labels[next_vertex].append(new_label)
                        heapq.heappush(heap, (new_end, new_label))
    """path_for_test"""
    return None, pathlist, time_windows, float('inf')


def construct_labeled_path(graph, weights, time_windows, source, start_time, path):
    # 初始化标签字典
    labels = {v: [] for v in graph.keys()}

    # 创建起始点的初始标签
    initial_label = (source, (start_time, float('inf')), None)
    labels[source].append(initial_label)

    # 为路径中的每个顶点构建标签
    prev_label = initial_label
    for i in range(1, len(path)):
        current_vertex = path[i-1]
        next_vertex = path[i]
        edge = (current_vertex, next_vertex)

        # 计算到达下一个顶点的时间
        travel_time = weights[edge]
        current_start, _ = prev_label[1]
        arrival_time = current_start

        # 调整时间窗口
        next_travel_time = weights[(next_vertex, path[i + 1])] if i < len(path) - 1 else 0
        adjusted_end_time = arrival_time + (20 if next_travel_time > 20 else next_travel_time)

        # 更新标签
        new_label = (next_vertex, (arrival_time, adjusted_end_time), prev_label)
        labels[next_vertex].append(new_label)
        prev_label = new_label

        # 检查时间窗口约束
        for window_start, window_end in time_windows[edge]:
            if arrival_time < window_start:
                # 如果到达时间早于时间窗口开始，则等待
                arrival_time = window_start
            if window_start <= arrival_time <= window_end:
                # 如果到达时间在时间窗口内，则创建新标签
                new_label = (next_vertex, (arrival_time, arrival_time + travel_time), prev_label)
                labels[next_vertex].append(new_label)
                prev_label = new_label
                break

    # 重构目标点的路径
    final_path = []
    while prev_label:
        final_path.append(prev_label)
        _, _, prev_label = prev_label

    final_path.reverse()
    return final_path