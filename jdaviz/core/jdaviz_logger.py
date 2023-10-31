import logging
from functools import wraps

'''
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("test_logging.log"),
        logging.StreamHandler()
    ]
)
'''

logger = logging.getLogger('jdaviz')
logger.setLevel(logging.INFO)
FileOutputHandler = logging.FileHandler('test_logging.log')
logger.addHandler(FileOutputHandler)


def method_logger(func):

    @wraps(func)
    def new_func(*args, **kwargs):
        saved_args = locals()
        class_name = saved_args['args'][0].__class__
        logger.info(f"Called {class_name}.{saved_args['func'].__name__} with arguments"
                     f"{saved_args['args'][1:]} and kwargs {saved_args['kwargs']}")

        return func(*args, **kwargs)

    return new_func
