"""Convenience class that stores user detail taken from Microsoft identity platform ID tokens.

"""
import datetime
import logging

import dagster.security.utils


class AdUser:
    """Convenience class that stores user detail taken from Microsoft identity platform ID tokens.

    Here, we simulate behaviour produced by the Azure AD B2C product that is stored in
    Flask App-Builder's :class:`flask_appbuilder.security.manager.BaseSecurityManager`
    class instance ``oauth_user_info`` attribute as a base.  We also further extend
    to support custom authentication requirements.

    """
    def __init__(self, id_token_claims: dict):
        """Attributes consumed from *id_token_claims* as per the Microsoft Graph API permissions.

        .. attribute:: oid

        .. attribute:: display_name

        .. attribute:: first_name

        .. attribute:: family_name

        .. attribute:: email

        .. attribute:: time_created
            :module:`datetime` time authorisation occurred

        .. attribute:: aad_groups
            The AAD group IDs this user belongs to

        .. attribute:: airflow_aad_group
            The AAD group ID that is to be used for Airflow authorisation

        """
        self.__oid = id_token_claims.get('oid')
        self.__display_name = id_token_claims.get('name', '')
        self.__first_name = id_token_claims.get('given_name', '')
        self.__email = id_token_claims.get('upn')
        self.__family_name = id_token_claims.get('family_name', '')

        self.__time_created = datetime.datetime.now(datetime.timezone.utc)
        self.__aad_groups = None
        self.__airflow_aad_group = None

        logging.info('User "%s" (oid: %s) authenticated at: %s',
                     self.__display_name,
                     self.__oid,
                     self.__time_created.isoformat())

    @property
    def oid(self):
        """:attr:`self.__oid getter.
        """
        return self.__oid

    @oid.setter
    def oid(self, val):
        """:attr:`self.__oid setter.
        """
        self.__oid = val

    @property
    def display_name(self):
        """:attr:`self.__display_name getter.
        """
        return self.__display_name

    @display_name.setter
    def display_name(self, val):
        """:attr:`self.__display_name setter.
        """
        self.__display_name = val

    @property
    def first_name(self):
        """:attr:`self.__first_name getter.
        """
        return self.__first_name

    @first_name.setter
    def first_name(self, val):
        """:attr:`self.__first_name setter.
        """
        self.__first_name = val

    @property
    def email(self):
        """:attr:`self.__email getter.
        """
        return self.__email

    @email.setter
    def email(self, val):
        """:attr:`self.__email setter.
        """
        self.__email = val

    @property
    def family_name(self):
        """:attr:`self.__family_name getter.
        """
        return self.__family_name

    @family_name.setter
    def family_name(self, val):
        """:attr:`self.__family_name setter.
        """
        self.__family_name = val

    @property
    def time_created(self):
        """:attr:`self.__time_created getter.
        """
        return self.__time_created

    @property
    def aad_groups(self):
        """:attr:`self.__aad_groups getter.
        """
        return self.__aad_groups

    @aad_groups.setter
    def aad_groups(self, val):
        """:attr:`self.__aad_groups setter.
        """
        if not self.__aad_groups:
            self.__aad_groups = []
        else:
            self.__aad_groups.clear()
        if isinstance(val, list):
            self.__aad_groups.extend(val)
        else:
            self.__aad_groups.append(val)

    @property
    def airflow_aad_group(self):
        """:attr:`self.__airflow_aad_group getter.
        """
        return self.__airflow_aad_group

    @airflow_aad_group.setter
    def airflow_aad_group(self, val):
        """:attr:`self.__airflow_aad_group setter.
        """
        self.__airflow_aad_group = val

    @property
    def azure_user_info(self):
        """Simulate the Azure return behaviour from
        class:`flask_appbuilder.security.manager.BaseSecurityManager` get_oauth_user_info method.

        """
        return {
            'name': self.display_name,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.family_name,
            'id': self.oid,
            'username': self.oid,
            'airflow_aad_group': self.airflow_aad_group,
        }

    def query_aad_groups(self, auth_header: str):
        """Query MS Graph API for all the AAD groups that the user belongs to.

        Set the :att:`aad_groups` attribute with list of all groups.

        """
        self.aad_groups = dagster.security.utils.msgraph_groups(self.oid, auth_header)


    def user_in_group_check(self, group_id: str) -> bool:
        """Check if *group_id* exists in :attr:`aad_groups`.

        Returns boolean ``True`` if match found.  ``False`` otherwise.

        """
        is_matched = False
        logging.info("Checking if AAD group ID \"%s\" is part of user's groups", group_id)
        if group_id in self.aad_groups:
            logging.info('AAD group ID "%s" matched', group_id)
            is_matched = True

        return is_matched
