from flask import Flask
from .controllers.index_view import bp as index_bp
from .controllers.api.account import bp as account_api_bp
# from .controllers.ajax_controller import bp as ajax
# from .controllers.s2s_controller import bp as s2s


app = Flask(__name__)
app.secret_key = "asdfasdfasdfasdf"
app.register_blueprint(index_bp)
app.register_blueprint(account_api_bp)

app.jinja_env.globals.update(
    zip=zip,
    enumerate=enumerate,
)