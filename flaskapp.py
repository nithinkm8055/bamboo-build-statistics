from flask import Flask, render_template, redirect, url_for, request
from bamboo import branch_status
import datetime


app = Flask(__name__)

@app.route("/")
def get_application_details():
    return render_template("start.html", year=datetime.datetime.now().year)


@app.route("/plan/<plankey>/branch/<branchname>")
def is_sbp_branch(plankey, branchname):
    PLAN_BRANCHES_DICT = branch_status.get_all_branches_in_plan(plankey)
    exists=False
    for child in PLAN_BRANCHES_DICT:
        if branchname == child.get("shortName"):
            exists=True
            break
    if exists:
        return "<p style='text-align: center; line-height: 5;'>{} is an {} branch</p>".format(branchname, plankey)
    else:
        return "<p style='text-align: center; line-height: 5;'>{} branch is not onboarded to {}</p>".format(branchname, plankey)


@app.route("/plan/<plankey>/branch/<branchname>/buildstatus")
def get_build_status_of_single_branch(plankey, branchname):
    latest_build_status, number_of_pass_builds, number_of_fail_builds, counter, no_of_bamboo_builds_on_branch = branch_status.get_build_status_per_branch(plankey, branchname)
    
    branch_key = branch_status.get_branch_key(plankey, branchname)
    last_build_duration, build_start_time = branch_status.get_build_duration_for_branch(branch_key)

    return render_template("branch.html", branch=branchname, branchkey=branch_key, planKey=plankey, recent_builds=counter, latest_build_status=latest_build_status,number_of_pass_builds=number_of_pass_builds, number_of_fail_builds=number_of_fail_builds,  last_build_duration=round(last_build_duration, 2), year=datetime.datetime.now().year)


@app.route("/plan/<plankey>/allbranches")
def get_build_status_of_branches(plankey):
    PLAN_BRANCHES_DICT = branch_status.get_all_branches_in_plan(plankey)

    if PLAN_BRANCHES_DICT == "401":
        return redirect(url_for('handle_error', code="401"))
    elif PLAN_BRANCHES_DICT == "400":
        return redirect(url_for('handle_error', code="400", message="PlanKey: " + plankey))

    number_of_branches = 0
    branches = []
    for branch_entry in PLAN_BRANCHES_DICT:
        branches.append(branch_entry)
        number_of_branches += 1

    total_number_of_bamboo_builds = branch_status.get_total_number_of_builds_from_active_branches(PLAN_BRANCHES_DICT)
    return render_template("index.html", branches=PLAN_BRANCHES_DICT, planKey=plankey, number_of_branches=number_of_branches, year=datetime.datetime.now().year, total_number_of_bamboo_builds=total_number_of_bamboo_builds)


@app.route("/error/<code>")
def handle_error(code):
    return render_template("error.html", code=code, message=request.args.get('message'), year=datetime.datetime.now().year)

if __name__ == "__main__":
    # Run the app in debug mode to auto-reload
    app.run(debug=True)
