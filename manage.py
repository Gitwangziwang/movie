#! /usr/bin/env python
# -*- coding:utf-8 -*-
from flask import render_template
from flask_script import Manager
from app.app import create_app, db
from flask_migrate import MigrateCommand


app = create_app()
manage = Manager(app)       # 使用Manager更好的管理项目，实例化一个Manager对象，接收的是app
manage.add_command('db', MigrateCommand)


@manage.command
def create():            # 创建数据库
    db.create_all()
    return '数据库已创建'


@manage.command
def drop():                             # 删除数据库
    db.drop_all()
    return '数据库删除完成'


@app.errorhandler(404)                             # 404页面配置
def page_not_found(error):
    return render_template("home/404.html"), 404


@app.errorhandler(500)                             # 500页面配置
def internal_error(error):
    db.session.rollback()                          # 让数据库回滚到正常的工作状态
    return render_template('home/500.html'), 500


if __name__ == '__main__':
    manage.run()               # 运行项目
