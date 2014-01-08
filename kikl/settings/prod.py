from .base import *
import dj_database_url

DEBUG = False

AWS_STORAGE_BUCKET_NAME = 'kikl'
S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME

STATIC_URL = S3_URL

DATABASES = {
    'default': dj_database_url.config()
}

# email settings
EMAIL_HOST = "smtp.mandrillapp.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = get_env_variable('MANDRILL_USERNAME')
EMAIL_HOST_PASSWORD = get_env_variable('MANDRILL_APIKEY')
DEFAULT_FROM_EMAIL = "kikl.co <no-reply@kikl.co>"
