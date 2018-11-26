from logging.handlers import RotatingFileHandler
from info.utils.common import func_index_convert
from flask import Flask
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from config import Config, config_dict
import logging

db = None  # type:SQLAlchemy
sr = None  # type:StrictRedis

# 日志配置(将日志保存到文件中)
def setup_log(log_level):
    # 设置日志的记录等级
    logging.basicConfig(level=log_level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(pathname)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_type,):
    config_class = config_dict.get(config_type)
    app = Flask(__name__)
    app.config.from_object(config_class)
    global db, sr

    db = SQLAlchemy(app)
    sr = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT,decode_responses=True)
    # 创建session存储对象
    Session(app)
    Migrate(app, db)

    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)
    from info.modules.home import home_blu
    app.register_blueprint(home_blu)
    from info.modules.news import news_blu
    app.register_blueprint(news_blu)

    setup_log(config_class.LOG_LEVEL)
    # 管理表模型文件
    import info.models
    # 在utils中定义的函数想要变成过滤器，需要在app中注册，并且转换成过滤器
    app.add_template_filter(func_index_convert,"index_convert")

    return app