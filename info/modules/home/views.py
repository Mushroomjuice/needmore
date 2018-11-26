from flask import session, current_app, render_template, request, jsonify

from info.constants import HOME_PAGE_MAX_NEWS
from info.models import User, News, Category
from info.modules.home import home_blu
from info import sr
import logging  # python 内置的日志模块，可以将日志打印到控制台，我们需要将日志存在文件里面

from info.utils.response_code import RET, error_map


@home_blu.route('/')
def index():
    # 在根路由中判断用户是否登陆，显示不同界面
    # 取得session中的user_id
    user_id = session.get("user_id")
    user = None  # 如果用户没登陆user默认使用None  # type:User
    if user_id:
        try:
            user = User.query.get(user_id)  # 这里查询到的是一个user对象
        except BaseException as e:
            current_app.logger.info(e)
    # 转换用户数据
    user = user.to_dict() if user else None
    # 查询新闻排行列表
    news_list=[]
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(10).all()
    except BaseException as e:
        current_app.logger.info(e)
    news_list=[news.to_basic_dict() for news in news_list]  # 查询得到的是每一个新闻对象，调用转字典的方法
    # 查询所有的新闻分类
    # category=[]
    try:
        categorys = Category.query.all()
    except BaseException as e:
        current_app.logger.info(e)
        return jsonify(errno=RET.DBERR,errmgs=error_map[RET.DBERR])
    categorys=[categoty.to_dict() for categoty in categorys]
    return render_template("news/index.html", user=user, news_list=news_list, categorys=categorys)  # 把user.to_dict()当做参数传进模板，在模板中根据user的值进行渲染


@home_blu.route("/favicon.ico")
def favicon():
    # 显示网页小图标
    return current_app.send_static_file("news/favicon.ico")


@home_blu.route('/get_news_list')
def get_news_list():
    # 按分类查询新闻数据，每种分类数据按分页传递，并且倒序
    cid = request.args.get("cid")  # 分类id
    cur_page = request.args.get("cur_page")  # 当前页面
    per_count = request.args.get("per_count",HOME_PAGE_MAX_NEWS)  # 每页条数
    # 校验参数
    if not all([cid,cur_page]):
        return jsonify(errno=RET.PARAMERR,errmgs=error_map[RET.PARAMERR])
    # 格式转换，args.get()获取的市字符串
    try:
        cid = int(cid)
        cur_page = int(cur_page)
        per_count = int(per_count)
    except BaseException as e:
        current_app.logger.info(e)
        return  jsonify(errno=RET.PARAMERR,errmgs=error_map[RET.PARAMERR])
    # 按照分类id和页数查询新闻数据
    # 新闻分类虽然有最新的分类，但是在添加新闻的时候没有新闻是最新分类的，所有当要看最新分类新闻，需要临时给最新分类添加新闻
    filter_list=[]
    if cid != 1:
        filter_list.append(News.category_id==cid)
    try:
        # pn对象可以想象成很多张纸，上面记录了我们需要的新闻
        pn = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(cur_page,per_count)
    except BaseException as e:
        current_app.logger.info(e)
        return jsonify(errno=RET.DBERR,errmgs=error_map[RET.DBERR])
    # 将数据包装到json中
    data = {
        "news_list":[news.to_dict() for news in pn.items], # 使用json的时候需要将模型转成内置类型
        "total_page":pn.pages  # 总页数，可以高数前段一共多少也，当到低的时候不在请求
        }

    # else:
    #     try:
    #         pn = News.query.order_by(News.create_time.desc()).paginate(cur_page,per_count)
    #     except BaseException as e:
    #         current_app.logger.info(e)
    #         return jsonify(errno=RET.DBERR,errmgs=error_map[RET.DBERR])
    #     # 将数据包装到json中
    #     data = {
    #         "news_list":[news.to_dict() for news in pn.items], # 使用json的时候需要将模型转成内置类型
    #         "total_page":pn.pages}  # 总页数，可以高数前段一共多少也，当到低的时候不在请求


    return jsonify(errno=RET.OK,errmgs=error_map[RET.OK],data=data)




