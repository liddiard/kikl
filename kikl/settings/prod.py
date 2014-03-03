from .base import *
import dj_database_url

DEBUG = True


DATABASES = {
    'default': dj_database_url.config()
}

# email settings
MANDRILL_API_KEY = get_env_variable('MANDRILL_API_KEY')
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
DEFAULT_FROM_EMAIL = "kikl.co <no-reply@kikl.co>"
