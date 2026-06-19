import os
import csv
import io
import random
import warnings
from datetime import datetime
from flask import Flask, render_template, request, redirect, session, flash, make_response, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from helpers import login_required
from dotenv import load_dotenv
from translations import LANGS
from datetime import datetime
import os
from cs50 import SQL

# ... (tu código de importaciones arriba)

# Configuración inicial
load_dotenv()
app = Flask(__name__)
# ... (resto de configuraciones)

# ... después de las configuraciones de app ...

# Ruta al archivo
if os.environ.get("RENDER"):
    # En Render, usamos /tmp/ para tener permisos de escritura
    db_path = "/tmp/mi_mundo.db"
else:
    # En local, usamos la carpeta del proyecto
    db_path = os.path.join(os.path.dirname(__file__), "mi_mundo.db")

# Crear el archivo si no existe (esto evita el error "does not exist")
if not os.path.exists(db_path):
    open(db_path, 'a').close()

# Inicializar la base de datos
db = SQL(f"sqlite:///{db_path}")

# Crear TODAS las tablas necesarias
db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        username TEXT NOT NULL,
        hash TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS finances (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        user_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        type TEXT NOT NULL,
        status TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS education (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        total_classes INTEGER NOT NULL,
        completed_classes INTEGER NOT NULL
    );
""")
# ... agrega aquí el resto de tus CREATE TABLE ...
#db = SQL("sqlite:///" + os.path.join(basedir, "mi_mundo.db"))

# ── Funciones Helper (Deben ir antes de las rutas) ─────────────────────────────
def is_ajax():
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

def is_partial_request():
    return request.headers.get('X-Partial-Request') == '1'

def render(template, **kwargs):
    # Si es parcial, usamos partial.html, si no, layout.html
    layout = "partial.html" if is_partial_request() else "layout.html"
    return render_template(template, layout=layout, **kwargs)

@app.context_processor
def inject_lang():
    def get_text(key):
        lang = session.get('lang', 'es')
        return LANGS.get(lang, LANGS['es']).get(key, key)
    return dict(_=get_text)

@app.route("/set_lang/<lang>")
def set_lang(lang):

    if lang in LANGS:
        session["lang"] = lang

    return redirect(request.referrer or "/")

# ── Rutas ─────────────────────────────────────────────────────────────────────

@app.route("/")
@login_required
def index():

    finances = db.execute(
        "SELECT amount, category FROM finances WHERE user_id = ?",
        session["user_id"]
    )

    balance = sum(
        f["amount"] if f["category"] == "ingreso"
        else -f["amount"]
        for f in finances
    )

    ingresos = db.execute(
        """
        SELECT COALESCE(SUM(amount),0) AS total
        FROM finances
        WHERE user_id = ?
        AND category = 'ingreso'
        """,
        session["user_id"]
    )[0]["total"]

    gastos = db.execute(
        """
        SELECT COALESCE(SUM(amount),0) AS total
        FROM finances
        WHERE user_id = ?
        AND category = 'gasto'
        """,
        session["user_id"]
    )[0]["total"]

    pending_count = db.execute(
        """
        SELECT COUNT(*) AS count
        FROM activities
        WHERE user_id = ?
        AND status = 'pendiente'
        """,
        session["user_id"]
    )[0]["count"]

    quote = random.choice(
        LANGS.get(
            session.get("lang", "es"),
            LANGS["es"]
        )["quotes"]
    )

    courses = db.execute(
        """
        SELECT *
        FROM education
        WHERE user_id = ?
        """,
        session["user_id"]
    )

    total_courses = len(courses)

    if total_courses > 0:
        avg_progress = sum(
            (c["completed_classes"] * 100) / c["total_classes"]
            for c in courses
        ) / total_courses
    else:
        avg_progress = 0

    user = db.execute(
        "SELECT username FROM users WHERE id = ?",
        session["user_id"]
    )[0]

    hour = datetime.now().hour

    lang = session.get("lang", "es")
    texts = LANGS.get(lang, LANGS["es"])

    if hour < 12:
        greeting = texts["good_morning"]
    elif hour < 18:
        greeting = texts["good_afternoon"]
    else:
        greeting = texts["good_evening"]

    return render(
        "dashboard.html",
        greeting=greeting,
        username=user["username"],
        balance=balance,
        pending=pending_count,
        ingresos=ingresos,
        gastos=gastos,
        ahorro=ingresos - gastos,
        quote=quote,
        total_courses=total_courses,
        avg_progress=round(avg_progress)
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.clear()
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Usuario o contraseña incorrectos", "error")
            return render_template("login.html")
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    return render_template("login.html")

@app.route("/agenda", methods=["GET", "POST"])
@login_required
def agenda():
    if request.method == "POST":
        db.execute("INSERT INTO activities (user_id, title, type, status) VALUES(?, ?, ?, ?)",
                   session["user_id"], request.form.get("title"), request.form.get("type"), 'pendiente')
        if is_ajax():
            act = db.execute("SELECT * FROM activities WHERE user_id = ? ORDER BY id DESC LIMIT 1", session["user_id"])
            return jsonify({"success": True, "activity": dict(act[0])})
        return redirect("/agenda")
    activities = db.execute("SELECT * FROM activities WHERE user_id = ? AND type IN ('type_estudio', 'type_ejercicio', 'type_personal')", session["user_id"])
    return render("agenda.html", activities=activities)

@app.route("/kanban", methods=["GET", "POST"])
@login_required
def kanban():
    if request.method == "POST":
        db.execute("INSERT INTO activities (user_id, title, type, status) VALUES(?, ?, ?, ?)",
                   session["user_id"], request.form.get("title"), 'tarea', 'pendiente')
        if is_ajax():
            task = db.execute("SELECT * FROM activities WHERE user_id = ? AND type = 'tarea' ORDER BY id DESC LIMIT 1", session["user_id"])
            return jsonify({"success": True, "task": dict(task[0])})
        return redirect("/kanban")
    tasks = db.execute("SELECT * FROM activities WHERE user_id = ? AND type = 'tarea'", session["user_id"])
    return render("kanban.html", tasks=tasks)

@app.route("/presupuesto", methods=["GET", "POST"])
@login_required
def presupuesto():
    if request.method == "POST":
        db.execute("INSERT INTO finances (user_id, description, amount, type, category) VALUES(?, ?, ?, ?, ?)",
                   session["user_id"], request.form.get("description"), float(request.form.get("amount")),
                   request.form.get("category"), request.form.get("category"))
        if is_ajax():
            fin = db.execute("SELECT * FROM finances WHERE user_id = ? ORDER BY id DESC LIMIT 1", session["user_id"])
            all_f = db.execute("SELECT amount, category FROM finances WHERE user_id = ?", session["user_id"])
            bal = sum(f['amount'] if f['category'] == 'ingreso' else -f['amount'] for f in all_f)
            return jsonify({"success": True, "finance": dict(fin[0]), "balance": bal})
        return redirect("/presupuesto")
    finances = db.execute("SELECT * FROM finances WHERE user_id = ?", session["user_id"])
    return render("presupuesto.html", finances=finances)

@app.route("/delete/<string:table>/<int:id>")
@login_required
def delete(table, id):
    if table in ['activities', 'finances']:
        db.execute(f"DELETE FROM {table} WHERE id = ? AND user_id = ?", id, session["user_id"])
    if is_ajax():
        return jsonify({"success": True})
    return redirect(request.referrer or '/')

@app.route("/update_task", methods=["POST"])
@login_required
def update_task():

    task_id = request.form.get("id")
    status = request.form.get("status")

    if not task_id:
        return jsonify({"success": False})

    valid_status = [
        "pendiente",
        "progreso",
        "completado"
    ]

    if status not in valid_status:
        return jsonify({"success": False})

    db.execute(
        """
        UPDATE activities
        SET status = ?
        WHERE id = ?
        AND user_id = ?
        """,
        status,
        task_id,
        session["user_id"]
    )

    return jsonify({
        "success": True,
        "status": status
    })


@app.route("/update_activity", methods=["POST"])
@login_required
def update_activity():

    activity_id = request.form.get("id")
    status = request.form.get("status")

    if not activity_id:
        return jsonify({"success": False})

    if status not in ["pendiente", "completado"]:
        return jsonify({"success": False})

    db.execute(
        """
        UPDATE activities
        SET status = ?
        WHERE id = ?
        AND user_id = ?
        """,
        status,
        activity_id,
        session["user_id"]
    )

    return jsonify({"success": True})


@app.route("/export")
@login_required
def export():

    finances = db.execute(
        """
        SELECT description,
               category,
               amount,
               date
        FROM finances
        WHERE user_id = ?
        ORDER BY date DESC
        """,
        session["user_id"]
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Description",
        "Category",
        "Amount",
        "Date"
    ])

    for row in finances:
        writer.writerow([
            row["description"],
            row["category"],
            row["amount"],
            row["date"]
        ])

    response = make_response(output.getvalue())

    filename = f"finances_{datetime.now().strftime('%Y%m%d')}.csv"

    response.headers["Content-Disposition"] = (
        f"attachment; filename={filename}"
    )

    response.headers["Content-Type"] = "text/csv"

    return response


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Complete all fields", "error")
            return redirect("/register")

        existing = db.execute(
            "SELECT id FROM users WHERE username = ?",
            username
        )

        if existing:
            flash("Username already exists", "error")
            return redirect("/register")

        db.execute(
            """
            INSERT INTO users
            (username, hash)
            VALUES (?, ?)
            """,
            username,
            generate_password_hash(password)
        )

        flash("Account created successfully")

        return redirect("/login")

    return render_template("register.html")

@app.route("/education")
@login_required
def education():

    courses = db.execute(
        """
        SELECT *
        FROM education
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        session["user_id"]
    )

    return render(
        "education.html",
        courses=courses
    )
@app.route("/add_course", methods=["POST"])
@login_required
def add_course():

    db.execute(
        """
        INSERT INTO education
        (
            user_id,
            name,
            total_classes,
            completed_classes
        )
        VALUES (?, ?, ?, 0)
        """,
        session["user_id"],
        request.form.get("name"),
        request.form.get("total_classes")
    )

    return redirect("/education")

@app.route("/course/increase/<int:id>", methods=["POST"])
@login_required
def increase_course(id):

    db.execute(
        """
        UPDATE education
        SET completed_classes =
            MIN(completed_classes + 1, total_classes)
        WHERE id = ?
        AND user_id = ?
        """,
        id,
        session["user_id"]
    )

    return redirect("/education")
@app.route("/course/decrease/<int:id>", methods=["POST"])
@login_required
def decrease_course(id):

    db.execute(
        """
        UPDATE education
        SET completed_classes =
            MAX(completed_classes - 1, 0)
        WHERE id = ?
        AND user_id = ?
        """,
        id,
        session["user_id"]
    )

    return redirect("/education")


@app.route("/course/delete/<int:id>", methods=["POST"])
@login_required
def delete_course(id):

    db.execute(
        """
        DELETE FROM education
        WHERE id = ?
        AND user_id = ?
        """,
        id,
        session["user_id"]
    )

    return redirect("/education")

@app.route("/course/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_course(id):

    if request.method == "POST":

        db.execute(
            """
            UPDATE education
            SET name = ?,
                total_classes = ?
            WHERE id = ?
            AND user_id = ?
            """,
            request.form.get("name"),
            request.form.get("total_classes"),
            id,
            session["user_id"]
        )

        return redirect("/education")

    course = db.execute(
        """
        SELECT *
        FROM education
        WHERE id = ?
        AND user_id = ?
        """,
        id,
        session["user_id"]
    )

    if not course:
        return redirect("/education")

    return render(
        "edit_course.html",
        course=course[0]
    )
