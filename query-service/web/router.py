from flask import Blueprint, render_template, redirect, url_for, request, abort

web_bp = Blueprint("web", __name__, url_prefix="/web")

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


@web_bp.route("/dashboard/partial/<topic>")
def dashboard_partial(topic: str):
    """Return only the partial HTML for a topic (used by SPA fetch).

    This endpoint renders the topic partial directly (no base template). The
    frontend calls `/web/dashboard/partial/<topic>?sysname=...` to get the
    fragment and inject it into the main container. Returning only the
    partial avoids accidentally embedding full-page markup into the
    dashboard main container.
    """
    sysname = request.args.get('sysname', 'viole')

    # Only allow known topics to avoid template injection
    allowed = {'systemstatus', 'network', 'disk', 'diskio'}
    if topic not in allowed:
        abort(404)

    return render_template(f'partials/{topic}.html', sysname=sysname, topic=topic)