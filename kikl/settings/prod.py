from .base import *
import dj_database_url

DEBUG = False


DATABASES = {
    'default': dj_database_url.config()
}

# email settings
EMAIL_HOST_USER = get_env_variable('MANDRILL_API_KEY')
DEFAULT_FROM_EMAIL = "kikl.co <no-reply@kikl.co>"
