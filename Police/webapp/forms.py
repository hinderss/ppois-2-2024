from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired


class WelcomeForm(FlaskForm):
    city = StringField('Город', validators=[
        InputRequired()])
    name = StringField('Имя', validators=[
        InputRequired()])
    submit = SubmitField('Сохранить')

