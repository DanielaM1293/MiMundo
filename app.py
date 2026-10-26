import os
import csv
import io
import random
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, flash, make_response, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL

from helpers import login_required
from translations import LANGS

# Configuración inicial
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Base de datos: la ruta viene de una variable de entorno (o local por defecto)
db_path = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "mi_mundo.db"))

if not os.path.exists(db_path):
    open(db_path, "a").close()

db = SQL(f"sqlite:///{db_path}")

db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL)")
db.execute("CREATE TABLE IF NOT EXISTS finances (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, description TEXT NOT NULL, amount REAL NOT NULL, type TEXT, category TEXT NOT NULL, date DATETIME DEFAULT CURRENT_TIMESTAMP)")
db.execute("CREATE TABLE IF NOT EXISTS activities (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, title TEXT NOT NULL, type TEXT NOT NULL, status TEXT NOT NULL)")
db.execute("CREATE TABLE IF NOT EXISTS education (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, name TEXT NOT NULL, total_classes INTEGER NOT NULL, completed_classes INTEGER NOT NULL)")
# Repara cursos con datos inválidos guardados antes de agregar las validaciones
db.execute("UPDATE education SET total_classes = 1 WHERE typeof(total_classes) != 'integer' OR total_classes < 1")
db.execute("UPDATE education SET completed_classes = 0 WHERE typeof(completed_classes) != 'integer' OR completed_classes < 0")
db.execute("UPDATE education SET completed_classes = total_classes WHERE completed_classes > total_classes")

# ── Funciones Helper (Deben ir antes de las rutas) ─────────────────────────────
def is_ajax():
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

def is_partial_request():
    return request.headers.get('X-Partial-Request') == '1'

def parse_positive_int(value):
    """Devuelve un entero mayor que 0, o None si el valor no es válido."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None

def parse_positive_float(value):
    """Devuelve un número mayor que 0, o None si el valor no es válido."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    # number != number detecta NaN; el límite evita valores absurdos
    if number != number or number <= 0 or number > 1_000_000_000_000:
        return None
    return number

def t(key):
    """Texto traducido según el idioma de la sesión (español por defecto)."""
    lang = session.get("lang", "es")
    return LANGS.get(lang, LANGS["es"]).get(key, key)

def get_course(course_id):
    """Devuelve el curso del usuario actual, o None si no existe."""
    rows = db.execute(
        "SELECT * FROM education WHERE id = ? AND user_id = ?",
        course_id, session["user_id"]
    )
    return rows[0] if rows else None

def course_json(course):
    """Respuesta AJAX con la tarjeta del curso ya dibujada."""
    return jsonify({
        "success": True,
        "id": course["id"],
        "html": render_template("_course_card.html", course=course)
    })

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
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM finances
        WHERE user_id = ?
        AND category = 'ingreso'
        """,
        session["user_id"]
    )[0]["total"]

    gastos = db.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
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

    # Ignora cursos con datos inválidos (por ejemplo 0 clases) para no romper el dashboard
    valid_courses = []
    for c in courses:
        try:
            if int(c["total_classes"]) > 0:
                valid_courses.append(c)
        except (TypeError, ValueError):
            continue

    if valid_courses:
        avg_progress = sum(
            (int(c["completed_classes"]) * 100) / int(c["total_classes"])
            for c in valid_courses
        ) / len(valid_courses)
    else:
        avg_progress = 0

    # Verificar que el usuario exista
    user = db.execute(
        "SELECT username FROM users WHERE id = ?",
        session["user_id"]
    )

    if not user:
        session.clear()
        return redirect("/login")

    user = user[0]

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

        description = (request.form.get("description") or "").strip()
        amount = parse_positive_float(request.form.get("amount"))
        category = request.form.get("category")

        # Validación: descripción obligatoria, monto > 0 y categoría válida
        if not description or amount is None or category not in ("ingreso", "gasto"):
            if is_ajax():
                return jsonify({
                    "success": False,
                    "error": "Datos inválidos: revisa la descripción, el monto y la categoría."
                }), 400
            flash("Datos inválidos: revisa la descripción, el monto y la categoría.", "error")
            return redirect("/presupuesto")

        try:

            db.execute(
                """
                INSERT INTO finances
                (user_id, description, amount, type, category)
                VALUES (?, ?, ?, ?, ?)
                """,
                session["user_id"],
                description,
                amount,
                category,   # type
                category    # category
            )

            if is_ajax():

                fin = db.execute(
                    """
                    SELECT *
                    FROM finances
                    WHERE user_id = ?
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    session["user_id"]
                )

                all_f = db.execute(
                    """
                    SELECT amount, category
                    FROM finances
                    WHERE user_id = ?
                    """,
                    session["user_id"]
                )

                balance = sum(
                    f["amount"] if f["category"] == "ingreso"
                    else -f["amount"]
                    for f in all_f
                )

                return jsonify({
                    "success": True,
                    "finance": dict(fin[0]),
                    "balance": balance
                })

            return redirect("/presupuesto")

        except Exception:
            import traceback
            traceback.print_exc()
            return jsonify({"success": False}), 500

    finances = db.execute(
        """
        SELECT *
        FROM finances
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        session["user_id"]
    )

    return render(
        "presupuesto.html",
        finances=finances
    )

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

    name = (request.form.get("name") or "").strip()
    total_classes = parse_positive_int(request.form.get("total_classes"))

    if not name or total_classes is None:
        if is_ajax():
            return jsonify({"success": False, "error": t("invalid_course")}), 400
        flash(t("invalid_course"), "error")
        return redirect("/education")

    course_id = db.execute(
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
        name,
        total_classes
    )

    if is_ajax():
        return course_json(get_course(course_id))

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

    if is_ajax():
        course = get_course(id)
        if not course:
            return jsonify({"success": False, "error": t("error_generic")}), 404
        return course_json(course)

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

    if is_ajax():
        course = get_course(id)
        if not course:
            return jsonify({"success": False, "error": t("error_generic")}), 404
        return course_json(course)

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

    if is_ajax():
        return jsonify({"success": True})

    return redirect("/education")

@app.route("/course/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_course(id):

    if request.method == "POST":

        name = (request.form.get("name") or "").strip()
        total_classes = parse_positive_int(request.form.get("total_classes"))

        if not name or total_classes is None:
            flash(t("invalid_course"), "error")
            return redirect(f"/course/edit/{id}")

        db.execute(
            """
            UPDATE education
            SET name = ?,
                total_classes = ?,
                completed_classes = MIN(completed_classes, ?)
            WHERE id = ?
            AND user_id = ?
            """,
            name,
            total_classes,
            total_classes,
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

if __name__ == "__main__":
    app.run(debug=True)
