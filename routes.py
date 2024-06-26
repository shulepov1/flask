from app_file import app
from flask import render_template
from browsers_app.forms import SearchForm
from browsers_app.models import Permission


@app.errorhandler(404)
def page_not_found(e):
    """
    page for 404 error
    """
    return render_template("/404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    """
    page for 500 error
    """
    return render_template("500.html"), 500


@app.errorhandler(405)
def method_not_allowed(e):
    """
    page for 405 error, method not found
    """
    return render_template("/405.html"), 405

@app.context_processor
def base():
    """
    передавать form в base.html -> navbar.html темплейты
    """
    form = SearchForm()
    return dict(form=form, Permission=Permission)
