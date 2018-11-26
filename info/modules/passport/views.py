import random
import re
from werkzeug.security import generate_password_hash
from info.constants import *
from flask import request, abort, current_app, make_response, jsonify, session
from info.libs.captcha.pic_captcha import captcha
# from info.libs.yuntongxun.sms import CCP  开发不需要真的发验证码
from info.models import User
from info.modules.passport import passport_blu
from info import sr, db
from info.utils import response_code
from info.utils.response_code import RET, error_map


@passport_blu.route('/get_img_code')
def get_img_code():
    # 获取图片验证码
    # 获取参数
    img_code_id = request.args.get("img_code_id")
    # 校验参数
    if not img_code_id:
        return abort(404)
    # 生成图片验证码
    img_name,img_code,img_bytes = captcha.generate_captcha()
    # 保存验证码和图片key , 设置过期时间，键值形式要符合要求
    try:
        sr.set("img_code_id"+img_code_id,img_code,ex=IMAGE_CODE_REDIS_EXPIRES)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)

    response = make_response(img_bytes)  # tpye:Response
    response.content_type = "image/jpeg"
    return response
    # 返回图片

@passport_blu.route('/get_sms_code',methods=['POST'])
def get_sms_code():
    # 获取短息验证码
    # 获取参数
    img_code_id = request.json.get("img_code_id")
    img_code = request.json.get("img_code")
    mobile = request.json.get("mobile")
    # 校验参数
    if not all([img_code,img_code_id,mobile]):
        return jsonify(errno=RET.OK,errmsg=error_map[RET.PARAMERR])

    if re.match(r"1[345678]\d{}$",mobile):
        return jsonify(errno=RET.OK,errmsg=error_map[RET.PARAMERR])
    try:
        real_img_code = sr.get("img_code_id"+img_code_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg=error_map(RET.DBERR))
    if real_img_code != img_code.upper():
        return jsonify(erorno=RET.PARAMERR,errmsg=error_map[RET.PARAMERR])
    # 发短信之前可以判断该用户是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except BaseException as e:
        current_app.logger.info(e)
        return jsonify(errno=RET.DBERR,errmsg=error_map(RET.DBERR))
    if user:
        return jsonify(errno=RET.DATAEXIST,errmgs=error_map[RET.DATAEXIST])


    # 发送短信
    rand_num = "%04d" % random.randint(0,9999)
    # response_code = CCP().send_template_sms('18516952650', ['1234', 5], 1)
    # if response_code != 0:
    #     return jsonify(errno=RET.THIRDERR,errmsg=error_map[RET.THIRDERR])
    #保存短信验证码
    try:
        sr.set("sms_code_id"+mobile, rand_num,ex=SMS_CODE_REDIS_EXPIRES)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmgs=error_map[RET.DBERR])
    current_app.logger.info("短信验证码：%s" % rand_num)
    # json返回

    return jsonify(errno=RET.OK,errmsg=error_map[RET.OK])

@passport_blu.route('/register',methods=['POST'])
def register():
    # 注册
    # 校验数据
    mobile = request.json.get("mobile")
    sms_code = request.json.get("sms_code")
    password = request.json.get("password")

    if not all([mobile,sms_code,password]):
        return jsonify(errno=RET.PARAMERR, errmgs=error_map[RET.PARAMERR])
    try:
        real_sms_code = sr.get("sms_code_id"+mobile)
    except BaseException as e:
        current_app.logger.info(e)
        return jsonify(errno=RET.DBERR,errmgs=error_map[RET.DBERR])
    if real_sms_code != sms_code:
        return jsonify(errno=RET.PARAMERR, errmgs=error_map[RET.PARAMERR])
    # 保存数据
    try:
        user = User()
        user.mobile = mobile
        user.nick_name=mobile
        # user.password = generate_password_hash(password)# 这样为了加密密码,但是通常不用这种方法
        user.password = password  # 定义用户模型的时候对password属性使用计算型属性
        db.session.add(user)
        db.session.commit()
    except BaseException as e :
        db.session.rollback()
        current_app.logger.info(e)
        return jsonify(errno=RET.DBERR,errmgs=error_map[RET.DBERR])
    # 注册成功对用户的信息进行保存
    session["user_id"]=user.id
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])

@passport_blu.route('/login',methods=['POST'])
def login():
    # 用户登陆，用户登陆的目的是保存用户的状态，为后面的各种操作建立条件
    # 校验手机号格式是否正确
    mobile = request.json.get("mobile")
    password = request.json.get("password")
    if not re.match(r"1[345678]\d{9}$",mobile):
        return jsonify(errno=RET.PARAMERR, errmgs=error_map[RET.PARAMERR])
    # 校验用户是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except BaseException as e:
        current_app.logger.info(e)
        return jsonify(errno=RET.DBERR,errmgs=error_map[RET.DBERR])
    if not user:
        return jsonify(errno=RET.NODATA,errmgs=error_map[RET.NODATA])
    # 校验密码是否正确
    if not user.check_password(password):
        return jsonify(errno=RET.PARAMERR, errmgs=error_map[RET.PARAMERR])
    # 走到这一步说明登陆参数校验完毕，并且可以登陆，进行状态记录
    session["user_id"]=user.id
    # json返回
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])

@passport_blu.route('/logout')
def logout():
    # 退出登陆，的实质就是删除session中的数据
    # 显示退出按钮说明用户已经登陆
    # session中保存的user_id
    session.pop("user_id",None)
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])
    #
