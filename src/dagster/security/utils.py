"""WorkflowManager security utils.

"""
import logging
import datetime
import requests
import jwt
import msal

AZURE_AUTHORITY = 'https://login.microsoftonline.com'
MS_GRAPH_ENDPOINT = 'https://graph.microsoft.com'


def msgraph_auth(tenant_id: str, client_id: str, client_secret: str) -> dict:
    """Authenticate to Microsoft Graph.

    See https://docs.microsoft.com/en-us/azure/active-directory/develop/id-tokens

    Returns a dictionary that can be used as the request header for
    subsequent authorised queries to Microsoft Graph or ``None`` on failure.
    For example::

        {'Authorization': 'Bearer <access_token>'}

    """
    logging.info('Authenticating to Microsoft Graph')
    authority = f'{AZURE_AUTHORITY}/{tenant_id}'
    app = msal.ConfidentialClientApplication(client_id,
                                             authority=authority,
                                             client_credential=client_secret)

    request_headers = None
    access_token = None

    scope = ['https://graph.microsoft.com/.default']
    cached_token = app.acquire_token_silent(scope, account=None)
    if cached_token:
        access_token = cached_token
    else:
        acquired_token = app.acquire_token_for_client(scopes=scope)
        access_token = acquired_token.get('access_token')
        if access_token:
            request_headers = {'Authorization': f'Bearer {access_token}'}
        else:
            logging.error('%s: %s',
                          acquired_token.get('error'),
                          acquired_token.get('error_description'))

    if access_token:
        decoded_access_token = jwt.decode(access_token, verify=False, algorithms=['RS256'])

        token_expiry = datetime.datetime.fromtimestamp(int(decoded_access_token.get('exp')))
        logging.info('Token Expires at: %s', str(token_expiry))

    return request_headers


def msgraph_search_group(group_name: str, headers: dict) -> str:
    """MS Graph request using the microsoft.graph $search facility to get groups with display names
    that contain the letters *group_name*.

    See https://docs.microsoft.com/en-us/graph/api/group-list?view=graph-rest-1.0&tabs=http#examples

    Returns the AAD Group's UUID on success.  Otherwise, ``None``.

    """
    headers.update({'ConsistencyLevel': 'eventual'})
    group_data = requests.get(f'{MS_GRAPH_ENDPOINT}/v1.0/groups?$search="displayName:{group_name}"',
                              headers=headers).json()

    result = [d for d in group_data.get('value') if d['displayName'] == group_name]
    group_id = None
    if result:
        group_id = result[0].get('id')
    logging.info('Group ID for displayName "%s": %s', group_name, group_id)

    return group_id


def msgraph_groups(user_id: str, headers: str) -> list:
    """MS Graph request using the microsoft.graph user: getMemberGroups.

    Return all the groups that the *user_id* is a member of.  See
    https://docs.microsoft.com/en-us/graph/api/user-getmembergroups?view=graph-rest-1.0&tabs=httc

    Returns a list of AAD Group UUID that *user_id* belongs to on success.  Otherwise, ``None``.

    """
    groups = requests.post(f'{MS_GRAPH_ENDPOINT}/v1.0/users/{user_id}/getMemberGroups',
                           headers=headers,
                           json={'securityEnabledOnly': 'false'}).json()

    group_uuids = groups.get('value')
    logging.info('User: "%s" belongs to %s groups', user_id, len(group_uuids))

    return group_uuids
