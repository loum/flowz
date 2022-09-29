"""Customised configuration for the Airflow webserver.

"""
import os
from airflow.www.fab_security.manager import AUTH_OAUTH
from dagster.security import WmSecurityManager


basedir = os.path.abspath(os.path.dirname(__file__))

SECURITY_MANAGER_CLASS = WmSecurityManager

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True

# ----------------------------------------------------
# AUTHENTICATION CONFIG
# ----------------------------------------------------
#
# The supported authentication type.
AUTH_TYPE = AUTH_OAUTH

# Will allow user self registration.
AUTH_USER_REGISTRATION = True

# The default user self registration role.
SUPER_AIRFLOW_ADMIN_GROUP = os.environ.get('SUPER_AIRFLOW_ADMIN_GROUP', '')
AIRFLOW_ADMIN_GROUP = os.environ.get('AIRFLOW_ADMIN_GROUP', '')
AIRFLOW_OP_GROUP_V1 = os.environ.get('AIRFLOW_OP_GROUP_V1', '')
AIRFLOW_OP_GROUP_V2 = os.environ.get('AIRFLOW_OP_GROUP_V2', '')
AIRFLOW_VIEWER_GROUP = os.environ.get('AIRFLOW_VIEWER_GROUP', '')
AUTH_USER_REGISTRATION_ROLE_JMESPATH = f"airflow_aad_group == '{SUPER_AIRFLOW_ADMIN_GROUP}' && 'Admin' || airflow_aad_group == '{AIRFLOW_ADMIN_GROUP}' && 'Admin' || airflow_aad_group == '{AIRFLOW_OP_GROUP_V1}' && 'Op' || airflow_aad_group == '{AIRFLOW_OP_GROUP_V2}' && 'Op' || 'Viewer'"

# If we should replace ALL the user's roles each login, or only on registration.
AUTH_ROLES_SYNC_AT_LOGIN = True

# Force users to re-auth after 30 minutes of inactivity (to keep roles in sync).
PERMANENT_SESSION_LIFETIME = 1800

AZURE_AD_TENANT_ID = os.environ.get('AZURE_AD_TENANT_ID')
AZURE_AD_APPLICATION_ID = os.environ.get('AZURE_AD_APPLICATION_ID')
AZURE_AD_SECRET = os.environ.get('AZURE_AD_SECRET')

OAUTH_PROVIDERS = [
    {
        'name': 'azure',
        'token_key': 'access_token',
        'icon': 'fa-windows',
        'remote_app': {
            'api_base_url': f'https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/oauth2',
            'client_kwargs': {
                'scope': 'User.read name preferred_username email profile upn',
                'resource': f'{AZURE_AD_APPLICATION_ID}',
            },
            'access_token_url':
                f'https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/oauth2/token',
            'authorize_url':
                f'https://login.microsoftonline.com/{AZURE_AD_TENANT_ID}/oauth2/authorize',
            'request_token_url': None,
            'client_id': f'{AZURE_AD_APPLICATION_ID}',
            'client_secret': f'{AZURE_AD_SECRET}',
        },
    },
]
