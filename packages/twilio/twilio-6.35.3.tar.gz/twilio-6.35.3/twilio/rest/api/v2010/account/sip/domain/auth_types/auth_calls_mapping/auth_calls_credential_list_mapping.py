# coding=utf-8
r"""
This code was generated by
\ / _    _  _|   _  _
 | (_)\/(_)(_|\/| |(/_  v1.0.0
      /       /
"""

from twilio.base import deserialize
from twilio.base import values
from twilio.base.instance_context import InstanceContext
from twilio.base.instance_resource import InstanceResource
from twilio.base.list_resource import ListResource
from twilio.base.page import Page


class AuthCallsCredentialListMappingList(ListResource):
    """  """

    def __init__(self, version, account_sid, domain_sid):
        """
        Initialize the AuthCallsCredentialListMappingList

        :param Version version: Version that contains the resource
        :param account_sid: The SID of the Account that created the resource
        :param domain_sid: The unique string that identifies the resource

        :returns: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingList
        :rtype: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingList
        """
        super(AuthCallsCredentialListMappingList, self).__init__(version)

        # Path Solution
        self._solution = {'account_sid': account_sid, 'domain_sid': domain_sid, }
        self._uri = '/Accounts/{account_sid}/SIP/Domains/{domain_sid}/Auth/Calls/CredentialListMappings.json'.format(**self._solution)

    def create(self, credential_list_sid):
        """
        Create the AuthCallsCredentialListMappingInstance

        :param unicode credential_list_sid: The SID of the CredentialList resource to map to the SIP domain

        :returns: The created AuthCallsCredentialListMappingInstance
        :rtype: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingInstance
        """
        data = values.of({'CredentialListSid': credential_list_sid, })

        payload = self._version.create(method='POST', uri=self._uri, data=data, )

        return AuthCallsCredentialListMappingInstance(
            self._version,
            payload,
            account_sid=self._solution['account_sid'],
            domain_sid=self._solution['domain_sid'],
        )

    def stream(self, limit=None, page_size=None):
        """
        Streams AuthCallsCredentialListMappingInstance records from the API as a generator stream.
        This operation lazily loads records as efficiently as possible until the limit
        is reached.
        The results are returned as a generator, so this operation is memory efficient.

        :param int limit: Upper limit for the number of records to return. stream()
                          guarantees to never return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, stream() will attempt to read the
                              limit with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(page_size=limits['page_size'], )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, limit=None, page_size=None):
        """
        Lists AuthCallsCredentialListMappingInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingInstance]
        """
        return list(self.stream(limit=limit, page_size=page_size, ))

    def page(self, page_token=values.unset, page_number=values.unset,
             page_size=values.unset):
        """
        Retrieve a single page of AuthCallsCredentialListMappingInstance records from the API.
        Request is executed immediately

        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of AuthCallsCredentialListMappingInstance
        :rtype: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingPage
        """
        data = values.of({'PageToken': page_token, 'Page': page_number, 'PageSize': page_size, })

        response = self._version.page(method='GET', uri=self._uri, params=data, )

        return AuthCallsCredentialListMappingPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of AuthCallsCredentialListMappingInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of AuthCallsCredentialListMappingInstance
        :rtype: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return AuthCallsCredentialListMappingPage(self._version, response, self._solution)

    def get(self, sid):
        """
        Constructs a AuthCallsCredentialListMappingContext

        :param sid: The unique string that identifies the resource

        :returns: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingContext
        :rtype: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingContext
        """
        return AuthCallsCredentialListMappingContext(
            self._version,
            account_sid=self._solution['account_sid'],
            domain_sid=self._solution['domain_sid'],
            sid=sid,
        )

    def __call__(self, sid):
        """
        Constructs a AuthCallsCredentialListMappingContext

        :param sid: The unique string that identifies the resource

        :returns: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingContext
        :rtype: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingContext
        """
        return AuthCallsCredentialListMappingContext(
            self._version,
            account_sid=self._solution['account_sid'],
            domain_sid=self._solution['domain_sid'],
            sid=sid,
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Api.V2010.AuthCallsCredentialListMappingList>'


class AuthCallsCredentialListMappingPage(Page):
    """  """

    def __init__(self, version, response, solution):
        """
        Initialize the AuthCallsCredentialListMappingPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API
        :param account_sid: The SID of the Account that created the resource
        :param domain_sid: The unique string that identifies the resource

        :returns: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingPage
        :rtype: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingPage
        """
        super(AuthCallsCredentialListMappingPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of AuthCallsCredentialListMappingInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingInstance
        :rtype: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingInstance
        """
        return AuthCallsCredentialListMappingInstance(
            self._version,
            payload,
            account_sid=self._solution['account_sid'],
            domain_sid=self._solution['domain_sid'],
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Api.V2010.AuthCallsCredentialListMappingPage>'


class AuthCallsCredentialListMappingContext(InstanceContext):
    """  """

    def __init__(self, version, account_sid, domain_sid, sid):
        """
        Initialize the AuthCallsCredentialListMappingContext

        :param Version version: Version that contains the resource
        :param account_sid: The SID of the Account that created the resource to fetch
        :param domain_sid: The SID of the SIP domain that contains the resource to fetch
        :param sid: The unique string that identifies the resource

        :returns: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingContext
        :rtype: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingContext
        """
        super(AuthCallsCredentialListMappingContext, self).__init__(version)

        # Path Solution
        self._solution = {'account_sid': account_sid, 'domain_sid': domain_sid, 'sid': sid, }
        self._uri = '/Accounts/{account_sid}/SIP/Domains/{domain_sid}/Auth/Calls/CredentialListMappings/{sid}.json'.format(**self._solution)

    def fetch(self):
        """
        Fetch the AuthCallsCredentialListMappingInstance

        :returns: The fetched AuthCallsCredentialListMappingInstance
        :rtype: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return AuthCallsCredentialListMappingInstance(
            self._version,
            payload,
            account_sid=self._solution['account_sid'],
            domain_sid=self._solution['domain_sid'],
            sid=self._solution['sid'],
        )

    def delete(self):
        """
        Deletes the AuthCallsCredentialListMappingInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._version.delete(method='DELETE', uri=self._uri, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Api.V2010.AuthCallsCredentialListMappingContext {}>'.format(context)


class AuthCallsCredentialListMappingInstance(InstanceResource):
    """  """

    def __init__(self, version, payload, account_sid, domain_sid, sid=None):
        """
        Initialize the AuthCallsCredentialListMappingInstance

        :returns: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingInstance
        :rtype: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingInstance
        """
        super(AuthCallsCredentialListMappingInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'account_sid': payload.get('account_sid'),
            'date_created': deserialize.rfc2822_datetime(payload.get('date_created')),
            'date_updated': deserialize.rfc2822_datetime(payload.get('date_updated')),
            'friendly_name': payload.get('friendly_name'),
            'sid': payload.get('sid'),
        }

        # Context
        self._context = None
        self._solution = {
            'account_sid': account_sid,
            'domain_sid': domain_sid,
            'sid': sid or self._properties['sid'],
        }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: AuthCallsCredentialListMappingContext for this AuthCallsCredentialListMappingInstance
        :rtype: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingContext
        """
        if self._context is None:
            self._context = AuthCallsCredentialListMappingContext(
                self._version,
                account_sid=self._solution['account_sid'],
                domain_sid=self._solution['domain_sid'],
                sid=self._solution['sid'],
            )
        return self._context

    @property
    def account_sid(self):
        """
        :returns: The SID of the Account that created the resource
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def date_created(self):
        """
        :returns: The RFC 2822 date and time in GMT that the resource was created
        :rtype: datetime
        """
        return self._properties['date_created']

    @property
    def date_updated(self):
        """
        :returns: The RFC 2822 date and time in GMT that the resource was last updated
        :rtype: datetime
        """
        return self._properties['date_updated']

    @property
    def friendly_name(self):
        """
        :returns: The string that you assigned to describe the resource
        :rtype: unicode
        """
        return self._properties['friendly_name']

    @property
    def sid(self):
        """
        :returns: The unique string that identifies the resource
        :rtype: unicode
        """
        return self._properties['sid']

    def fetch(self):
        """
        Fetch the AuthCallsCredentialListMappingInstance

        :returns: The fetched AuthCallsCredentialListMappingInstance
        :rtype: twilio.rest.api.v2010.account.sip.domain.auth_types.auth_calls_mapping.auth_calls_credential_list_mapping.AuthCallsCredentialListMappingInstance
        """
        return self._proxy.fetch()

    def delete(self):
        """
        Deletes the AuthCallsCredentialListMappingInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._proxy.delete()

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Api.V2010.AuthCallsCredentialListMappingInstance {}>'.format(context)
