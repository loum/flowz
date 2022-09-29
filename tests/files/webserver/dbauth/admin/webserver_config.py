"""Customised configuration for the Airflow webserver.

"""
import os
from airflow.www.fab_security.manager import AUTH_DB


basedir = os.path.abspath(os.path.dirname(__file__))

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True

# ----------------------------------------------------
# AUTHENTICATION CONFIG
# ----------------------------------------------------
#
# The supported authentication type.
AUTH_TYPE = AUTH_DB

# Uncomment to setup Public role name, no authentication needed.
AUTH_ROLE_PUBLIC = 'Admin'

# Will allow user self registration.
AUTH_USER_REGISTRATION = True

