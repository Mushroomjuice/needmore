import logging
from datetime import timedelta

from redis import StrictRedis


class Config:  # 封装应用的所有配置
    DEBUG = True  # 开启调试模式
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/hm_newscass"  # 数据库连接地址
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 是否追踪数据库变化
    REDIS_HOST = "127.0.0.1"  # redis的ip地址
    REDIS_PORT = 6379  # redis的端口
    SESSION_TYPE = "redis"  # 设置session存储的方式  redis 性能好 可以设置过期时间
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 设置保存数据的redis操作对象
    SESSION_USE_SIGNER = True  # 设置sessionid是否加密
    SECRET_KEY = "0uapub3iKhrMyb7MRSHlg8Jvjw0q09jIXDPzXytTVqlPa8meOJo2/Y3nQI0mx2Re"  # 应用秘钥
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=60)  # 设置session过期时间, 默认就支持设置过期时间
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 设置每次请求后, 数据库自动提交


# 针对不同的环境设置不同的配置信息(配置子类化)
class DevelopmentConfig(Config):  # 开发环境配置
    DEBUG = True
    LOG_LEVEL = logging.DEBUG  # 设置日志等级


class ProductConfig(Config):  # 生产环境配置
    DEBUG = False
    LOG_LEVEL = logging.ERROR  # 设置日志等级


config_dict = {
    "pro": ProductConfig,
    "dev": DevelopmentConfig
}