from flask import Flask
from .controllers.index_view import bp as index_bp
from .controllers.dashboard_view import bp as dashboard_bp
from .controllers.member_view import bp as member_bp
from .controllers.approval_view import bp as approval_bp
from .controllers.project_view import bp as project_bp
from .controllers.api.member import bp as member_api_bp
from .controllers.api.project import bp as project_api_bp
from .controllers.api.approval import bp as approval_api_bp
from .controllers.api.dev_test import bp as dev_api
from .controllers.api.services import *
# from .controllers.ajax_controller import bp as ajax
# from .controllers.s2s_controller import bp as s2s
from flask.json import JSONEncoder

app = Flask(__name__)
app.secret_key = "asdfasdfasdfasdf"
app.register_blueprint(index_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(approval_bp)
app.register_blueprint(approval_api_bp)
app.register_blueprint(project_bp)
app.register_blueprint(project_api_bp)
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
    prjct_ty_code_list=get_code_list('prjct_ty_code'.upper()),
    progrs_sttus_code_list=get_code_list('progrs_sttus_code'.upper()),
    approval_se_code_list=get_code_list('approval_se_code'.upper()),
    approval_ty_code_list=get_code_list('approval_ty_code'.upper()),
    author_list=get_author_list(),
    bcnc_list=get_bcnc_list(),
    member_list=get_member_list()
)

