#! /usr/bin/env python
# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms.fields import StringField,SubmitField,FileField,TextAreaField,SelectField
from wtforms.validators import DataRequired,ValidationError
from app.models.model import Tag,Movie


class TagForm(FlaskForm):
    name = StringField(
        label="名称",
        validators=[
            DataRequired("请输入标签！")
        ],
        description="标签",
        render_kw={
            "placeholder": "请输入标签名称！",
            'required': 'required',
        }
    )
    submit = SubmitField(
        label='添加',
    )

    def validate_name(self,field):
        tag = Tag.query.filter_by(name=field.data).first()
        if tag:
            raise ValidationError('标签已经存在！')


class MovieForm(FlaskForm):
    title = StringField(
        label="片名",
        validators=[
            DataRequired("请输入片名！")
        ],
        description="片名",
        render_kw={
            "placeholder": "请输入片名！",
            'required': 'required',
        }
    )
    url = FileField(
        label="文件",
        validators=[
            DataRequired("请上传文件！")
        ],
        description="文件",
    )
    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("请输入简介！")
        ],
        description="简介",
        render_kw={
            "placeholder": "请输入简介！",
            'required': 'required',
            "rows": 10
        }
    )
    logo = FileField(
        label="封面",
        validators=[
            DataRequired("请上传封面！")
        ],
        description="封面",
    )
    star = SelectField(
        label="星级",
        validators=[
            DataRequired("请选择星级！")
        ],
        coerce=int,
        choices=[(1, "1星"), (2, "2星"), (3, "3星"), (4, "4星"), (5, "5星")],
        description="星级",
    )
    tag_id = SelectField(
        label="标签",
        validators=[
            DataRequired("请选择标签！")
        ],
        coerce=int,
        choices='',
        description="标签",
    )
    area = StringField(
        label="地区",
        validators=[
            DataRequired("请输入地区！")
        ],
        description="地区",
        render_kw={
            "placeholder": "请输入地区！",
            'required': 'required',
        }
    )
    length = StringField(
        label="片长",
        validators=[
            DataRequired("请输入片长！")
        ],
        description="片长",
        render_kw={
            "placeholder": "请输入片长！",
            'required': 'required',
        }
    )
    release_time = StringField(
        label="上映时间",
        validators=[
            DataRequired("请选择上映时间！")
        ],
        description="上映时间",
        render_kw={
            "placeholder": "请选择上映时间！",
            'required': 'required',
        }
    )
    submit = SubmitField(
        label='添加',
    )

    def __init__(self, *args, **kwargs):                    # 数据库查询操作不能直接写在定义表单中，需要另写init方法
        self.tag_id.choices=[(v.id, v.name) for v in Tag.query.all()]
        super().__init__(*args, **kwargs)

    def validate_title(self,field):
        movie = Movie.query.filter_by(title=field.data).first()
        if movie:
            raise ValidationError('片名已经存在！')


class PreviewForm(FlaskForm):
    title = StringField(
        label="预告标题",
        validators=[
            DataRequired("请输入预告标题！")
        ],
        description="预告标题",
        render_kw={
            "placeholder": "请输入预告标题！",
            'required': 'required',
        }
    )
    logo = FileField(
        label="预告封面",
        validators=[
            DataRequired("请上传预告封面！")
        ],
        description="预告封面",
    )
    submit = SubmitField(
        label='添加',
    )

