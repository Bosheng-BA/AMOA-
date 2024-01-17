import sys
import os.path
import tkinter
import airport
import traffic
import hmi
import hmi2
import Initial_network
import RSA4CEPO2
import time
import datetime
import helpfunction
import Draw_path
import Sour_and_Des


def find_routing(the_airport, the_airport2, sour, des, flight, flightnum, network, pointcoordlist, network_cepo,
             in_angles, out_angles, in_angles_cepo, out_angles_cepo, node_lock_periods):

    if flight.departure == 'ZBTJ':
        start_time = flight.ttot - 600
    else:
        start_time = flight.aldt

    # flightnum = len(pathlist) + 1
    s = pointcoordlist.index(sour)
    d = pointcoordlist.index(des)

    """CEPO 寻路过程"""
    path_set, length_set, plist, t, v, path_activation_times = \
        RSA4CEPO2.main(network_cepo, in_angles_cepo, out_angles_cepo, s, d, flightnum, pointcoordlist,
                       the_airport2, network, start_time, node_lock_periods, the_airport2.points)

    Draw_path.create_matplotlib_figure(network_point=network, pointcoordlist=pointcoordlist, path=plist, stand=s,
                                       runway=d, flightnum=flightnum)

    return path_set, plist, path_activation_times



