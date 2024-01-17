import gaptraffic
import airc_type
import Cst

filename = Cst.flight_file_name
flights = gaptraffic.read_flights(filename)
airc_type_dict = airc_type.airc_type_dict
Heavy = ["RH", "SH", "TH"]
Middle_and_Light = ["RM", "TM", "TL"]


def stand_and_runway_points(points):
    stand_list = []
    stand_dict = {}
    stand_dict2 = {}
    runway_list = []
    runway_dict = {}
    runway_dict2 = {}
    for p in points:
        if p.ptype == "Stand":
            stand_list.append(p.xy)
            stand_dict[p.name] = p.xy
            stand_dict2[p.xy] = p.name
        elif p.ptype == "Runway":
            runway_list.append(p.xy)
            runway_dict[p.name] = p.xy
            runway_dict2[p.xy] = p.name
    return stand_dict, runway_dict, stand_list, stand_dict2, runway_list, runway_dict2


def find_the_sour_des(stands, pists, flight):
    if flight.departure == "ZBTJ":  # 天津起飞
        # spoint = parking_to_point(points, flight.parking)  # 此时是停机坪号
        sour = stands[flight.parking]
        arcftype = airc_type_dict[flight.type]
        if flight.qfu == "16R":
            if arcftype in Heavy:
                if sour[1] > 6926:
                    des = pists['B7']  # B7
                elif sour[1] < 6926:
                    des = pists['A10']  # A10
            elif arcftype in Middle_and_Light:
                des = (20155, 6926)  # 16R-34L
        elif flight.qfu == "16L":
            des = (21057, 9026)  # 16L-34R
        elif flight.qfu == "34L":
            if sour[1] > 6926:
                des = (23610, 6926)  # 16R-34L
            elif sour[1] < 6926:
                des = pists['A1']  # A1
        elif flight.qfu == "34R":
            des = (24018, 9026)  # 16L-34R
    elif flight.arrivee == "ZBTJ":  # 天津降落
        # despoint = parking_to_point(points, flight.parking)  # 此时是停机坪号
        des = stands[flight.parking]
        arcftype = airc_type_dict[flight.type]
        if flight.qfu == "16R":
            if arcftype in Heavy:
                if des[1] > 6926:
                    sour = pists['B3']  # B3
                elif des[1] < 6926:
                    sour = pists['A1']  # A1
            elif arcftype in Middle_and_Light:
                if des[1] > 6926:
                    sour = pists['B4']  # B4
                elif des[1] < 6926:
                    sour = pists['A5']  # A5
        elif flight.qfu == "16L":
            sour = pists['W3']  # W3
        elif flight.qfu == "34L":
            if des[1] > 6926:
                if arcftype in Heavy:
                    sour = pists['B6']  # B6
                elif arcftype in Middle_and_Light:
                    sour = pists['B5']  # B5
            elif des[1] < 6926:
                sour = pists['A10']  # A10
        elif flight.qfu == "34R":
            if arcftype in Heavy:
                sour = pists['W8']  # W8
            elif arcftype in Middle_and_Light:
                sour = pists['W7']  # W7
    return sour, des

