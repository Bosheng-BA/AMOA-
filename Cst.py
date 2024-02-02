import os
# 打开并读取文件
file = 'gaptraffic-2018-09-29-new'
DATA_PATH = "/Users/小巴的工作台/BBS_WORK_SPACE/Python_Workspace/airport/Datas/DATA"
APT_FILE = os.path.join(DATA_PATH, "tianjin_new.txt")

airc_file_name = "/Users/小巴的工作台/BBS_WORK_SPACE/Python_Workspace/airport/Datas/traffic/acft_types.txt"

flight_file_name = "/Users/小巴的工作台/BBS_WORK_SPACE/Python_Workspace/airport/Datas/traffic/" + file + ".csv"

# 存储文件的位置
# file = 'gaptraffic-2019-08-07-new'
# 确保目录存在
# os.makedirs(file, exist_ok=True)