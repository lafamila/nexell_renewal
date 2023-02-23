from flask import Blueprint, render_template, make_response, session, redirect
from ..helpers import session_helper
bp = Blueprint('card', __name__, url_prefix='/card')

@bp.route('/')
@session_helper.session_check
def index_page():
    return render_template('card.html')
