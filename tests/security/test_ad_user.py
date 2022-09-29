""":class:`dagster.security.AdUser` unit test cases.
"""
import datetime
import unittest.mock

from dagster.security import AdUser


@unittest.mock.patch('dagster.security.ad_user.datetime')
def test_user_init(mock_datetime):
    """Initialise a dagster.security.AdUser object.
    """
    # Given a dictionary of id_token_claims
    id_token_claims = {
        'aud': '2aeb06fa-2827-40e3-8bf7-XXXXXXXXXXXX',
        'iss': 'https://sts.windows.net/82551a12-bbc8-4fed-8b7f-2b758284b5ea/',
        'iat': 1621740501,
        'nbf': 1621740501,
        'exp': 1621744401,
        'amr': ['pwd', 'mfa'],
        'family_name': 'Doe',
        'given_name': 'John',
        'ipaddr': '127.0.0.1',
        'name': 'John Doe',
        'oid': 'f1688cc8-2eb4-46a2-8a72-XXXXXXXXXXXX',
        'onprem_sid': 'S-1-5-21-9122744-1558073900-1550850067-1020880',
        'rh': '0.AQYAEhpVgsi77U-Lfyt1goS16voG6yonKONAi_cr90EwX2UGAJA.',
        'sub': 'XaIAK1k807N3fSSFk8hdYELgRSYAszPZQKzcNQp2388',
        'tid': '82551a12-bbc8-4fed-8b7f-XXXXXXXXXXXX',
        'unique_name': 'John.Doe@email.com.au',
        'upn': 'John.Doe@email.com.au',
        'ver': '1.0'
    }

    # when I initialise a dagster.security.AdUser object
    mock_datetime.datetime.now.return_value = datetime.datetime(2020, 12, 1, 14, 53, 4)
    user = AdUser(id_token_claims)

    # then I should get a dagster.security.AdUser instance
    msg = 'Object is not a dagster.security.AdUser instance'
    assert isinstance(user, AdUser), msg

    # and the attributes should match
    assert user.oid == 'f1688cc8-2eb4-46a2-8a72-XXXXXXXXXXXX', 'AdUser.oid error'
    assert user.display_name == 'John Doe', 'AdUser.display_name error'
    assert user.email == 'John.Doe@email.com.au', 'AdUser.email error'
    assert user.first_name == 'John', 'AdUser.first_name error'
    assert user.family_name == 'Doe', 'AdUser.family_name error'
    assert str(user.time_created.isoformat()) == '2020-12-01T14:53:04', 'AdUser.time_created error'

    expected = {
        'first_name': 'John',
        'id': 'f1688cc8-2eb4-46a2-8a72-XXXXXXXXXXXX',
        'last_name': 'Doe',
        'name': 'John Doe',
        'username': 'f1688cc8-2eb4-46a2-8a72-XXXXXXXXXXXX',
        'email': 'John.Doe@email.com.au',
        'airflow_aad_group': None,
    }
    assert user.azure_user_info == expected, 'AdUser.azure_user_info error'


@unittest.mock.patch('dagster.security.utils')
def test_query_aad_groups(mock_security_utils):
    """Query the remote MS Graph API for all the groups that user belongs to.
    """
    # Given a MSAL user context
    id_token_claims = {}
    user = AdUser(id_token_claims)

    # and a MSAL request header
    auth_header = {'Authorization': 'Bearer XXXX'}

    # when I query the MS Graph API for AAD groups
    mock_security_utils.msgraph_groups.return_value = [
        '270ea4f0-3822-4a0c-ae0c-XXXXXXXXXXXX',
        '15e98e62-e9fa-4730-9088-XXXXXXXXXXXX',
    ]
    user.query_aad_groups(auth_header)

    # then I should be able to obtain the user context AAD groups
    expected = [
        '270ea4f0-3822-4a0c-ae0c-XXXXXXXXXXXX',
        '15e98e62-e9fa-4730-9088-XXXXXXXXXXXX',
    ]
    msg = 'AD User context AAD groups list error'
    assert user.aad_groups == expected, msg


def test_user_in_group_check_and_matched():
    """Check if AAD group ID exists in MSAL user context: match found.
    """
    # Given a MSAL user context
    id_token_claims = {}
    user = AdUser(id_token_claims)

    # with a set of MSAL user context AAD groups of which the user belongs
    user.aad_groups = [
        '270ea4f0-3822-4a0c-ae0c-XXXXXXXXXXXX',
        '15e98e62-e9fa-4730-9088-XXXXXXXXXXXX',
    ]

    # when I query the MSAL user context AAD groups with a group that the user belongs to
    group_id = '15e98e62-e9fa-4730-9088-XXXXXXXXXXXX'
    received = user.user_in_group_check(group_id)

    # then I should receive a match
    msg = 'AAD group search in MSAL user context where user belongs error'
    assert received, msg


def test_user_in_group_check_and_not_matched():
    """Check if AAD group ID exists in MSAL user context: match not found.
    """
    # Given a MSAL user context
    id_token_claims = {}
    user = AdUser(id_token_claims)

    # with a set of MSAL user context AAD groups of which the user belongs
    user.aad_groups = [
        '270ea4f0-3822-4a0c-ae0c-XXXXXXXXXXXX',
        '15e98e62-e9fa-4730-9088-XXXXXXXXXXXX',
    ]

    # when I query the MSAL user context AAD groups with a group that the user belongs to
    group_id = 'X5e98e62-e9fa-4730-9088-XXXXXXXXXXXX'
    received = user.user_in_group_check(group_id)

    # then I should not receive a match
    msg = 'AAD group search in MSAL user context where user does not belong error'
    assert not received, msg
