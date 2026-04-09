from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "secret"

UPLOAD_FOLDER = "database"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= LOGIN =================
@app.route('/')
def login():
    return render_template("login.html")

# ================= EMPLOYEE LOGIN =================
@app.route('/employee_login', methods=['POST'])
def employee_login():
    emp_id = request.form['emp_id']

    df = pd.read_csv("data/employee_details.csv")

    if emp_id in df['employee_id'].astype(str).values:
        session['emp_id'] = emp_id
        return redirect(url_for('dashboard'))   #  IMPORTANT
    else:
        return render_template("login.html", emp_error="Invalid Employee ID")
@app.route('/dashboard')
def dashboard():
    emp_id = session.get('emp_id')

    if not emp_id:
        return redirect(url_for('login'))  # safety

    df = pd.read_csv("data/employee_details.csv")
    emp = df[df['employee_id'].astype(str) == emp_id].iloc[0]

    return render_template("dashboard.html", emp=emp)
@app.route('/performance/<year>')
def performance(year):
    emp_id = session.get('emp_id')

    df = pd.read_csv(f"data/employee_performance_{year}.csv")
    emp = df[df['employee_id'].astype(str) == emp_id].iloc[0]

    return render_template("performance.html", emp=emp, year=year)   
# ================= ADMIN LOGIN =================
@app.route('/admin_login', methods=['POST'])
def admin_login():
    if request.form['password'] == "1889":
        return redirect('/admin_dashboard')
    return render_template("login.html", admin_error="Invalid Password")

# ================= ADMIN DASHBOARD =================
@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template("admin_dashboard.html")

# ================= CREATE TEAM =================
@app.route('/create_team', methods=['POST'])
def create_team():
    team = request.form.get('team')

    if not team:
        return render_template("upload.html", error="Enter Team Name")

    path = os.path.join(UPLOAD_FOLDER, team)

    if not os.path.exists(path):
        os.makedirs(path)
        return render_template("upload.html", success="Team Created Successfully")

    return render_template("upload.html", success="Team already exists")
# ================= UPLOAD =================
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        team = request.form.get('team')
        title = request.form.get('title')
        file = request.files.get('file')
        link = request.form.get('link')

        if not team:
            return render_template("upload.html", error="Enter Team Name")

        if not title:
            return render_template("upload.html", error="Enter Title")

        # CREATE TEAM AUTOMATICALLY
        path = os.path.join(UPLOAD_FOLDER, team)
        os.makedirs(path, exist_ok=True)

        # SAVE FILE
        if file and file.filename != "":
            filename = f"{title}_{file.filename}"
            file.save(os.path.join(path, filename))

        # SAVE LINK
        elif link:
            filename = f"{title}.link"
            with open(os.path.join(path, filename), "w") as f:
                f.write(link)

        else:
            return render_template("upload.html", error="Select file or enter link")

        return render_template("upload.html", success="Saved Successfully")

    return render_template("upload.html")

# ================= DECISION =================
@app.route('/decision', methods=['GET', 'POST'])
def decision():
    if request.method == 'POST':
        team = request.form.get('team')
        title = request.form.get('title')
        content = request.form.get('content')

        if not team:
            return render_template("decision.html", error="Enter Team Name")

        if not title:
            return render_template("decision.html", error="Enter Title")

        #  AUTO CREATE TEAM
        path = os.path.join(UPLOAD_FOLDER, team)
        os.makedirs(path, exist_ok=True)

        # SAVE TEXT
        with open(os.path.join(path, f"{title}.txt"), "w") as f:
            f.write(content)

        return render_template("decision.html", success="Saved Successfully")

    return render_template("decision.html")

# ================= RESULTS =================
@app.route('/results_login', methods=['GET', 'POST'])
def results_login():
    if request.method == 'POST':
        password = request.form.get('password')

        if password == "2421":
            return redirect('/results')
        else:
            return render_template("results_login.html", error="Wrong Password")

    return render_template("results_login.html")
@app.route('/results')
def results():
    query = request.args.get('search', '').lower()

    teams = [f for f in os.listdir("database") 
             if os.path.isdir(os.path.join("database", f))]

    if query:
        teams = [team for team in teams if query in team.lower()]

    return render_template("results.html", teams=teams)
@app.route('/results')
def results():
    teams = [f for f in os.listdir("database") if os.path.isdir(os.path.join("database", f))]
    return render_template("results.html", teams=teams)
# ================= TEAM FILES =================
@app.route('/team/<team>')
def team_files(team):
    folder = os.path.join("database", team)

    files = os.listdir(folder)

    #  Sort by latest (new first)
    files = sorted(
        files,
        key=lambda x: os.path.getmtime(os.path.join(folder, x)),
        reverse=True
    )

    return render_template("team_files.html", files=files, team=team)
# ================= OPEN =================
@app.route('/open/<team>/<path:file>')
def open_file(team, file):
    path = os.path.join(UPLOAD_FOLDER, team)

    if file.endswith(".link"):
        with open(os.path.join(path, file)) as f:
            return redirect(f.read())

    return send_from_directory(path, file)

# ================= DELETE =================
@app.route('/delete/<team>/<file>')
def delete_file(team, file):
    os.remove(os.path.join(UPLOAD_FOLDER, team, file))
    return redirect(f"/team/{team}")

# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)