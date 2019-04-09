#! /usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Blueprint, render_template,flash,redirect,url_for,request,session,current_app,jsonify
from .forms import LoginForm, RegisterForm,ChangePwdForm,UserInfoForm,CommentForm
from app.models.model import User,Tag,Movie,Comment,Moviecol,Preview
from app.app import db,redis
import uuid, os, stat, json, datetime
from flask_login import current_user,login_user,logout_user,login_required
import traceback
from app.lib.common import falseReturn,trueReturn


home = Blueprint('home', __name__)     # 定义蓝图


@home.route("/<int:page>", methods=["GET"])
@home.route("/index", methods=["GET"])          # 一个视图函数定义两个路由
@login_required
def index(page=None):
    tags = Tag.query.all()                # 查询所有数据
    page_data = Movie.query
    # 标签
    tid = request.args.get("tid", 0)        # 获取'tid'数据，没有则为0
    if int(tid) != 0:
        page_data = page_data.filter_by(tag_id=int(tid))
    # 星级
    star = request.args.get("star", 0)
    if int(star) != 0:
        page_data = page_data.filter_by(star=int(star))
    # 时间
    time = request.args.get("time", 0)
    if int(time) != 0:
        if int(time) == 1:
            page_data = page_data.order_by(Movie.add_time.desc())   # 逆序排列
        else:
            page_data = page_data.order_by(Movie.add_time.asc())    # 正序排列
    # 播放量
    pm = request.args.get("pm", 0)
    if int(pm) != 0:
        if int(pm) == 1:
            page_data = page_data.order_by(Movie.play_num.desc())
        else:
            page_data = page_data.order_by(Movie.play_num.asc())
    # 评论量
    cm = request.args.get("cm", 0)
    if int(cm) != 0:
        if int(cm) == 1:
            page_data = page_data.order_by(Movie.comment_num.desc())
        else:
            page_data = page_data.order_by(Movie.comment_num.asc())
    if page is None:
        page = 1
    page_data = page_data.paginate(page=page, per_page=8)      # 分页
    p = dict(
        tid=tid,
        star=star,
        time=time,
        pm=pm,
        cm=cm,
    )
    return render_template("home/index.html", tags=tags, p=p, page_data=page_data)


@home.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():                    # 如果验证通过，则注册成功，将用户存进数据库
        data = form.data
        user = User()                            # 实例化User
        user.username = data['username']     # form.data[''] 、request.form['']和request.form.get('')都可以获取form表单数据
        user.email = data['email']
        user.phone = data['phone']
        user.uuid = uuid.uuid4().hex         # 通用唯一识别码
        user.role_id = data['role_id']
        user.set_password(data['pwd']),
        db.session.add(user)                  # 插入数据至User表
        db.session.commit()                   # 确认
        flash("注册成功!")              # flash('消息','flag')
        return redirect(url_for('home.login'))            # 注册成功重定向至登录页面
    return render_template('home/register.html', form=form)


@home.route('/login', methods=['GET', 'POST'])   # 默认是"GET"请求，"POST"请求需要特别说明,'/login'不要忘记'/'啊啊！！
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        username = data['username']
        user = User.query.filter_by(username=username).first()    # 查询符合条件的第一条数据
        if not user:
            flash('用户名不存在')                 # 此处error要和前端模板的值对应才有效果！！
            return redirect(url_for('home.login'))
        if not user.check_password(data['pwd']):
            flash('密码错误')
            return redirect(url_for('home.login'))
        login_user(user)                                  # 用户登录
        session['role_id'] = user.role_id
        return redirect(url_for('home.index'))
    return render_template('home/login.html', form=form)   # 将form表单传至前端


@home.route("/logout")                              # 登出，删除session中保存的 role_id
@login_required
def logout():
    logout_user()
    session.pop('role_id',None)
    return redirect(url_for("home.login"))


@home.route("/change_pwd", methods=["GET", "POST"])
@login_required
def change_pwd():
    form = ChangePwdForm()
    username = current_user.username
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(username=username).first()
        user.set_password(data['new_pwd'])               # 重新设置密码,不需要重新db.session.add(user)
        db.session.commit()
        flash("修改密码成功，请重新登录！")
        return redirect(url_for('home.logout'))
    return render_template("home/changepwd.html", form=form)


@home.route("/userinfo", methods=["GET", "POST"])
@login_required
def userinfo():
    form = UserInfoForm()
    username = current_user.username
    user = User.query.filter_by(username=username).first()

    if request.method == "GET":                # 刚开始时，表单默认显示用户已经存在的信息
        form.username.data = user.username
        form.email.data = user.email
        form.phone.data = user.phone
        form.info.data = user.info
    if form.validate_on_submit():
        data = form.data
        filename = form.image.data.filename             # 获取文件名
        if not os.path.exists(current_app.config["IG_DIR"]):
            os.makedirs(current_app.config["IG_DIR"])
            os.chmod(current_app.config["IG_DIR"], stat.S_IRWXO)            # os.chmod用于更改文件或目录的权限
        form.image.data.save(current_app.config["IG_DIR"] + filename)       # form.image.data.save()保存文件

        n_user = User.query.filter_by(username=data["username"]).first()
        if n_user and data["username"] != user.username:     # 如果输入的名称不是现在这个，而且数据库中查询到
            flash("昵称已经存在！")
            return redirect(url_for("home.userinfo"))

        e_user = User.query.filter_by(email=data["email"]).first()
        if e_user and data["email"] != user.email:
            flash("邮箱已经存在！")
            return redirect(url_for("home.userinfo"))

        p_user = User.query.filter_by(phone=data["phone"]).first()
        if p_user and data["phone"] != user.phone:
            flash("手机号码已经存在！")
            return redirect(url_for("home.userinfo"))

        user.username = data["username"]
        user.email = data["email"]
        user.phone = data["phone"]
        user.info = data["info"]
        user.image = filename
        db.session.commit()
        flash("修改成功！")
        return redirect(url_for("home.userinfo"))
    return render_template("home/userinfo.html", form=form, user=user)


@home.route("/comments/<int:page>")
@login_required
def comments(page=None):                  # query.join 多表联合查询 , paginate分页
    try:
        if page is None:
            page = 1
        page_data = Comment.query.join(Movie).join(User).filter(Movie.id == Comment.movie_id,User.id == current_user.id).\
            order_by(Comment.add_time.desc()).paginate(page=page, per_page=10)
    except:
        print('traceback.format_exc():\n%s' % traceback.format_exc())
        return jsonify(falseReturn('','服务器错误'))
    return render_template("home/comments.html", page_data=page_data)


@home.route("/add_moviecol", methods=["GET"])
@login_required
def add_moviecol():
    uid = request.args.get("uid", "")
    mid = request.args.get("mid", "")
    moviecol = Moviecol.query.filter_by(user_id=int(uid),movie_id=int(mid)).first()
    if moviecol:
        data = {
            'ok': 0
        }
    else:
        moviecol = Moviecol(user_id=int(uid),movie_id=int(mid))
        db.session.add(moviecol)
        db.session.commit()
        data = {
            'ok': 1
        }
    return jsonify(data)


@home.route("/moviecol/<int:page>")
@login_required
def moviecol(page=None):
    if page is None:
        page = 1
    page_data = Moviecol.query.join(Movie).join(User).filter(Movie.id == Moviecol.movie_id,User.id == current_user.id).\
        order_by(Moviecol.add_time.desc()).paginate(page=page, per_page=10)
    return render_template("home/moviecol.html", page_data=page_data)


@home.route("/animation/")
@login_required
def animation():
    data = Preview.query.all()
    return render_template("home/animation.html", data=data)


@home.route("/search/<int:page>")
@login_required
def search(page=None):
    if page is None:
        page = 1
    key = request.args.get("key", "")
    movie_count = Movie.query.filter(Movie.title.ilike('%' + key + '%')).count()
    page_data = Movie.query.filter(Movie.title.ilike('%' + key + '%')).\
        order_by(Movie.add_time.desc()).paginate(page=page, per_page=10)
    page_data.key = key
    return render_template("home/search.html", movie_count=movie_count, key=key, page_data=page_data)


@home.route("/play/<int:id>/<int:page>", methods=["GET", "POST"])
@login_required
def play(id=None, page=None):
    movie = Movie.query.join(Tag).filter(Tag.id == Movie.tag_id,Movie.id == int(id)).first_or_404()
    if page is None:
        page = 1
    page_data = Comment.query.join(Movie).join(User).filter(Movie.id == movie.id,User.id == Comment.user_id).\
        order_by(Comment.add_time.desc()).paginate(page=page, per_page=10)

    movie.play_num = movie.play_num + 1
    form = CommentForm()
    if form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data["content"],
            movie_id=movie.id,
            user_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        movie.comment_num = movie.comment_num + 1
        db.session.add(movie)
        db.session.commit()
        flash("添加评论成功！")
        return redirect(url_for('home.play', id=movie.id, page=1))
    db.session.add(movie)
    db.session.commit()
    return render_template("home/play.html", movie=movie, form=form, page_data=page_data)


@home.route("/video/<int:id>/<int:page>", methods=["GET", "POST"])
@login_required
def video(id=None, page=None):
    movie = Movie.query.join(Tag).filter(Tag.id == Movie.tag_id,Movie.id == int(id)).first_or_404()
    if page is None:
        page = 1
    page_data = Comment.query.join(Movie).join(User).filter(Movie.id == movie.id,User.id == Comment.user_id).\
        order_by(Comment.add_time.desc()).paginate(page=page, per_page=10)

    movie.play_num = movie.play_num + 1
    form = CommentForm()
    if form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data["content"],
            movie_id=movie.id,
            user_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        movie.comment_num = movie.comment_num + 1
        db.session.add(movie)
        db.session.commit()
        flash("添加评论成功！")
        return redirect(url_for('home.video', id=movie.id, page=1))
    db.session.add(movie)
    db.session.commit()
    return render_template("home/video.html", movie=movie, form=form, page_data=page_data)


@home.route("/barrage", methods=["GET", "POST"])
@login_required
def barrage():
    if request.method == "GET":
        id = request.args.get('id')
        key = "movie" + str(id)
        if redis.llen(key):                   # redis.llen返回列表的长度，如果没有则返回空值
            msgs = redis.lrange(key, 0, 2999)    # redis.lrange返回列表中的元素，0-2999
            res = {
                "code": 1,
                "danmaku": [json.loads(v) for v in msgs]    # json.loads()函数是将json格式数据转换为字典
            }
        else:
            res = {
                "code": 1,
                "danmaku": []
            }
    else:
        data = json.loads(request.get_data())
        msg = {
            "__v": 0,
            "author": data["author"],
            "time": data["time"],
            "text": data["text"],
            "color": data["color"],
            "type": data['type'],
            "ip": request.remote_addr,
            "_id": datetime.datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex,
            "player": [
                data["player"]
            ]
        }
        res = {
            "code": 1,
            "data": msg
        }
        redis.lpush("movie" + str(data["player"]), json.dumps(msg))   # redis.lpush将一个或多个值插入到列表头部
    return jsonify(trueReturn(res,'200'))
