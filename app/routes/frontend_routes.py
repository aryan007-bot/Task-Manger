"""
Frontend routes — serve Jinja2 templates for the SPA-like UI.
"""
from flask import Blueprint, render_template

frontend_bp = Blueprint("frontend", __name__)


@frontend_bp.get("/")
def index():
    return render_template("login.html")


@frontend_bp.get("/login")
def login_page():
    return render_template("login.html")


@frontend_bp.get("/register")
def register_page():
    return render_template("register.html")


@frontend_bp.get("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")
