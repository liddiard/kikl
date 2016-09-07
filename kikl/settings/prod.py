from .base import *
import dj_database_url

DEBUG = False


DATABASES = {
    'default': dj_database_url.config()
}

# email settings
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = get_env_variable('SENDGRID_USERNAME')
EMAIL_HOST_PASSWORD = get_env_variable('SENDGRID_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "kikl.co <no-reply@kikl.co>"