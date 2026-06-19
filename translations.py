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
        'register_link': 'Registrarse ',
        'placeholder_user': 'user ',
        'placeholder_pass': 'contraseña ',

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
        'register_link': 'Register Link ',
        'placeholder_user': 'username ',
        'placeholder_pass': 'password ',




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
