from wtforms import Form, StringField, PasswordField, SubmitField, validators


class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    login = SubmitField('Log in')
