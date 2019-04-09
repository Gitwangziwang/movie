#! /usr/bin/env python
# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,TextAreaField,SelectField
from wtforms.validators import DataRequired,Email,Regexp,EqualTo,Length,ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app.models.model import User
from flask_login import current_user


class RegisterForm(FlaskForm):
    username = StringField(
        label='用户名',
        validators=[
            DataRequired('请输入用户名')
        ],
        description='用户名',
        render_kw={
            'placeholder': '请输入用户名',
            'required': 'required',
        }
    )
    role_id = SelectField(
        label="用户角色",
        validators=[
            DataRequired("请选择用户角色！")
        ],
        coerce=int,
        choices=[(1, "会员"), (2, "管理员")],
        description="用户角色",
    )
    email = StringField(
        label='邮箱',
        validators=[
            DataRequired('请输入邮箱'),
            Email('邮箱格式不正确')      # Email 验证邮箱格式
        ],
        description='邮箱',
        render_kw={
            'placeholder': '请输入邮箱',
            'required': 'required',
        }
    )
    phone = StringField(
        label='手机',
        validators=[
            DataRequired('请输入手机号码'),
            Regexp(r'^1[3456789]\d{9}$', message='手机号格式不正确')    # Regexp 正则匹配手机号码
        ],
        description='手机',
        render_kw={
            'placeholder': '请输入手机号',
            'required': 'required'
        }
    )
    pwd = PasswordField(
        label='密码',
        validators=[
            DataRequired('请输入密码'),
            Length(min=8, max=20, message='密码长度需在8-20之间'),     # Length 密码长度限制在8-20之间
            Regexp(r'^(?:(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])).*$', message='密码需同时包含大小写与数字')    # 正则匹配密码
        ],
        description='密码',
        render_kw={
            'placeholder': '请输入密码',
            'required': 'required',
        }
    )
    repwd = PasswordField(
        label='确认密码',
        validators=[
            DataRequired('请再次输入密码'),
            EqualTo('pwd',message='两次密码不一致')
        ],
        description='确实密码',
        render_kw={
            'placeholder': '请再次输入密码',
            'required': 'required',
        }
    )
    submit = SubmitField(
        label='注册',
    )

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()       # 验证用户名是否已经存在
        if user:
            raise ValidationError('用户名已经存在')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()        # 验证用户名是否已经存在
        if user:
            raise ValidationError('邮箱已经存在')

    def validate_phone(self, field):
        user = User.query.filter_by(phone=field.data).first()        # 验证用户名是否已经存在
        if user:
            raise ValidationError('手机号已经被注册')


class LoginForm(FlaskForm):
    username = StringField(
        label='用户名',
        validators=[
            DataRequired('请输入用户名')
        ],
        description="用户名",
        render_kw={  # 附加选项
            "placeholder": "请输入用户名",
            "required": "required",  # 添加强制属性，H5会在前端验证
        }
    )
    pwd = PasswordField(
        label='密码',
        validators=[
            DataRequired('请输入密码')
        ],
        description='密码',
        render_kw={
            "placeholder": "请输入密码",
            "required": "required",
        }
    )
    submit = SubmitField(
        label='登录',
    )


class ChangePwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("请输入旧密码！")
        ],
        description="旧密码",
        render_kw={
            "placeholder": "请输入旧密码！",
            "required": "required",
        }
    )
    new_pwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("请输入新密码！")
        ],
        description="新密码",
        render_kw={
            "placeholder": "请输入新密码！",
            "required": "required",
        }
    )
    repwd = PasswordField(
        label='确认密码',
        validators=[
            DataRequired('请再次输入密码'),
            EqualTo('new_pwd', message='两次密码不一致')
        ],
        description='确认密码',
        render_kw={
            'placeholder': '请再次输入密码',
            'required': 'required',
        }
    )
    submit = SubmitField(
        label='提交',
    )

    def validate_old_pwd(self,field):
        username = current_user.username
        user = User.query.filter_by(username=username).first()
        if not user.check_password(field.data):
            raise ValidationError('旧密码错误')

    def validate_new_pwd(self, field):
        old_pwd = self.old_pwd.data
        if field.data == old_pwd:
            raise ValidationError('新密码与旧密码不能相同')


class UserInfoForm(FlaskForm):
    username = StringField(
        label="用户名",
        validators=[
            DataRequired("请输入用户名！")
        ],
        description="用户名",
        render_kw={
            "placeholder": "请输入用户名！",
            'required': 'required',
        }
    )
    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱！"),
            Email("邮箱格式不正确！")
        ],
        description="邮箱",
        render_kw={
            "placeholder": "请输入邮箱！",
            'required': 'required',
        }
    )
    phone = StringField(
        label="手机",
        validators=[
            DataRequired("请输入手机！"),
            Regexp(r'^1[3456789]\d{9}$', message='手机号格式不正确')
        ],
        description="手机",
        render_kw={
            "placeholder": "请输入手机！",
            'required': 'required',
        }
    )
    image = FileField(
        label="头像",
        validators=[
            FileRequired("请上传头像！"),
            FileAllowed(['jpg', 'png'], 'Images only!')
        ],
        description="头像",
    )
    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("请输入简介！")
        ],
        description="简介",
        render_kw={
            "rows": 10,
            'required': 'required',
        }
    )
    submit = SubmitField(
        '保存修改',
    )


class CommentForm(FlaskForm):
    content = TextAreaField(
        label="内容",
        validators=[
            DataRequired("请输入内容！"),
        ],
        description="内容",
    )
    submit = SubmitField(
        label='提交评论',
    )
