from pathlib import Path
import environ


BASE_DIR = Path(__file__).resolve().parent.parent

# --- env ---
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

# Use ONLY env-driven values (remove duplicates below)
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")

TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", default="")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID", default="")

BAKONG_BASE_URL = env("BAKONG_BASE_URL", default="https://api-bakong.nbc.gov.kh")
BAKONG_API_TOKEN = env("BAKONG_API_TOKEN", default="")


# --- apps ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'store.apps.StoreConfig',
    "widget_tweaks",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "anitoys.urls"

# --- templates ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Point to your app templates folder
        "DIRS": [BASE_DIR / "store" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # cart totals available in navbar, etc.
                "store.context_processors.cart_summary",
                "store.context_processors.global_shop",

            ],
        },
    },
]

WSGI_APPLICATION = "anitoys.wsgi.application"

# --- database (PostgreSQL via .env) ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

# --- auth ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- static & media ---
TEMPLATES[0]["DIRS"] = [BASE_DIR / "store" / "templates"]
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "store" / "static"]  # your Bootstrap theme files

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"  # uploaded product images

# --- redirects after login/logout ---
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
