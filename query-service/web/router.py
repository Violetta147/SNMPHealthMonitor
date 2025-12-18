from flask import Blueprint, render_template, redirect, url_for

web_bp = Blueprint("web", __name__)

@web_bp.route("/")
def index():
    # entry point
    return redirect(url_for("web.dashboard_default"))

@web_bp.route("/dashboard")
def dashboard_default():
    return render_template(
        "dashboard.html",
        sysname="viole",
        topic="systemstatus"
    )

@web_bp.route("/dashboard/<sysname>")
def dashboard_sys(sysname: str):
    return render_template(
        "dashboard.html",
        sysname=sysname,
        topic="systemstatus"
    )

@web_bp.route("/dashboard/<sysname>/<topic>")
def dashboard_topic(sysname: str, topic: str):
    return render_template(
        "dashboard.html",
        sysname=sysname,
        topic=topic
    )
