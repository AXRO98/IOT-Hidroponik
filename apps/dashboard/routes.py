from flask import render_template

from apps.dashboard import blueprint

@blueprint.route('/')
def dashboard():   
    return render_template('dashboard/dashboard.html', segment='dashboard')