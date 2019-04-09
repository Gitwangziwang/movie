from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_redis import FlaskRedis
import pymysql
pymysql.install_as_MySQLdb()

db = SQLAlchemy()      # 实例化一个SQLAlchemy对象
migrate = Migrate()    # 实例化一个Migrate对象
redis = FlaskRedis()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'home.login'


def create_app():
    from .home.views import home    # 引入定义的蓝图，才能进行注册
    from .admin.views import admin

    app = Flask(__name__)          # 实例化一个FLASK对象
    app.debug = True               # debug为True，调试模式
    app.config.from_object('config')   # 指定配置文件config.py路径

    db.init_app(app)              # 初始化db
    migrate.init_app(app, db)     # 初始化migrate
    redis.init_app(app)           # 初始化redis
    login_manager.init_app(app)

    app.register_blueprint(home)  # 注册蓝图，此处不设置根路由
    app.register_blueprint(admin, url_prefix='/admin')

    return app                   # 这是一个函数，记得要返回app！！
