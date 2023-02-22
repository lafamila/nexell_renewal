from flask import Flask
from .controllers.index_view import bp as index_bp
from .controllers.dashboard_view import bp as dashboard_bp
from .controllers.member_view import bp as member_bp
from .controllers.approval_view import bp as approval_bp
from .controllers.project_view import bp as project_bp
from .controllers.stock_view import bp as stock_bp
from .controllers.sales_view import bp as sales_bp
from .controllers.goal_view import bp as goal_bp
from .controllers.work_view import bp as work_bp
from .controllers.tax_view import bp as tax_bp
from .controllers.common_view import bp as common_bp
from .controllers.api.member import bp as member_api_bp
from .controllers.api.dashboard import bp as dashboard_api_bp
from .controllers.api.project import bp as project_api_bp
from .controllers.api.approval import bp as approval_api_bp
from .controllers.api.stock import bp as stock_api_bp
from .controllers.api.dev_test import bp as dev_api
from .controllers.api.sales import bp as sales_api_bp
from .controllers.api.goal import bp as goal_api_bp
from .controllers.api.work import bp as work_api_bp
from .controllers.api.tax import bp as tax_api_bp
from .controllers.api.common import bp as common_api_bp
from .controllers.api.services import *
# from .controllers.ajax_controller import bp as ajax
# from .controllers.s2s_controller import bp as s2s
from flask.json import JSONEncoder

app = Flask(__name__)
app.secret_key = "asdfasdfasdfasdf"
app.register_blueprint(index_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(dashboard_api_bp)
app.register_blueprint(approval_bp)
app.register_blueprint(approval_api_bp)
app.register_blueprint(project_bp)
app.register_blueprint(project_api_bp)
app.register_blueprint(member_bp)
app.register_blueprint(member_api_bp)
app.register_blueprint(stock_bp)
app.register_blueprint(stock_api_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(sales_api_bp)
app.register_blueprint(goal_bp)
app.register_blueprint(goal_api_bp)
app.register_blueprint(work_bp)
app.register_blueprint(work_api_bp)
app.register_blueprint(tax_bp)
app.register_blueprint(tax_api_bp)
app.register_blueprint(common_bp)
app.register_blueprint(common_api_bp)
app.register_blueprint(dev_api)

app.jinja_env.globals.update(
    zip=zip,
    enumerate=enumerate,
    set_menu=set_menu,
    menus=list(),
    selng_ty_code_list=get_code_list('selng_ty_code'.upper()),
    prdlst_se_code_list=get_code_list('prdlst_se_code'.upper()),
    dept_code_list=get_code_list('dept_code'.upper()),
    puchas_ty_code_list=get_code_list('ct_se_code'.upper()),
    delng_se_code_list=get_code_list('delng_se_code'.upper()),
    ofcps_code_list=get_code_list('ofcps_code'.upper()),
    rspofc_code_list=get_code_list('rspofc_code'.upper()),
    prjct_ty_code_list=get_code_list('prjct_ty_code'.upper()),
    progrs_sttus_code_list=get_code_list('progrs_sttus_code'.upper()),
    approval_se_code_list=get_code_list('approval_se_code'.upper()),
    approval_ty_code_list=get_code_list('approval_ty_code'.upper()),
    mber_sttus_code_list=get_code_list('mber_sttus_code'.upper()),
    author_list=get_author_list(),
    bcnc_list=get_bcnc_list(),
    member_list=get_member_list(),
    prduct_ty_code_list=get_code_list('prduct_ty_code'.upper()),
    prduct_sse_code_list=get_code_list('prduct_sse_code'.upper()),
    invn_sttus_code_list=get_code_list('invn_sttus_code'.upper()),
    inventory_list=get_inventory_name_list(),
    contract_list=get_contract_list(),
    amt_ty_code_list=get_code_list('amt_ty_code'.upper())
)

