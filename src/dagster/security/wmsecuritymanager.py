"""WorkflowManager implementation of :class:`airflow.www.security.AirflowSecurityManager`.

"""
import logging
from typing import Tuple
from flask import current_app
from airflow.www.security import AirflowSecurityManager

import dagster.security


class WmSecurityManager(AirflowSecurityManager):
    """Customised :class:`airflow.www.security.AirflowSecurityManager` for enhanced
    integration with Azure Active Directory.

    The Azure AD B2C product does not yet support including group membership information in
    the id_token claims.  Instead, we use Microsoft's Graph API to access group information.
    To hook this into the auth model we need to update Flask App-Builder's
    :class:`flask_appbuilder.security.manager.BaseSecurityManager` class instance
    ``oauth_user_info`` attribute.

    """
    def get_oauth_user_info(self, provider, resp) -> dict:
        """Override of :class:`flask_appbuilder.security.manager.BaseSecurityManager`
        ``get_oauth_user_info`` method.

        Only supporting Microsoft Azure OAuth 2.0 as a provider.

        Azure OAuth response contains:
        - JWT token which has user info
        - JWT token needs to be base64 decoded

        See https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-protocols-oauth-code

        Here, we are also extending the base structure with AAD group information context.

        """
        user_info = {}

        if provider == 'azure':
            logging.debug('Azure response received: %s', resp)
            id_token = resp.get('id_token')
            decode_payload = self._azure_jwt_token_parse(id_token)

            user = dagster.security.AdUser(decode_payload)
            auth_header = WmSecurityManager._get_msal_auth()
            user.query_aad_groups(auth_header)

            # Order from most privilege to least privileges.
            aad_group_vars = [
                'SUPER_AIRFLOW_ADMIN_GROUP',
                'AIRFLOW_ADMIN_GROUP',
                'AIRFLOW_OP_GROUP_V1',
                'AIRFLOW_OP_GROUP_V2',
                'AIRFLOW_VIEWER_GROUP',
            ]
            for aad_group_var in aad_group_vars:
                (group_name, group_id) = WmSecurityManager._get_aad_group_id(aad_group_var,
                                                                             auth_header)
                if group_id:
                    if user.user_in_group_check(group_id):
                        logging.info('Airflow AAD match for authorisation: "%s"', group_name)
                        user.airflow_aad_group = group_name
                        break

            user_info.update(user.azure_user_info)

        return user_info

    @staticmethod
    def _get_aad_group_id(aad_group_var: str, headers: str) -> Tuple[str, str]:
        """Query the AAD group ID for the given *aad_group_var*.

        Returns the AAD group UUID in string format on success else``None``.

        """
        group_name = current_app.appbuilder.get_app.config.get(aad_group_var)
        logging.info('Processing AAD group variable name "%s" with AAD group "%s"',
                     aad_group_var, group_name)
        group_id = None
        if group_name:
            group_id = dagster.security.utils.msgraph_search_group(group_name, headers)
        else:
            logging.info('AAD Group environment variable "%s" undefined: skipping MS Graph lookup',
                         aad_group_var)

        return (group_name, group_id)

    @staticmethod
    def _get_msal_auth() -> dict:
        """Helper method to generate a MSAL authorisation header.

        """
        kwargs = {
            'tenant_id': current_app.appbuilder.get_app.config.get('AZURE_AD_TENANT_ID'),
            'client_id': current_app.appbuilder.get_app.config.get('AZURE_AD_APPLICATION_ID'),
            'client_secret': current_app.appbuilder.get_app.config.get('AZURE_AD_SECRET'),
        }
        auth_header = dagster.security.utils.msgraph_auth(**kwargs)

        return auth_header
