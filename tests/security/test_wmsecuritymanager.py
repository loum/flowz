""":class:`dagster.security.WmSecurityManager` unit test cases.
"""
import unittest.mock
from airflow.www import app as application

from dagster.security import WmSecurityManager


# This one has expired.
ACCESS_TOKEN = {
    'token_type': 'Bearer',
    'scope': 'Directory.Read.All email User.Read',
    'expires_in': '3599',
    'ext_expires_in': '3599',
    'expires_on': '1622257051',
    'not_before': '1622253151',
    'resource': '00000002-0000-0000-c000-000000000000',
    'access_token': 'eyJ...',
    'refresh_token': '0.A...',
    'id_token':
        'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ2MnNrQWh3ZkZlTEVaYlBaTHpoREFUUHBLcklUeXo4U0wxQkFTZkZRMHBVI'
        'iwidmVyIjoiMS4wIiwiYW1yIjoiW1wicHdkXCIsIFwibWZhXCJdIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5'
        'uZXQvODI1NTFhMTItYmJjOC00ZmVkLThiN2YtWFhYWFhYWFhYWFhYLyIsIm9ucHJlbV9zaWQiOiJTLTEtNS0yMS05M'
        'TIyNzQ0LTE1NTgwNzM5MDAtMTU1MDg1MDA2Ny0xMDIwODgwIiwib2lkIjoiZjE2ODhjYzgtMmViNC00NmEyLThhNzI'
        'tWFhYWFhYWFhYWFhYIiwiZ2l2ZW5fbmFtZSI6IkpvaG4iLCJ0aWQiOiI4MjU1MWExMi1iYmM4LTRmZWQtOGI3Zi1YW'
        'FhYWFhYWFhYWFgiLCJhdWQiOiJlMTRiMjlhMy02NDliLTRkMDMtYjQ1OC1YWFhYWFhYWFhYWFgiLCJ1bmlxdWVfbmF'
        'tZSI6IkpvaG4uRG9lQGNvbGVzLmNvbS5hdSIsInVwbiI6IkpvaG4uRG9lQGNvbGVzLmNvbS5hdSIsIm5iZiI6IjE2M'
        'jIyNTMxNTEiLCJyaCI6IjAuQVFZQUVocFZnc2k3N1UtTGZ5dDFnb1MxNnFNcFMtR2JaQU5OdEZqd3k0eE8xUXdHQUp'
        'BLiIsIm5hbWUiOiJKb2huIERvZSIsImV4cCI6IjE2MjIyNTcwNTEiLCJpcGFkZHIiOiIxMjcuMC4wLjEiLCJpYXQiO'
        'iIxNjIyMjUzMTUxIiwiZmFtaWx5X25hbWUiOiJEb2UifQ.yCmP89uOpFDd9SxV4dHCBhugbmj9PX_ETJZkrSi6z0k',
    'expires_at': 1622257050
}


def test_wmsecuritymanager_init():
    """Initialise a dagster.security.WmSecurityManager object.
    """
    # Given an appbuilder application
    app = application.create_app(testing=True)
    appbuilder = app.appbuilder # pylint: disable=no-member

    # when I initialise a dagster.security.WmSecurityManager object
    sec_man = WmSecurityManager(appbuilder)

    # I should get a dagster.security.WmSecurityManager instance
    msg = 'Object is not a dagster.security.WmSecurityManager instance'
    assert isinstance(sec_man, WmSecurityManager), msg


@unittest.mock.patch('dagster.security.WmSecurityManager._get_aad_group_id')
@unittest.mock.patch('dagster.security.WmSecurityManager._get_msal_auth')
@unittest.mock.patch('dagster.security.utils')
def test_get_oauth_user_info_for_azure(mock_security_utils, mock_msal_headers, mock_group_id):
    """Overridden flask_appbuilder.security.manager.BaseSecurityManager get_oauth_user_info method:
    provider azure.
    """
    # Given an Airflow security manager instance
    app = application.create_app(testing=True)
    appbuilder = app.appbuilder # pylint: disable=no-member
    sec_man = WmSecurityManager(appbuilder)

    # and an OAuth 2.0 provider that is Azure
    provider = 'azure'

    # when I trigger an Azure OAuth 2.0 authentication flow
    mock_msal_headers.return_value = {'Authorization': 'Bearer XXXX'}
    mock_security_utils.msgraph_groups.return_value = []
    blank_group_id = (None, None)
    mock_group_id.side_effect = ((blank_group_id, ) * 5)
    received = sec_man.get_oauth_user_info(provider, ACCESS_TOKEN)
    msg = 'Decoded JWT user auth info error'
    expected = {
        'email': 'John.Doe@coles.com.au',
        'first_name': 'John',
        'id': 'f1688cc8-2eb4-46a2-8a72-XXXXXXXXXXXX',
        'last_name': 'Doe',
        'name': 'John Doe',
        'username': 'f1688cc8-2eb4-46a2-8a72-XXXXXXXXXXXX',
        'airflow_aad_group': None,
    }
    assert received == expected, msg


@unittest.mock.patch('dagster.security.WmSecurityManager._get_aad_group_id')
@unittest.mock.patch('dagster.security.WmSecurityManager._get_msal_auth')
@unittest.mock.patch('dagster.security.utils')
def test_get_oauth_user_info_for_azure_with_aad_group_match(mock_security_utils,
                                                            mock_msal_headers,
                                                            mock_group_id):
    """Overridden flask_appbuilder.security.manager.BaseSecurityManager get_oauth_user_info method:
    provider azure with Airflow AAD group match.
    """
    # Given an Airflow security manager instance
    app = application.create_app(testing=True)
    appbuilder = app.appbuilder # pylint: disable=no-member
    sec_man = WmSecurityManager(appbuilder)

    # and an OAuth 2.0 provider that is Azure
    provider = 'azure'

    # when I trigger an Azure OAuth 2.0 authentication flow
    mock_msal_headers.return_value = {'Authorization': 'Bearer XXXX'}
    mock_security_utils.msgraph_groups.return_value = [
        '270ea4f0-3822-4a0c-ae0c-XXXXXXXXXXXX',
        '15e98e62-e9fa-4730-9088-XXXXXXXXXXXX',
    ]
    mock_group_id.side_effect = [
        (None, None),
        ('INTB-Contributor', '15e98e62-e9fa-4730-9088-XXXXXXXXXXXX')
    ]
    received = sec_man.get_oauth_user_info(provider, ACCESS_TOKEN)
    msg = 'Decoded JWT user auth info error'
    expected = {
        'email': 'John.Doe@coles.com.au',
        'first_name': 'John',
        'id': 'f1688cc8-2eb4-46a2-8a72-XXXXXXXXXXXX',
        'last_name': 'Doe',
        'name': 'John Doe',
        'username': 'f1688cc8-2eb4-46a2-8a72-XXXXXXXXXXXX',
        'airflow_aad_group': 'INTB-Contributor',
    }
    assert received == expected, msg


def test_get_oauth_user_info_for_non_azure():
    """Overridden flask_appbuilder.security.manager.BaseSecurityManager get_oauth_user_info method:
    provider non-azure.
    """
    # Given an Airflow security manager instance
    app = application.create_app(testing=True)
    appbuilder = app.appbuilder # pylint: disable=no-member
    sec_man = WmSecurityManager(appbuilder)

    # and an OAuth 2.0 provider that is not Azure
    provider = 'google'

    # when I trigger an Azure OAuth 2.0 authentication flow
    received = sec_man.get_oauth_user_info(provider, ACCESS_TOKEN)
    msg = 'Decoded JWT user auth info error'
    assert not received, msg


def test_wmsecuritymanager_roles():
    """dagster.security.WmSecurityManager Roles.
    """
    # Given an OAuth 2.0 user login instance
    app = application.create_app(testing=True)
    appbuilder = app.appbuilder # pylint: disable=no-member
    sec_man = WmSecurityManager(appbuilder)

    # when I query the roles
    msg = 'dagster.security.WmSecurityManager object roles error'
    expected = [
        'Public',
        'Viewer',
        'User',
        'Op',
        'Admin',
    ]
    assert sorted([x.get('role') for x in sec_man.ROLE_CONFIGS]) == sorted(expected), msg


@unittest.mock.patch('dagster.security.utils')
def test_get_msal_auth(mock_security_utils):
    """The MSAL authorisation header generator.
    """
    # Given an Airflow security manager instance
    app = application.create_app(testing=True)

    with app.app_context():
        app.config['AZURE_AD_TENANT_ID'] = '82551a12-bbc8-4fed-8b7f-XXXXXXXXXXXX'
        app.config['AZURE_AD_APPLICATION_ID'] = 'e14b29a3-649b-4d03-b458-XXXXXXXXXXXX'
        app.config['AZURE_AD_SECRET'] = 'XXXXXXXXXXXX'

        # when I authenticate using MSAL
        # then I should receive an authorisation header dictionary structure
        mock_security_utils.msgraph_auth.return_value = {'Authorization': 'Bearer XXXX'}
        received = WmSecurityManager._get_msal_auth() # pylint: disable=protected-access

    # then I should receive a dictionary instance
    msg = 'Invalid return instance for _get_msal_auth'
    assert isinstance(received, dict), msg


@unittest.mock.patch('dagster.security.utils')
def test_get_aad_group_id(mock_security_utils):
    """The AAD group ID query helper.
    """
    # Given an Airflow security manager instance
    app = application.create_app(testing=True)

    with app.app_context():
        # and a group name
        app.config['SUPER_AIRFLOW_ADMIN_GROUP'] = 'WM-TechLead'

        # and an MSAL authentication request header
        auth_header = {'Authorization': 'Bearer XXXX'}

        # when I query the MS Graph API
        # then I should receive an AAD group ID
        group_id = '0ecca151-80e1-4baa-8883-XXXXXXXXXXXX'
        mock_security_utils.msgraph_search_group.return_value = group_id
        # pylint: disable=protected-access
        received = WmSecurityManager._get_aad_group_id('SUPER_AIRFLOW_ADMIN_GROUP', auth_header)
        # pylint: enable=protected-access

    # then I should receive a string instance
    msg = 'Invalid return instance for _get_aad_group_id'
    assert received == ('WM-TechLead', '0ecca151-80e1-4baa-8883-XXXXXXXXXXXX'), msg
