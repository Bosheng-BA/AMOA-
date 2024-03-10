import os
# 打开并读取文件
weight = [1, 0]
file = 'gaptraffic-2017-08-03-new'
DATA_PATH = "Datas/DATA"
APT_FILE = os.path.join(DATA_PATH, "tianjin_new.txt")

airc_file_name = "Datas/traffic/acft_types.txt"

flight_file_name = "Datas/traffic/" + file + ".csv"

flight_file_name_list = ['gaptraffic-2017-08-03-new.csv','gaptraffic-2017-08-06-new.csv',
                         'gaptraffic-2017-08-14-new.csv','gaptraffic-2017-08-17-new.csv',
                         'gaptraffic-2017-08-19-new.csv','gaptraffic-2018-07-18-new.csv',
                         'gaptraffic-2018-07-29-new.csv','gaptraffic-2018-09-29-new.csv',
                         'gaptraffic-2019-02-01-new.csv','gaptraffic-2019-08-07-new.csv',]

# 存储文件的位置
# file = 'gaptraffic-2019-08-07-new'
# 确保目录存在
# os.makedirs(file, exist_ok=True)