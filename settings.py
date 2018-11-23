import easy_env
 
PAUSE = easy_env.get_int('PAUSE', 10)
CALC_TIME = easy_env.get_int('CALC_TIME', 15)
DONE_TIME = easy_env.get_int('DONE_TIME', 300)
VCPU_COUNT = easy_env.get_int('VCPU_COUNT', 2)
IMAGE_ID = easy_env.get_str('IMAGE_ID', 'ami-09c509c5afd31ced6')
INSTANCE_TYPE = easy_env.get_str('INSTANCE_TYPE', 't2.micro')
INSTANCE_TAG = easy_env.get_str('INSTANCE_TAG', 'ForBacktests')
MAX_INSTANCES = easy_env.get_int('MAX_INSTANCES', 0)
REGION_NAME = easy_env.get_str('REGION_NAME', 'eu-west-1')
SPOT_MARKET = easy_env.get_bool('SPOT_MARKET', False) 