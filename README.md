#  Event Manager — Django Web Application

**Author:** Aman Ajwa Fatima
**Framework:** Django 5.2 | **Language:** Python 3.11 | **Database:** SQLite

---

##  Problem Understanding

Managing events manually — tracking who registered, who created what, and keeping everything organized — is inefficient and error-prone. The goal of this project was to build a **full-stack web application** that solves this by giving users a centralized platform to:

- Create and manage events
- Allow other users to discover and register for events
- Give each user a personal space (dashboard) to track their activity
- Handle secure user authentication including account creation and password recovery

The core challenge was not just building individual features, but making them work **together seamlessly** — authentication protecting the right pages, event ownership enforced correctly, and navigation working without errors across all templates.

---

##  Approach

The project was built following Django's **MVT (Model-View-Template)** architecture, breaking the problem into three clear layers:

**1. Data Layer (Models)**
Designed the database schema to represent the two main entities — Users and Events — with a many-to-many relationship to handle event registrations. One user can register for many events, and one event can have many registered users.

**2. Logic Layer (Views)**
Used a combination of Django's **class-based views** (for standard CRUD operations on events) and **function-based views** (for custom logic like event registration/unregistration and the dashboard). This kept standard operations clean while allowing full control where custom behaviour was needed.

**3. Presentation Layer (Templates)**
Built a base template that all pages extend from, keeping the navigation, styling, and structure consistent. Individual templates override content blocks for each specific page.

**Authentication** was handled using Django's built-in `django.contrib.auth` system, extended with custom templates to match the project's design.

---

##  What I Implemented

###  User Authentication System
Built the complete login, logout, and registration flow using Django's built-in auth views combined with custom registration logic. Wrote the register view manually to handle form validation, user creation, and auto-login after successful registration.

###  Event CRUD Operations
Implemented full Create, Read, Update, and Delete functionality for events using Django's class-based generic views (`CreateView`, `UpdateView`, `DeleteView`, `DetailView`, `ListView`). Added ownership checks so users can only edit or delete their own events.

###  Event Registration System
Built a custom many-to-many registration system allowing users to register and unregister for events. Wrote `register_for_event` and `unregister_for_event` function-based views with proper redirect handling after each action.

###  User Dashboard & My Events
Designed a personalized dashboard that gives logged-in users an overview of their activity, and a separate "My Events" page showing only the events they have registered for — filtered by the currently logged-in user.

###  Password Reset Flow
Configured the complete 4-step Django password reset flow:
`Request → Email Sent → Confirm New Password → Success`
Wired up all four views with custom templates and integrated Django's console email backend for development testing.

###  Frontend & Template Design
Designed all templates manually using HTML and CSS, including a shared `base.html` with consistent navigation, card-style layouts, and styling across all pages.

###  URL Routing
Structured and organized all URL patterns across both the main `event_manager/urls.py` and the app-level `events/urls.py`, using named URLs throughout templates with the `{% url %}` tag.

---

##  Challenges Faced

### 1. `NoReverseMatch` — `password_reset` URL Error
**Problem:** The login template used `{% url 'password_reset' %}` but Django could not find the URL, causing a crash on every page — including the admin login.

**Why it was tricky:** The error appeared even on pages completely unrelated to password reset, because `base.html` contained the broken URL tag and every single template extended it. This made the problem look much larger and more confusing than it actually was.

**Solution:** Rather than relying on `include('django.contrib.auth.urls')` which was not resolving correctly in this setup, I explicitly defined all four password reset URL patterns directly inside `events/urls.py` with names that matched exactly what the templates expected.

---

### 2. Django Auth URL Namespace Conflicts
**Problem:** Having both `path('accounts/', include('django.contrib.auth.urls'))` in the main `urls.py` AND custom auth views in `events/urls.py` at the same time created conflicts about which URL names Django should resolve.

**Solution:** Removed the `accounts/` include entirely and defined all auth-related URLs in one place — `events/urls.py` — keeping routing centralized and conflict-free.

---

### 3. Template Inheritance Breaking Silently
**Problem:** Errors inside a parent template (`base.html`) would surface as errors on child pages, making debugging confusing. The traceback pointed to the child template but the real problem was always in the parent.

**Solution:** Learned to read the full traceback carefully — identifying the actual file and line number causing the error, rather than just looking at the top of the stack trace.

---

##  Project Structure

```
Bot/
├── event_manager/
│   ├── settings.py               # Project configuration
│   ├── urls.py                   # Root URL routing
│   └── wsgi.py
├── events/
│   ├── templates/
│   │   └── events/
│   │       ├── base.html
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── dashboard.html
│   │       ├── event_list.html
│   │       ├── event_detail.html
│   │       ├── event_form.html
│   │       ├── my_events.html
│   │       ├── password_reset.html
│   │       ├── password_reset_done.html
│   │       ├── password_reset_confirm.html
│   │       └── password_reset_complete.html
│   ├── models.py                 # Event & User models
│   ├── views.py                  # All views (CBV + FBV)
│   ├── urls.py                   # App-level URL patterns
│   └── forms.py                  # Custom forms
├── db.sqlite3
└── manage.py
```

---

##  How to Run

```bash
# 1. Activate environment
conda activate myenv

# 2. Apply migrations
python manage.py migrate

# 3. Create admin user
python manage.py createsuperuser

# 4. Start server
python manage.py runserver
```

Visit **http://127.0.0.1:8000**

---

##  Key URLs

| Page | URL |
|---|---|
| Home | `/` |
| Register | `/register/` |
| Login | `/login/` |
| Dashboard | `/dashboard/` |
| All Events | `/events/` |
| Create Event | `/events/new/` |
| My Events | `/my-events/` |
| Forgot Password | `/password-reset/` |
| Admin Panel | `/admin/` |

---

> **Note:** `EMAIL_BACKEND` is set to console output for development. Password reset emails will appear in the terminal, not in a real inbox. For production, replace with SMTP settings.
