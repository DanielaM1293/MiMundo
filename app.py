import os
import csv
import io
import hmac
import random
import secrets
from datetime import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask import (
    Flask, abort, flash, jsonify, make_response, redirect,
    render_template, request, session
)
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL

from helpers import login_required
from translations import LANGS

# ── Configuración inicial ─────────────────────────────────────────────────────
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# En Render (https) la cookie de sesión solo viaja por conexiones seguras
app.config["SESSION_COOKIE_SECURE"] = bool(os.environ.get("RENDER"))
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024  # 1 MB máximo por petición

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

# Tipos válidos de actividad en la Agenda
AGENDA_TYPES = ("personal", "estudio", "ejercicio")


# ── Funciones auxiliares (deben ir antes de las rutas) ────────────────────────
def is_ajax():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def is_partial_request():
    return request.headers.get("X-Partial-Request") == "1"


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


def reset_session():
    """Borra la sesión pero conserva el idioma elegido."""
    lang = session.get("lang")
    session.clear()
    if lang:
        session["lang"] = lang


def safe_referrer(default="/"):
    """Vuelve a la página anterior solo si es de este mismo sitio."""
    referrer = request.referrer
    if referrer:
        parsed = urlparse(referrer)
        if parsed.netloc == request.host:
            return parsed.path or default
    return default


def csv_safe(value):
    """Evita que Excel interprete un texto como fórmula (=, +, -, @)."""
    text = "" if value is None else str(value)
    if text[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + text
    return text


# ── Protección CSRF ───────────────────────────────────────────────────────────
def get_csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_hex(16)
        session["csrf_token"] = token
    return token


@app.before_request
def check_csrf():
    """Todo POST debe traer el token secreto de la sesión.

    /login y /register quedan fuera: todavía no hay una sesión que proteger y así
    nadie se queda sin poder entrar (por ejemplo, con una página vieja en caché).
    """
    if request.endpoint in ("login", "register"):
        return

    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        expected = session.get("csrf_token", "")
        sent = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token") or ""
        if not expected or not hmac.compare_digest(expected.encode(), sent.encode()):
            abort(400)


@app.context_processor
def inject_helpers():
    return dict(_=t, csrf_token=get_csrf_token)


# ── Manejo de errores ─────────────────────────────────────────────────────────
def render(template, **kwargs):
    # Si es parcial, usamos partial.html, si no, layout.html
    layout = "partial.html" if is_partial_request() else "layout.html"
    return render_template(template, layout=layout, **kwargs)


def error_response(code, key):
    message = t(key)
    if is_ajax():
        return jsonify({"success": False, "error": message}), code
    return render("error.html", message=message), code


@app.errorhandler(400)
def bad_request(e):
    return error_response(400, "error_bad_request")


@app.errorhandler(404)
def not_found(e):
    return error_response(404, "error_not_found")


@app.errorhandler(405)
def method_not_allowed(e):
    return error_response(405, "error_not_allowed")


@app.errorhandler(413)
def too_large(e):
    return error_response(413, "error_bad_request")


@app.errorhandler(500)
def server_error(e):
    return error_response(500, "error_server")


# ── Consultas reutilizables ───────────────────────────────────────────────────
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


def get_activity(activity_id):
    """Devuelve la actividad de la Agenda del usuario actual, o None."""
    rows = db.execute(
        "SELECT * FROM activities WHERE id = ? AND user_id = ? AND type != 'tarea'",
        activity_id, session["user_id"]
    )
    return rows[0] if rows else None


def activity_json(activity):
    """Respuesta AJAX con la tarjeta de la actividad ya dibujada."""
    return jsonify({
        "success": True,
        "id": activity["id"],
        "html": render_template("_activity_card.html", activity=activity)
    })


# ── Rutas ─────────────────────────────────────────────────────────────────────
@app.route("/set_lang/<lang>")
def set_lang(lang):
    if lang in LANGS:
        session["lang"] = lang
    return redirect(safe_referrer())


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
        reset_session()
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
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash(t("login_error"), "error")
            return render_template("login.html")

        reset_session()
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    reset_session()
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if not username or not password:
            flash(t("register_empty"), "error")
            return redirect("/register")

        if len(username) > 20:
            flash(t("register_long"), "error")
            return redirect("/register")

        if len(password) < 8:
            flash(t("register_short"), "error")
            return redirect("/register")

        existing = db.execute(
            "SELECT id FROM users WHERE username = ?",
            username
        )

        if existing:
            flash(t("register_exists"), "error")
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

        flash(t("register_ok"))

        return redirect("/login")

    return render_template("register.html")


# ── Agenda ────────────────────────────────────────────────────────────────────
@app.route("/agenda", methods=["GET", "POST"])
@login_required
def agenda():

    if request.method == "POST":

        title = (request.form.get("title") or "").strip()
        activity_type = request.form.get("type")

        if not title or len(title) > 100 or activity_type not in AGENDA_TYPES:
            if is_ajax():
                return jsonify({"success": False, "error": t("invalid_activity")}), 400
            flash(t("invalid_activity"), "error")
            return redirect("/agenda")

        activity_id = db.execute(
            "INSERT INTO activities (user_id, title, type, status) VALUES(?, ?, ?, ?)",
            session["user_id"], title, activity_type, "pendiente"
        )

        if is_ajax():
            return activity_json(get_activity(activity_id))

        return redirect("/agenda")

    # Todo lo que no sea una tarea del Kanban (incluye tipos guardados con el formato viejo)
    activities = db.execute(
        "SELECT * FROM activities WHERE user_id = ? AND type != 'tarea' ORDER BY id DESC",
        session["user_id"]
    )

    return render("agenda.html", activities=activities)


@app.route("/update_activity", methods=["POST"])
@login_required
def update_activity():

    activity_id = request.form.get("id")
    status = request.form.get("status")

    if not activity_id:
        return jsonify({"success": False}), 400

    if status not in ["pendiente", "completado"]:
        return jsonify({"success": False}), 400

    db.execute(
        """
        UPDATE activities
        SET status = ?
        WHERE id = ?
        AND user_id = ?
        AND type != 'tarea'
        """,
        status,
        activity_id,
        session["user_id"]
    )

    if is_ajax():
        activity = get_activity(activity_id)
        if not activity:
            return jsonify({"success": False, "error": t("error_generic")}), 404
        return activity_json(activity)

    return jsonify({"success": True})


# ── Kanban ────────────────────────────────────────────────────────────────────
@app.route("/kanban", methods=["GET", "POST"])
@login_required
def kanban():

    if request.method == "POST":

        title = (request.form.get("title") or "").strip()

        if not title or len(title) > 100:
            if is_ajax():
                return jsonify({"success": False, "error": t("invalid_activity")}), 400
            flash(t("invalid_activity"), "error")
            return redirect("/kanban")

        task_id = db.execute(
            "INSERT INTO activities (user_id, title, type, status) VALUES(?, ?, ?, ?)",
            session["user_id"], title, "tarea", "pendiente"
        )

        if is_ajax():
            task = db.execute(
                "SELECT * FROM activities WHERE id = ? AND user_id = ?",
                task_id, session["user_id"]
            )
            return jsonify({"success": True, "task": dict(task[0])})

        return redirect("/kanban")

    tasks = db.execute(
        "SELECT * FROM activities WHERE user_id = ? AND type = 'tarea'",
        session["user_id"]
    )

    return render("kanban.html", tasks=tasks)


@app.route("/update_task", methods=["POST"])
@login_required
def update_task():

    task_id = request.form.get("id")
    status = request.form.get("status")

    if not task_id:
        return jsonify({"success": False}), 400

    valid_status = [
        "pendiente",
        "progreso",
        "completado"
    ]

    if status not in valid_status:
        return jsonify({"success": False}), 400

    db.execute(
        """
        UPDATE activities
        SET status = ?
        WHERE id = ?
        AND user_id = ?
        AND type = 'tarea'
        """,
        status,
        task_id,
        session["user_id"]
    )

    return jsonify({
        "success": True,
        "status": status
    })


# ── Presupuesto ───────────────────────────────────────────────────────────────
@app.route("/presupuesto", methods=["GET", "POST"])
@login_required
def presupuesto():

    if request.method == "POST":

        description = (request.form.get("description") or "").strip()
        amount = parse_positive_float(request.form.get("amount"))
        category = request.form.get("category")

        # Validación: descripción obligatoria, monto > 0 y categoría válida
        if (not description or len(description) > 50
                or amount is None or category not in ("ingreso", "gasto")):
            if is_ajax():
                return jsonify({"success": False, "error": t("invalid_finance")}), 400
            flash(t("invalid_finance"), "error")
            return redirect("/presupuesto")

        finance_id = db.execute(
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
                "SELECT * FROM finances WHERE id = ? AND user_id = ?",
                finance_id, session["user_id"]
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
            csv_safe(row["description"]),
            csv_safe(row["category"]),
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


# ── Borrar actividades y movimientos (solo por POST) ──────────────────────────
@app.route("/delete/<string:table>/<int:id>", methods=["POST"])
@login_required
def delete(table, id):

    if table == "activities":
        db.execute(
            "DELETE FROM activities WHERE id = ? AND user_id = ?",
            id, session["user_id"]
        )
    elif table == "finances":
        db.execute(
            "DELETE FROM finances WHERE id = ? AND user_id = ?",
            id, session["user_id"]
        )
    else:
        abort(404)

    if is_ajax():
        return jsonify({"success": True})

    return redirect(safe_referrer())


# ── Educación ─────────────────────────────────────────────────────────────────
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

    if not name or len(name) > 100 or total_classes is None:
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

        if not name or len(name) > 100 or total_classes is None:
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

    course = get_course(id)

    if not course:
        return redirect("/education")

    return render(
        "edit_course.html",
        course=course
    )


if __name__ == "__main__":
    # El modo debug solo se activa si lo pides: FLASK_DEBUG=1
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
