# Production information
PRODUCT_NAME = 'FOOHU EDA'

# FTP connection
HOST = '127.0.0.1'
PORT = 8080
USER = 'admin'
PASSWD = ''

# initial interval to retrieve simulation status
RETR_SIM_STATUS_INTVL = 0.5  # second

# directories on FTP
# - simulation flow
FTP_SIM_NETLIST_DIR = r'F:\\netlists\\'
FTP_SIM_PASS_DIR = r'F:\\simProcessed\\'
FTP_SIM_FAIL_DIR = r'F:\\simFailed\\'
FH_SIM_PROC_DIR = r'H:\\wave\\'
FH_SIM_WAVE_DIR = r'H:\\wave\\Results\\'
FTP_SIM_WAVE_DIR = r'F:\\waves\\'

# - auto-layout flow
# FTP_LAY_NETLIST_DIR = r'F:\\LaGen\\netlists\\'
# 
# FTP_LAGEN_PATH = r'F:\\LaGen\\'
# FTP_LAGEN_S1_PATH = r'F:\\LaGen\\gdsS1\\'
# FTP_LAGEN_S2_PATH = r'F:\\LaGen\\gdsS2\\'
# 
# FH_LAY_NETLIST_PATH = r'H:\\LaGen\\netlists\\'
# FH_GDS_S1_PATH = r'H:\\LaGen\\gds_files\\gds_s1\\metal\\to_client\\'
# FH_GDS_S2_PATH = r'H:\\LaGen\\gds_files\\gds_s2\\metal\\'