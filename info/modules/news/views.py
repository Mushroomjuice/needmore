from flask import current_app, jsonify, abort, render_template, session, g

from info.models import News, User
from info.modules.news import news_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET, error_map


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    # 查看新闻详情,每次浏览，新闻的点击量加一
    user = g.user
    # user = user.to_dict() if user else None
    try:
        news = News.query.get(news_id)  #
    except BaseException as e:
        current_app.logger.info(e)
        # return jsonify(errno=RET.DBERR,errmgs=error_map[RET.DBERR])
        return  abort(500)
        # 按照点击量查询排行前10的新闻数据
    # 点击量+1
    news.clicks += 1
    news_list = []
    # 在新闻详情页再次查询新闻排行，并显示
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(10).all()
    except BaseException as e:
        current_app.logger.error(e)

    news_list = [news.to_basic_dict() for news in news_list]
    return  render_template("news/detail.html",news=news.to_dict(),news_list=news_list,user=user)