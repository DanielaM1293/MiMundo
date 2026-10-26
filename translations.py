"""
translations.py
---------------
Este módulo centraliza todas las cadenas de texto de la aplicación MiMundo.
"""

LANGS = {
    # Traducciones en Español (Default)
    'es': {
        # Dashboard
        'quick_access': 'Acceso Rápido',
        'pending_tasks': 'Tareas pendientes',
        'finance': 'Finanzas',
        'income': 'Ingresos',
        'expenses': 'Gastos',
        'savings': 'Ahorro',
        'dashboard': 'Tablero',
        'agenda': 'Agenda',
        'kanban': 'Kanban',
        'budget': 'Presupuesto',
        'logout': 'Cerrar sesión',
        'welcome': 'Bienvenido',
        'welcome_back': 'Bienvenido de nuevo',
        'toggle_theme': 'Cambiar tema',
        'quick_access': 'Acceso Rápido',
        'finance_summary': 'Resumen de ingresos, gastos y ahorro',
        'no_finance_data': 'Aún no hay movimientos financieros.',
        "good_morning": "Buenos días",
        "good_afternoon": "Buenas tardes",
        "good_evening": "Buenas noches",
        "dashboard_subtitle": "Aquí tienes un resumen de tus finanzas de hoy.",

        # Agenda
        'agenda_title': 'Mi Agenda',
        'placeholder_todo': '¿Qué vas a hacer?',
        'type_estudio': 'Estudio',
        'type_ejercicio': 'Ejercicio',
        'type_personal': 'Personal',
        'btn_add': 'Agregar',
        'no_activities': 'No hay actividades registradas aún.',

        # Kanban
        'kanban_title': 'Mi Tablero Kanban',
        'placeholder_task': 'Nueva tarea...',
        'col_pending': 'Pendientes',
        'col_progress': 'En Progreso',
        'col_completed': 'Completadas',
        'view_kanban': 'Ver Kanban',

        # Presupuesto
        'budget_title': 'Mi Presupuesto',
        'placeholder_concept': 'Concepto',
        'placeholder_amount': 'Monto',
        'select_category': 'Categoría',
        'cat_ingreso': 'Ingreso',
        'cat_gasto': 'Gasto',
        'btn_register': 'Registrar',
        'current_balance': 'Saldo Actual',
        'new_expense': 'Nuevo Gasto',
        'btn_back_budget': '← Volver al Presupuesto',

        # Formacion
        'education': 'Formación',
        'add_course': 'Agregar curso',
        'course_name': 'Nombre del curso',
        'total_classes': 'Total de módulos',
        'active_courses': 'Cursos activos',
        'average_progress': 'Progreso promedio',
        'no_courses': 'No hay cursos registrados todavía.',
        'edit_course': 'Editar curso',
        'save': 'Guardar',
        'delete': 'Eliminar',
        'progress': 'Progreso',
        'completed_modules': 'Módulos completados',
        'courses_completed': 'Cursos completados',
        'active_courses': 'Cursos activos',
        'average_progress': 'Progreso promedio',
        "delete_course_title": "¿Eliminar curso?",
        "delete_course_message": "¿Seguro que deseas eliminar",
        "delete_course_warning": "Esta acción no se puede deshacer.",
        "cancel": "Cancelar",
        "confirm_delete": "Sí, eliminar",

        'btn_login': 'Iniciar sesión',
        'register_title': 'Registrarse',
        'no_account' : '¿Sin cuenta?',
        'register_link': 'Registrarse',
        'have_account': '¿Ya tienes cuenta?',
        'login_link': 'Inicia sesión',
        'placeholder_user': 'Usuario',
        'placeholder_pass': 'Contraseña',

        # Mensajes de Formación (cursos)
        'completed_badge': 'Completado',
        'invalid_course': 'Escribe un nombre y un número de clases mayor que 0.',
        'error_generic': 'Algo salió mal. Inténtalo de nuevo.',

        # Mensajes de sesión y registro
        'login_error': 'Usuario o contraseña incorrectos.',
        'register_empty': 'Completa todos los campos.',
        'register_long': 'El usuario puede tener máximo 20 caracteres.',
        'register_short': 'La contraseña debe tener al menos 8 caracteres.',
        'register_exists': 'Ese nombre de usuario ya existe.',
        'register_ok': 'Cuenta creada con éxito. Ya puedes iniciar sesión.',

        # Validaciones y errores
        'invalid_activity': 'Escribe un título (máximo 100 caracteres) y elige un tipo válido.',
        'invalid_finance': 'Revisa los datos: concepto (máximo 50 caracteres), monto mayor que 0 y categoría.',
        'error_bad_request': 'La solicitud no es válida o la sesión expiró. Recarga la página e inténtalo de nuevo.',
        'error_not_found': 'No encontramos esa página.',
        'error_not_allowed': 'Esta acción no está permitida.',
        'error_server': 'Ocurrió un error en el servidor. Inténtalo de nuevo en un momento.',
        'back_home': '← Volver al inicio',

        # Agenda
        'mark_done': 'Marcar como completada',
        'mark_pending': 'Marcar como pendiente',

        # Frases
        'daily_quote': 'Frase del día',
        'quotes': [
            "La disciplina es el puente entre las metas y los logros. — Jim Rohn",
            "El éxito es la suma de pequeños esfuerzos repetidos día tras día. — Robert Collier",
            "La mejor forma de predecir el futuro es creándolo. — Peter Drucker",
            "Tu tiempo es limitado, no lo desperdicies viviendo la vida de otro. — Steve Jobs"
        ]
    },

    # Traducciones en Inglés
    'en': {
        # Dashboard
        'pending_tasks': 'Pending Tasks',
        'finance': 'Finance',
        'income': 'Income',
        'expenses': 'Expenses',
        'savings': 'Savings',
        'dashboard': 'Dashboard',
        'agenda': 'Schedule',
        'kanban': 'Kanban',
        'budget': 'Budget',
        'logout': 'Log Out',
        'welcome': 'Welcome',
        'welcome_back': 'Welcome back',
        'toggle_theme': 'Toggle Theme',
        'quick_access': 'Quick Access',
        'finance_summary': 'Income, expenses and savings summary',
        'no_finance_data': 'No financial data yet.',
        "good_morning": "Good morning",
        "good_afternoon": "Good afternoon",
        "good_evening": "Good evening",
        "dashboard_subtitle": "Here's an overview of your finances today.",

        # Schedule
        'agenda_title': 'My Schedule',
        'placeholder_todo': 'What are you going to do?',
        'type_estudio': 'Study',
        'type_ejercicio': 'Exercise',
        'type_personal': 'Personal',
        'btn_add': 'Add',
        'no_activities': 'No activities recorded yet.',

        # Kanban
        'kanban_title': 'My Kanban Board',
        'placeholder_task': 'New task...',
        'col_pending': 'Pending',
        'col_progress': 'In Progress',
        'col_completed': 'Completed',
        'view_kanban': 'View Kanban',

        # Budget
        'budget_title': 'My Budget',
        'placeholder_concept': 'Concept',
        'placeholder_amount': 'Amount',
        'select_category': 'Category',
        'cat_ingreso': 'Income',
        'cat_gasto': 'Expense',
        'btn_register': 'Register',
        'current_balance': 'Current Balance',
        'new_expense': 'New Expense',
        'btn_back_budget': '← Back to Budget',


        # Education
        'education': 'Education',
        'add_course': 'Add course',
        'course_name': 'Course name',
        'total_classes': 'Total modules',
        'active_courses': 'Active courses',
        'average_progress': 'Average progress',
        'no_courses': 'No courses registered yet.',
        'edit_course': 'Edit course',
        'save': 'Save',
        'delete': 'Delete',
        'progress': 'Progress',
        'completed_modules': 'Completed modules',
        'courses_completed': 'Completed courses',
        'active_courses': 'Active courses',
        'average_progress': 'Average progress',
        "delete_course_title": "Delete course?",
        "delete_course_message": "Are you sure you want to delete",
        "delete_course_warning": "This action cannot be undone.",
        "cancel": "Cancel",
        "confirm_delete": "Yes, delete",

        'btn_login': 'Login',
        'register_title': 'Register',
        'no_account' : 'No account?',
        'register_link': 'Register',
        'have_account': 'Already have an account?',
        'login_link': 'Log in',
        'placeholder_user': 'Username',
        'placeholder_pass': 'Password',

        # Education (courses) messages
        'completed_badge': 'Completed',
        'invalid_course': 'Enter a name and a number of classes greater than 0.',
        'error_generic': 'Something went wrong. Please try again.',

        # Session and registration messages
        'login_error': 'Incorrect username or password.',
        'register_empty': 'Please fill in all fields.',
        'register_long': 'The username can have at most 20 characters.',
        'register_short': 'The password must be at least 8 characters long.',
        'register_exists': 'That username already exists.',
        'register_ok': 'Account created successfully. You can now log in.',

        # Validation and errors
        'invalid_activity': 'Enter a title (up to 100 characters) and choose a valid type.',
        'invalid_finance': 'Check the data: concept (up to 50 characters), amount greater than 0 and category.',
        'error_bad_request': 'The request is not valid or the session expired. Reload the page and try again.',
        'error_not_found': "We couldn't find that page.",
        'error_not_allowed': 'This action is not allowed.',
        'error_server': 'A server error occurred. Please try again in a moment.',
        'back_home': '← Back to home',

        # Schedule
        'mark_done': 'Mark as completed',
        'mark_pending': 'Mark as pending',




        # Motivation
        'daily_quote': 'Daily Quote',
        'quotes': [
            "Discipline is the bridge between goals and accomplishment. — Jim Rohn",
            "Success is the sum of small efforts, repeated day in and day out. — Robert Collier",
            "The best way to predict the future is to create it. — Peter Drucker",
            "Your time is limited, so don't waste it living someone else's life. — Steve Jobs"
        ]
    }
}
