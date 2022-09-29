""":module:`dagster.security.utils` unit test cases.
"""
import unittest.mock
import pytest

import dagster.security.utils as sec_utils


ACCESS_TOKEN = {
    'token_type': 'Bearer',
    'expires_in': 3599,
    'ext_expires_in': 3599,
    'access_token': (
        'eyJ0eXAiOiJKV1QiLCJub25jZSI6IkdSRWZLcFk2UUJWeWVWU21CUEw2d3Y3cFNGeTlmX19qSVVHRGhwN0d2OT'
        'giLCJhbGciOiJSUzI1NiIsIng1dCI6Im5PbzNaRHJPRFhFSzFqS1doWHNsSFJfS1hFZyIsImtpZCI6Im5PbzNa'
        'RHJPRFhFSzFqS1doWHNsSFJfS1hFZyJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20iLCJpc'
        '3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC84MjU1MWExMi1iYmM4LTRmZWQtOGI3Zi0yYjc1ODI4NGI1ZWE'
        'vIiwiaWF0IjoxNjIxODYyMTk3LCJuYmYiOjE2MjE4NjIxOTcsImV4cCI6MTYyMTg2NjA5NywiYWlvIjoiRTJaZ'
        '1lPaSszbXB6em5xZHozUURENk5uMVF0VEFRPT0iLCJhcHBfZGlzcGxheW5hbWUiOiJTUE4tQ29sZXMtREVWLUl'
        'OVEVHUkFUSU9OLVdGTS1PQVVUSC1BQUQiLCJhcHBpZCI6ImUxNGIyOWEzLTY0OWItNGQwMy1iNDU4LWYwY2I4Y'
        'zRlZDUwYyIsImFwcGlkYWNyIjoiMSIsImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0LzgyNTUxYTEyLWJ'
        'iYzgtNGZlZC04YjdmLTJiNzU4Mjg0YjVlYS8iLCJpZHR5cCI6ImFwcCIsIm9pZCI6ImFjYTNjNzk2LWUyNWItN'
        'GI2Zi05YjVlLTVkZjU3MjRlYWIyOSIsInJoIjoiMC5BUVlBRWhwVmdzaTc3VS1MZnl0MWdvUzE2cU1wUy1HYlp'
        'BTk50Rmp3eTR4TzFRd0dBQUEuIiwicm9sZXMiOlsiRG9tYWluLlJlYWQuQWxsIl0sInN1YiI6ImFjYTNjNzk2L'
        'WUyNWItNGI2Zi05YjVlLTVkZjU3MjRlYWIyOSIsInRlbmFudF9yZWdpb25fc2NvcGUiOiJPQyIsInRpZCI6Ijg'
        'yNTUxYTEyLWJiYzgtNGZlZC04YjdmLTJiNzU4Mjg0YjVlYSIsInV0aSI6Im9ZQ0w1OWFHVkVPUDUxWVpjUTA3Q'
        'UEiLCJ2ZXIiOiIxLjAiLCJ4bXNfdGNkdCI6MTM2NTEwNjMzNH0.j3suowlDJx_8NmMfQmkOOs7bS_Suc1Jt8O1'
        'iRzA1z02u-2ZAFKewwo3Luo2vQJjiEMe7inHMk1Q6VrYIUIVrivgAur03X7_Jf0IZBql1y11FoV3K7HcdPkrpB'
        'ddZcdx3jFjmBgiBPo-LCI3bq_XvCbkm3jXnFO9uhPy8vHQhim4FvlwZI51uOXe05n88kysZdL5Ho8DoZTl97-E'
        'GFjNvecJMBnizQePgWPucSgdOkObjU9BPzU8nYScCD2trf2Lb9GsIdHjmRUGlBleSr2ajr2S1QVHXBZiWkHtjg'
        'f7nnIlTK2TrCh0l47d2t8bHyZ6JFvqI0gtOqptZlriJ6Pd9rg'
    )
}

ACCESS_TOKEN_ERROR = {
    'error': 'unauthorized_client',
    'error_description':
        ("AADSTS700016: Application with identifier 'e14b29a3-649b-4d03-b458-XXXXXXXXXXXX' was not "
         "found in the directory '82551a12-bbc8-4fed-8b7f-XXXXXXXXXXXX'. This can happen if the app"
         "lication has not been installed by the administrator of the tenant or consented to by any"
         " user in the tenant. You may have sent your authentication request to the wrong tenant.\r"
         "\nTrace ID: 13b30bc1-c485-4cca-a776-3bf98edb8201\r\nCorrelation ID: 81d38843-2a98-4345-bc"
         "15-8f119e136eb8\r\nTimestamp: 2021-05-27 22:56:47Z"),
    'error_codes': [700016],
    'timestamp': '2021-05-27 22:56:47Z',
    'trace_id': '13b30bc1-c485-4cca-a776-3bf98edb8201',
    'correlation_id': '81d38843-2a98-4345-bc15-8f119e136eb8',
    'error_uri': 'https://login.microsoftonline.com/error?code=700016'
}


GROUP_DATA = {
    '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#groups',
    'value': [
        {
            '@odata.id':
                ('https://graph.microsoft.com/v2/82551a12-bbc8-4fed-8b7f-2b758284b5ea/directoryObje'
                 'cts/0ecca151-80e1-4baa-8883-c8cbf07ad013/Microsoft.DirectoryServices.Group'),
            'id': '0ecca151-80e1-4baa-8883-XXXXXXXXXXXX',
            'deletedDateTime': None,
            'classification': None,
            'createdDateTime': '2020-06-11T06:39:51Z',
            'creationOptions': [],
            'description': None,
            'displayName': 'INTB-TechLead',
            'expirationDateTime': None,
            'groupTypes': [],
            'isAssignableToRole': None,
            'mail': None,
            'mailEnabled': False,
            'mailNickname': 'BposMailNickName',
            'membershipRule': None,
            'membershipRuleProcessingState': None,
            'onPremisesDomainName': None,
            'onPremisesLastSyncDateTime': None,
            'onPremisesNetBiosName': None,
            'onPremisesSamAccountName': None,
            'onPremisesSecurityIdentifier': None,
            'onPremisesSyncEnabled': None,
            'preferredDataLocation': None,
            'preferredLanguage': None,
            'proxyAddresses': [],
            'renewedDateTime': '2020-06-11T06:39:51Z',
            'resourceBehaviorOptions': [],
            'resourceProvisioningOptions': [],
            'securityEnabled': True,
            'securityIdentifier': 'S-1-12-1-248291665-1269465313-3418915720-332430064',
            'theme': None,
            'visibility': None,
            'onPremisesProvisioningErrors': [],
        }
    ]
}


MEMBER_GROUPS = {
    '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#Collection(Edm.String)',
    'value': [
        '270ea4f0-3822-4a0c-ae0c-XXXXXXXXXXXX',
        '15e98e62-e9fa-4730-9088-XXXXXXXXXXXX',
        'e06daeb2-4d83-4475-95e9-XXXXXXXXXXXX',
        'bd1a88ca-2620-4088-8a93-XXXXXXXXXXXX',
        '7c478cdf-33a1-4d2a-89b1-XXXXXXXXXXXX',
        '876e2d50-b177-4c50-b232-XXXXXXXXXXXX',
        '6f06b85e-1023-4127-8136-XXXXXXXXXXXX',
        '52a205a1-0cb0-4cec-b1ed-XXXXXXXXXXXX',
        '5a98be14-fdcb-4647-b501-XXXXXXXXXXXX',
        '44f4bcb0-7708-4efb-b35f-XXXXXXXXXXXX',
        '2ee6fec3-bf0d-4aef-8796-XXXXXXXXXXXX',
        'ae8bc507-963e-4487-809b-XXXXXXXXXXXX',
        '41be808c-b42f-4c1c-9dca-XXXXXXXXXXXX',
        '0898dfdd-f25b-4550-a063-XXXXXXXXXXXX',
        'dfb29f1a-6bbd-4fe9-9204-XXXXXXXXXXXX',
        '52098861-1403-461d-8cca-XXXXXXXXXXXX',
        '159ef636-6c89-454e-9019-XXXXXXXXXXXX',
        '0449183b-6c2e-4b66-a0b9-XXXXXXXXXXXX',
        '77a23e70-5c72-45ef-8ebe-XXXXXXXXXXXX',
        '7f8fb470-7678-4b19-89f1-XXXXXXXXXXXX',
        'a0ed918b-b96d-4567-9249-XXXXXXXXXXXX',
        '9c648913-61a9-4582-924e-XXXXXXXXXXXX',
        '4ab8d396-5b1b-44c4-8330-XXXXXXXXXXXX',
        'b3e8074c-4a7e-46af-8bb1-XXXXXXXXXXXX',
        '296a0452-69aa-460b-a480-XXXXXXXXXXXX',
        '62d60d5e-8fc8-465b-a733-XXXXXXXXXXXX',
        '73a602e8-1189-4ac3-acb5-XXXXXXXXXXXX',
        '216b2e61-9f3d-4acc-a640-XXXXXXXXXXXX',
        '4a72a5c6-c808-4423-b169-XXXXXXXXXXXX',
        'b320ef57-2c8c-44a9-8ab4-XXXXXXXXXXXX',
        'a5003b3c-a897-4b3c-8432-XXXXXXXXXXXX',
        '605e9c4d-84ee-49db-90c2-XXXXXXXXXXXX',
        '8c0bf4c7-ee9f-4658-8c49-XXXXXXXXXXXX',
        '89e78123-e3c9-4a40-b6de-XXXXXXXXXXXX',
        'a4d09fa5-86b6-4934-8a70-XXXXXXXXXXXX',
        '0a0b5f3f-d1e7-4b27-bd3e-XXXXXXXXXXXX',
        '0ecca151-80e1-4baa-8883-XXXXXXXXXXXX',
        '8261d278-e063-49a4-b957-XXXXXXXXXXXX',
        '178033f4-957f-4260-9d9e-XXXXXXXXXXXX',
        '3421a2d5-7ffa-4838-9873-XXXXXXXXXXXX',
        '80e4a77f-2fbc-4e35-9fc4-XXXXXXXXXXXX',
        '5969fedd-ea2b-48ef-8bb9-XXXXXXXXXXXX',
        'ff6c377a-8f84-42ae-ab9d-XXXXXXXXXXXX',
        'f5389c2f-1f19-4ea7-9fbc-XXXXXXXXXXXX',
        '3086889d-fc66-480d-81e2-XXXXXXXXXXXX',
        '7d4d40ce-ac8b-4116-a7f0-XXXXXXXXXXXX',
        '7c2ba6d6-f874-4bb3-b180-XXXXXXXXXXXX',
        '9c789114-81d1-49fe-a213-XXXXXXXXXXXX',
        '403c9c4b-e920-4efa-be49-XXXXXXXXXXXX',
        '73610cf7-ebee-4aec-b6e5-XXXXXXXXXXXX',
        '0a88e858-1be3-4c50-930d-XXXXXXXXXXXX',
        'cf8cd328-0bbf-4f3d-9dd2-XXXXXXXXXXXX',
        '1b883f7f-0ab1-4a1c-a14a-XXXXXXXXXXXX',
        '3942b801-6946-4b2c-ab35-XXXXXXXXXXXX'
    ]
}


@pytest.fixture()
def mock_graph_auth(access_token) -> dict:
    """Return an auth header for HTTPS requests.

    """
    tenant_id = '82551a12-bbc8-4fed-8b7f-XXXXXXXXXXXX'
    client_id = 'e14b29a3-649b-4d03-b458-XXXXXXXXXXXX'
    client_secret = 'BvIqGA-Sb4lgo6-XXXXXXXXXXXXXXXXXXX'

    with unittest.mock.patch('msal.ConfidentialClientApplication') as mock_msal_context:
        mock_msal_context.return_value.acquire_token_silent.return_value = None
        mock_msal_context.return_value.acquire_token_for_client.return_value = access_token

        yield sec_utils.msgraph_auth(tenant_id, client_id, client_secret)


@pytest.mark.skip(reason='Since jyPWT 2.4.0 seeing "Could not deserialize ..." error')
@pytest.mark.parametrize('access_token', [ACCESS_TOKEN])
def test_msgraph_auth(mock_graph_auth): # pylint: disable=redefined-outer-name
    """Authenticate to Microsoft Graph.
    """
    # When I auth against the Microsoft Graph API
    # then I should receive an authorisation header
    msg = 'MS Graph MSAL auth error'
    assert list(mock_graph_auth.keys()) == ['Authorization'], msg


@pytest.mark.parametrize('access_token', [ACCESS_TOKEN_ERROR])
def test_msgraph_auth_error(mock_graph_auth): # pylint: disable=redefined-outer-name
    """Authenticate to Microsoft Graph returning an auth error.
    """
    # When I auth against the Microsoft Graph API with incorrect credentials
    # then the authorisation header should be undefined
    msg = 'MS Graph MSAL auth with incorrect credentials did not return None'
    assert not mock_graph_auth, msg


@unittest.mock.patch('requests.get')
def test_msgraph_group_search(mock_request):
    """Get group with $search against displayName.
    """
    # Given a AAD Group name
    group_name = 'INTB-TechLead'

    # and a auth request header
    request_header = {'Authorization': 'Bearer XXXX'}

    # when I search for a valid AAD Group
    mock_request.return_value.json.return_value = GROUP_DATA
    received = sec_utils.msgraph_search_group(group_name, request_header)

    # then I should receive a group UID
    msg = 'MS Graph search against displayName did not return a group UID'
    assert received == '0ecca151-80e1-4baa-8883-XXXXXXXXXXXX', msg


@unittest.mock.patch('requests.get')
def test_msgraph_group_search_no_match(mock_request):
    """Get group with $search against displayName: no match.
    """
    # Given a AAD Group name that does not exist
    group_name = 'INTB-Dummy'

    # and a auth request header
    request_header = {'Authorization': 'Bearer XXXX'}

    # when I search for an invalid AAD Group
    mock_request.return_value.json.return_value = {
        '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#groups',
        'value': []
    }
    received = sec_utils.msgraph_search_group(group_name, request_header)

    # then I should receive None
    msg = 'MS Graph search against unknown displayName did not return None'
    assert not received, msg


@unittest.mock.patch('requests.post')
def test_msgraph_groups(mock_request):
    """Return all the groups that the user is a member of.
    """
    # Given a user ID
    user_id = 'f1688cc8-2eb4-46a2-8a72-XXXXXXXXXXXX'

    # and a auth request header
    request_header = {'Authorization': 'Bearer XXXX'}

    # when I search for all AAD Groups that user ID is part of
    mock_request.return_value.json.return_value = MEMBER_GROUPS
    received = sec_utils.msgraph_groups(user_id, request_header)

    # then I should receive a non-zero count of AAD Groups
    msg = 'MS Graph AAD Groups for user count error'
    assert received, msg


@unittest.mock.patch('requests.post')
def test_msgraph_groups_for_user_with_no_groups(mock_request):
    """Return all the groups that the user is a member of: no groups.
    """
    # Given a user ID
    user_id = 'f1688cc8-2eb4-46a2-8a72-XXXXXXXXXXXX'

    # and a auth request header
    request_header = {'Authorization': 'Bearer XXXX'}

    # when I search for all AAD Groups that user ID is part of
    mock_request.return_value.json.return_value = {
        '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#Collection(Edm.String)',
        'value': []
    }
    received = sec_utils.msgraph_groups(user_id, request_header)

    # then I should receive a zero count of AAD Groups
    msg = 'MS Graph AAD Groups count error for no groups returned'
    assert not received, msg
