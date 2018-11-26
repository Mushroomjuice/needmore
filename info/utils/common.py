# 自定义公共文件
import functools
from flask import session, current_app, g

from info.models import User


def func_index_convert(value):  # value = 1, 自定义的过滤器，用来转换前段对应的类名,定义函数后去app中注册
    index_dict = {1: "first", 2: "second", 3: "third"}
    return index_dict.get(value, "")

def user_login_data(f):
    @functools.wraps(f)
    def wrapper(*args,**kwargs):
        # 判断用户是否登录  取出session中的user_id
        user_id = session.get("user_id")
        user = None  # type: User
        if user_id:  # 已登录
            # 查询用户数据
            try:
                user = User.query.get(user_id)
            except BaseException as e:
                current_app.logger.error(e)

        # 将用户信息保存到g变量
        g.user = user
        return f(*args,**kwargs)
    return wrapper