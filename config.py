#! /usr/bin/env python
# -*- coding:utf-8 -*-
import os

CSRF_ENABLED = True    # CSRF_ENABLED 配置是为了激活 跨站点请求伪造保护
SECRET_KEY = 'af2fad8cfe1f4c5fac4aa5edf6fcc8f3'     # 设置session时需要

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:201554@127.0.0.1:3306/movie"      # 数据库配置
SQLALCHEMY_TRACK_MODIFICATIONS = False   # 跟踪数据库的修改
SQLALCHEMY_COMMIT_ON_TEARDOWN = True     # 该配置为True,则每次请求结束都会自动commit数据库的变动

REDIS_URL = "redis://127.0.0.1:6379/0"              # 数据缓存配置


UP_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "app/static/uploads/")     #文件路径配置
IG_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "app/static/uploads/users/")
