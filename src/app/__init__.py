from flask import Flask
from .controllers.index_view import bp as index_bp
from .controllers.dashboard_view import bp as dashboard_bp
from .controllers.member_view import bp as member_bp
from .controllers.api.member import bp as member_api_bp
from .controllers.api.dev_test import bp as dev_api
from .controllers.api.services import set_menu, get_code_list, get_author_list
# from .controllers.ajax_controller import bp as ajax
# from .controllers.s2s_controller import bp as s2s


app = Flask(__name__)
app.secret_key = "asdfasdfasdfasdf"
app.register_blueprint(index_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(member_bp)
app.register_blueprint(member_api_bp)
app.register_blueprint(dev_api)

app.jinja_env.globals.update(
    zip=zip,
    enumerate=enumerate,
    set_menu=set_menu,
    menus=list(),
    dept_code_list=get_code_list('dept_code'.upper()),
    ofcps_code_list=get_code_list('ofcps_code'.upper()),
    rspofc_code_list=get_code_list('rspofc_code'.upper()),
    author_list=get_author_list(),
)