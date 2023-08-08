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
from .controllers.fund_view import bp as fund_bp
from .controllers.card_view import bp as card_bp
from .controllers.completed_view import bp as completed_bp
from .controllers.energy_view import bp as energy_bp
from .controllers.common_view import bp as common_bp
from .controllers.bbs_view import bp as bbs_bp
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
from .controllers.api.fund import bp as fund_api_bp
from .controllers.api.card import bp as card_api_bp
from .controllers.api.completed import bp as completed_api_bp
from .controllers.api.energy import bp as energy_api_bp
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
app.register_blueprint(fund_bp)
app.register_blueprint(fund_api_bp)
app.register_blueprint(card_bp)
app.register_blueprint(card_api_bp)
app.register_blueprint(completed_bp)
app.register_blueprint(completed_api_bp)
app.register_blueprint(energy_bp)
app.register_blueprint(energy_api_bp)
app.register_blueprint(common_bp)
app.register_blueprint(common_api_bp)
app.register_blueprint(bbs_bp)
# app.register_blueprint(bbs_api_bp)
app.register_blueprint(dev_api)

app.jinja_env.globals.update(
    zip=zip,
    enumerate=enumerate,
)

