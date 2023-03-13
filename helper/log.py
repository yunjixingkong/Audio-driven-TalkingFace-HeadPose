from loguru import logger

__all__ = [
    'logger',
]

logger.add("tmp/file_{time}.log", rotation="50 MB", retention="10 days", serialize=False, encoding='utf-8')

logger.info("Init logger")

# @logger.catch
# def func(x, y, z):
#     return 1 / (x + y + z)


# if __name__ == '__main__':
#     func(0, 1, -1)