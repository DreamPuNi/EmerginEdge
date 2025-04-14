import os
import logging

# TODO: 把日志等级提到参数里面

LOG_DIR = 'log'
os.makedirs(LOG_DIR,exist_ok=True)

logger = logging.getLogger("EmerginEdge")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

#file_handler = logging.FileHandler(os.path.join(LOG_DIR, 'app.log'))
#file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s] - [%(module)s:%(lineno)d] - [%(levelname)s] : %(message)s')
console_handler.setFormatter(formatter)
#file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
#logger.addHandler(file_handler)