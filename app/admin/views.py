#! /usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Blueprint,render_template,redirect,flash,url_for,session,current_app,request
from app.admin.forms import TagForm,MovieForm,PreviewForm
from app.models.model import Tag,Movie,Preview,Comment,Moviecol,User
from app.app import db
import os,stat,datetime
from flask_login import logout_user,login_user,login_required,current_user

admin = Blueprint('admin', __name__)


@admin.context_processor                                   # 上下文处理器
def time():
    data = dict(
        online_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")      # 返回当前具体时间，可在任意页面进行使用
    )
    return data


@admin.route('/')
@admin.route('/index')
def index():
    role_id = session['role_id']
    if role_id != 2:
        return redirect(url_for('home.index'))
    return render_template('admin/index.html')


@admin.route("/add_tag", methods=["GET", "POST"])
@login_required
def add_tag():
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag = Tag(name=data["name"])
        db.session.add(tag)
        db.session.commit()
        flash("添加标签成功！")
        redirect(url_for('admin.add_tag'))
    return render_template("admin/add_tag.html", form=form)


@admin.route("/edit_tag/<int:id>", methods=["GET", "POST"])
@login_required
def edit_tag(id=None):
    form = TagForm()
    tag = Tag.query.get_or_404(id)           # 获取不到数据则报404错误
    if form.validate_on_submit():
        data = form.data
        tag.name = data["name"]
        db.session.commit()
        flash("修改标签成功！")
        redirect(url_for('admin.edit_tag', id=id))
    return render_template("admin/edit_tag.html", form=form, tag=tag)


@admin.route("/tag_list/<int:page>", methods=["GET"])
@login_required
def tag_list(page=None):
    if page is None:
        page = 1
    page_data = Tag.query.order_by(Tag.add_time.desc()).paginate(page=page, per_page=10)
    return render_template("admin/tag_list.html", page_data=page_data)


@admin.route("/del_tag/<int:id>", methods=["GET"])
@login_required
def del_tag(id=None):
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("删除标签成功！")
    return redirect(url_for('admin.tag_list', page=1))


@admin.route("/add_movie", methods=["GET", "POST"])
@login_required
def add_movie():
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        file_url = form.url.data.filename
        file_logo = form.logo.data.filename
        if not os.path.exists(current_app.config["UP_DIR"]):
            os.makedirs(current_app.config["UP_DIR"])
            os.chmod(current_app.config["UP_DIR"], stat.S_IRWXO)
        form.url.data.save(current_app.config["UP_DIR"] + file_url)
        form.logo.data.save(current_app.config["UP_DIR"] + file_logo)

        movie = Movie(
            title=data["title"],
            info=data["info"],
            star=int(data["star"]),
            play_num=0,
            comment_num=0,
            tag_id=int(data["tag_id"]),
            area=data["area"],
            release_time=data["release_time"],
            length=data["length"],
            url=file_url,
            logo=file_logo
        )
        db.session.add(movie)
        db.session.commit()
        flash("添加电影成功！")
        return redirect(url_for('admin.add_movie'))
    return render_template("admin/add_movie.html", form=form)


@admin.route("/movie_list/<int:page>", methods=["GET"])
@login_required
def movie_list(page=None):
    if page is None:
        page = 1
    page_data = Movie.query.join(Tag).filter(Tag.id == Movie.tag_id).order_by(Movie.add_time.desc()).paginate(page=page, per_page=10)
    return render_template("admin/movie_list.html", page_data=page_data)


@admin.route("/del_movie/<int:id>", methods=["GET"])
@login_required
def del_movie(id=None):
    movie = Movie.query.get_or_404(int(id))
    db.session.delete(movie)
    db.session.commit()
    flash("删除电影成功！")
    return redirect(url_for('admin.movie_list', page=1))


@admin.route("/edit_movie/<int:id>", methods=["GET", "POST"])
@login_required
def edit_movie(id=None):
    form = MovieForm()
    form.url.validators = []
    form.logo.validators = []
    movie = Movie.query.get_or_404(int(id))
    if request.method == "GET":
        form.info.data = movie.info
        form.tag_id.data = movie.tag_id
        form.star.data = movie.star
    if form.validate_on_submit():
        data = form.data
        file_url = form.url.data.filename
        file_logo = form.logo.data.filename
        if not os.path.exists(current_app.config["UP_DIR"]):
            os.makedirs(current_app.config["UP_DIR"])
            os.chmod(current_app.config["UP_DIR"], stat.S_IRWXO)
        form.url.data.save(current_app.config["UP_DIR"] + file_url)
        form.logo.data.save(current_app.config["UP_DIR"] + file_logo)

        movie.star = data["star"]
        movie.tag_id = data["tag_id"]
        movie.info = data["info"]
        movie.title = data["title"]
        movie.area = data["area"]
        movie.length = data["length"]
        movie.release_time = data["release_time"]
        movie.url = file_url
        movie.logo = file_logo
        db.session.commit()
        flash("修改电影成功！")
        return redirect(url_for('admin.edit_movie', id=id))
    return render_template("admin/edit_movie.html", form=form, movie=movie)


@admin.route("/add_preview", methods=["GET", "POST"])
@login_required
def add_preview():
    form = PreviewForm()
    if form.validate_on_submit():
        data = form.data
        file_logo = form.logo.data.filename
        if not os.path.exists(current_app.config["UP_DIR"]):
            os.makedirs(current_app.config["UP_DIR"])
            os.chmod(current_app.config["UP_DIR"], stat.S_IRWXO)
        form.logo.data.save(current_app.config["UP_DIR"] + file_logo)
        preview = Preview(
            title=data["title"],
            logo = file_logo
        )
        db.session.add(preview)
        db.session.commit()
        flash("添加预告成功！")
        return redirect(url_for('admin.add_preview'))
    return render_template("admin/add_preview.html", form=form)


@admin.route("/preview_list/<int:page>", methods=["GET"])
@login_required
def preview_list(page=None):
    if page is None:
        page = 1
    page_data = Preview.query.order_by(Preview.add_time.desc()).paginate(page=page, per_page=10)
    return render_template("admin/preview_list.html", page_data=page_data)


@admin.route("/del_preview/<int:id>", methods=["GET"])
@login_required
def del_preview(id=None):
    preview = Preview.query.get_or_404(int(id))
    db.session.delete(preview)
    db.session.commit()
    flash("删除预告成功！")
    return redirect(url_for('admin.preview_list', page=1))


@admin.route("/edit_preview/<int:id>", methods=["GET", "POST"])
@login_required
def edit_preview(id):
    form = PreviewForm()
    form.logo.validators = []
    preview = Preview.query.get_or_404(int(id))
    if request.method == "GET":
        form.title.data = preview.title
    if form.validate_on_submit():
        data = form.data
        if form.logo.data.filename != "":
            file_logo = form.logo.data.filename
            form.logo.data.save(current_app.config["UP_DIR"] + file_logo)
        preview.title = data["title"]
        db.session.commit()
        flash("修改预告成功！")
        return redirect(url_for('admin.edit_preview', id=id))
    return render_template("admin/edit_preview.html", form=form, preview=preview)


@admin.route("/user_list/<int:page>", methods=["GET"])
@login_required
def user_list(page=None):
    if page is None:
        page = 1
    page_data = User.query.order_by(User.add_time.desc()).paginate(page=page, per_page=10)    # 对会员进行分页，每页１０个
    return render_template("admin/user_list.html", page_data=page_data)


@admin.route("/user_view/<int:id>", methods=["GET"])
@login_required
def user_view(id=None):
    user = User.query.get_or_404(int(id))
    return render_template("admin/user_view.html", user=user)


@admin.route("/del_user/<int:id>", methods=["GET"])
@login_required
def del_user(id=None):
    user = User.query.get_or_404(int(id))
    db.session.delete(user)
    db.session.commit()
    flash("删除会员成功！")
    return redirect(url_for('admin.user_list', page=1))


@admin.route("/comment_list/<int:page>", methods=["GET"])
@login_required
def comment_list(page=None):
    if page is None:
        page = 1
    page_data = Comment.query.join(Movie).join(User).filter(Movie.id == Comment.movie_id,User.id == Comment.user_id).\
        order_by(Comment.add_time.desc()).paginate(page=page, per_page=10)
    return render_template("admin/comment_list.html", page_data=page_data)


@admin.route("/del_comment/<int:id>", methods=["GET"])
@login_required
def del_comment(id=None):
    comment = Comment.query.get_or_404(int(id))
    db.session.delete(comment)
    db.session.commit()
    flash("删除评论成功！")
    return redirect(url_for('admin.comment_list', page=1))


@admin.route("/moviecol_list/<int:page>", methods=["GET"])
@login_required
def moviecol_list(page=None):
    if page is None:
        page = 1
    page_data = Moviecol.query.join(Movie).join(User).filter(Movie.id == Moviecol.movie_id,User.id == Moviecol.user_id).\
        order_by(Moviecol.add_time.desc()).paginate(page=page, per_page=10)
    return render_template("admin/moviecol_list.html", page_data=page_data)


@admin.route("/del_moviecol/<int:id>", methods=["GET"])
@login_required
def del_moviecol(id=None):
    moviecol = Moviecol.query.get_or_404(int(id))
    db.session.delete(moviecol)
    db.session.commit()
    flash("删除收藏成功！")
    return redirect(url_for('admin.moviecol_list', page=1))
