import pandas as pd

class Flight:
    def __init__(self, data, callsign, departure, arrivee, ttot, tldt, atot, aldt, type, wingspan, airline, qfu, parking, registration):
        self.data = data
        self.callsign = callsign
        self.departure = departure
        self.arrivee = arrivee
        self.ttot = ttot
        self.tldt = tldt
        self.atot = atot
        self.aldt = aldt
        self.type = type
        self.wingspan = wingspan
        self.airline = airline
        self.qfu = qfu
        self.parking = parking
        self.registration = registration

def read_flights(files_name):
    # 读取Excel文件
    df = pd.read_csv(files_name)

    # 创建一个空列表来存储Flight对象
    flights = []

    # 创建新的列
    df['start_taxi_time'] = df.apply(lambda row: row['TTOT'] - 600 if row['departure'] == 'ZBTJ' else row['ALDT'],
                                     axis=1)

    # 对DataFrame进行排序
    df_sorted = df.sort_values(by='start_taxi_time')
    df_sorted.to_csv("sorted_file11.csv", index=False)

    for index, row in df_sorted.iterrows():
        flight = Flight(row['data'], row['callsign'], row['departure'], row['arrivee'], row['TTOT'], row['TLDT'],
                        row['ATOT'], row['ALDT'], row['Type'], row['Wingspan'], row['Airline'],
                        row['QFU'], row['Parking'], row['registration'])
        flights.append(flight)
    return flights



