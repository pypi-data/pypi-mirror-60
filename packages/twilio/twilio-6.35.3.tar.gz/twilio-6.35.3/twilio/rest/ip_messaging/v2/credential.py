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


class CredentialList(ListResource):
    """  """

    def __init__(self, version):
        """
        Initialize the CredentialList

        :param Version version: Version that contains the resource

        :returns: twilio.rest.chat.v2.credential.CredentialList
        :rtype: twilio.rest.chat.v2.credential.CredentialList
        """
        super(CredentialList, self).__init__(version)

        # Path Solution
        self._solution = {}
        self._uri = '/Credentials'.format(**self._solution)

    def stream(self, limit=None, page_size=None):
        """
        Streams CredentialInstance records from the API as a generator stream.
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
        :rtype: list[twilio.rest.chat.v2.credential.CredentialInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(page_size=limits['page_size'], )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, limit=None, page_size=None):
        """
        Lists CredentialInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.chat.v2.credential.CredentialInstance]
        """
        return list(self.stream(limit=limit, page_size=page_size, ))

    def page(self, page_token=values.unset, page_number=values.unset,
             page_size=values.unset):
        """
        Retrieve a single page of CredentialInstance records from the API.
        Request is executed immediately

        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of CredentialInstance
        :rtype: twilio.rest.chat.v2.credential.CredentialPage
        """
        data = values.of({'PageToken': page_token, 'Page': page_number, 'PageSize': page_size, })

        response = self._version.page(method='GET', uri=self._uri, params=data, )

        return CredentialPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of CredentialInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of CredentialInstance
        :rtype: twilio.rest.chat.v2.credential.CredentialPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return CredentialPage(self._version, response, self._solution)

    def create(self, type, friendly_name=values.unset, certificate=values.unset,
               private_key=values.unset, sandbox=values.unset, api_key=values.unset,
               secret=values.unset):
        """
        Create the CredentialInstance

        :param CredentialInstance.PushService type: The type of push-notification service the credential is for
        :param unicode friendly_name: A string to describe the resource
        :param unicode certificate: [APN only] The URL encoded representation of the certificate
        :param unicode private_key: [APN only] The URL encoded representation of the private key
        :param bool sandbox: [APN only] Whether to send the credential to sandbox APNs
        :param unicode api_key: [GCM only] The API key for the project that was obtained from the Google Developer console for your GCM Service application credential
        :param unicode secret: [FCM only] The Server key of your project from Firebase console

        :returns: The created CredentialInstance
        :rtype: twilio.rest.chat.v2.credential.CredentialInstance
        """
        data = values.of({
            'Type': type,
            'FriendlyName': friendly_name,
            'Certificate': certificate,
            'PrivateKey': private_key,
            'Sandbox': sandbox,
            'ApiKey': api_key,
            'Secret': secret,
        })

        payload = self._version.create(method='POST', uri=self._uri, data=data, )

        return CredentialInstance(self._version, payload, )

    def get(self, sid):
        """
        Constructs a CredentialContext

        :param sid: The SID of the Credential resource to fetch

        :returns: twilio.rest.chat.v2.credential.CredentialContext
        :rtype: twilio.rest.chat.v2.credential.CredentialContext
        """
        return CredentialContext(self._version, sid=sid, )

    def __call__(self, sid):
        """
        Constructs a CredentialContext

        :param sid: The SID of the Credential resource to fetch

        :returns: twilio.rest.chat.v2.credential.CredentialContext
        :rtype: twilio.rest.chat.v2.credential.CredentialContext
        """
        return CredentialContext(self._version, sid=sid, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.IpMessaging.V2.CredentialList>'


class CredentialPage(Page):
    """  """

    def __init__(self, version, response, solution):
        """
        Initialize the CredentialPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API

        :returns: twilio.rest.chat.v2.credential.CredentialPage
        :rtype: twilio.rest.chat.v2.credential.CredentialPage
        """
        super(CredentialPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of CredentialInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.chat.v2.credential.CredentialInstance
        :rtype: twilio.rest.chat.v2.credential.CredentialInstance
        """
        return CredentialInstance(self._version, payload, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.IpMessaging.V2.CredentialPage>'


class CredentialContext(InstanceContext):
    """  """

    def __init__(self, version, sid):
        """
        Initialize the CredentialContext

        :param Version version: Version that contains the resource
        :param sid: The SID of the Credential resource to fetch

        :returns: twilio.rest.chat.v2.credential.CredentialContext
        :rtype: twilio.rest.chat.v2.credential.CredentialContext
        """
        super(CredentialContext, self).__init__(version)

        # Path Solution
        self._solution = {'sid': sid, }
        self._uri = '/Credentials/{sid}'.format(**self._solution)

    def fetch(self):
        """
        Fetch the CredentialInstance

        :returns: The fetched CredentialInstance
        :rtype: twilio.rest.chat.v2.credential.CredentialInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return CredentialInstance(self._version, payload, sid=self._solution['sid'], )

    def update(self, friendly_name=values.unset, certificate=values.unset,
               private_key=values.unset, sandbox=values.unset, api_key=values.unset,
               secret=values.unset):
        """
        Update the CredentialInstance

        :param unicode friendly_name: A string to describe the resource
        :param unicode certificate: [APN only] The URL encoded representation of the certificate
        :param unicode private_key: [APN only] The URL encoded representation of the private key
        :param bool sandbox: [APN only] Whether to send the credential to sandbox APNs
        :param unicode api_key: [GCM only] The API key for the project that was obtained from the Google Developer console for your GCM Service application credential
        :param unicode secret: [FCM only] The Server key of your project from Firebase console

        :returns: The updated CredentialInstance
        :rtype: twilio.rest.chat.v2.credential.CredentialInstance
        """
        data = values.of({
            'FriendlyName': friendly_name,
            'Certificate': certificate,
            'PrivateKey': private_key,
            'Sandbox': sandbox,
            'ApiKey': api_key,
            'Secret': secret,
        })

        payload = self._version.update(method='POST', uri=self._uri, data=data, )

        return CredentialInstance(self._version, payload, sid=self._solution['sid'], )

    def delete(self):
        """
        Deletes the CredentialInstance

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
        return '<Twilio.IpMessaging.V2.CredentialContext {}>'.format(context)


class CredentialInstance(InstanceResource):
    """  """

    class PushService(object):
        GCM = "gcm"
        APN = "apn"
        FCM = "fcm"

    def __init__(self, version, payload, sid=None):
        """
        Initialize the CredentialInstance

        :returns: twilio.rest.chat.v2.credential.CredentialInstance
        :rtype: twilio.rest.chat.v2.credential.CredentialInstance
        """
        super(CredentialInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'sid': payload.get('sid'),
            'account_sid': payload.get('account_sid'),
            'friendly_name': payload.get('friendly_name'),
            'type': payload.get('type'),
            'sandbox': payload.get('sandbox'),
            'date_created': deserialize.iso8601_datetime(payload.get('date_created')),
            'date_updated': deserialize.iso8601_datetime(payload.get('date_updated')),
            'url': payload.get('url'),
        }

        # Context
        self._context = None
        self._solution = {'sid': sid or self._properties['sid'], }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: CredentialContext for this CredentialInstance
        :rtype: twilio.rest.chat.v2.credential.CredentialContext
        """
        if self._context is None:
            self._context = CredentialContext(self._version, sid=self._solution['sid'], )
        return self._context

    @property
    def sid(self):
        """
        :returns: The unique string that identifies the resource
        :rtype: unicode
        """
        return self._properties['sid']

    @property
    def account_sid(self):
        """
        :returns: The SID of the Account that created the resource
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def friendly_name(self):
        """
        :returns: The string that you assigned to describe the resource
        :rtype: unicode
        """
        return self._properties['friendly_name']

    @property
    def type(self):
        """
        :returns: The type of push-notification service the credential is for
        :rtype: CredentialInstance.PushService
        """
        return self._properties['type']

    @property
    def sandbox(self):
        """
        :returns: [APN only] Whether to send the credential to sandbox APNs
        :rtype: unicode
        """
        return self._properties['sandbox']

    @property
    def date_created(self):
        """
        :returns: The ISO 8601 date and time in GMT when the resource was created
        :rtype: datetime
        """
        return self._properties['date_created']

    @property
    def date_updated(self):
        """
        :returns: The ISO 8601 date and time in GMT when the resource was last updated
        :rtype: datetime
        """
        return self._properties['date_updated']

    @property
    def url(self):
        """
        :returns: The absolute URL of the Credential resource
        :rtype: unicode
        """
        return self._properties['url']

    def fetch(self):
        """
        Fetch the CredentialInstance

        :returns: The fetched CredentialInstance
        :rtype: twilio.rest.chat.v2.credential.CredentialInstance
        """
        return self._proxy.fetch()

    def update(self, friendly_name=values.unset, certificate=values.unset,
               private_key=values.unset, sandbox=values.unset, api_key=values.unset,
               secret=values.unset):
        """
        Update the CredentialInstance

        :param unicode friendly_name: A string to describe the resource
        :param unicode certificate: [APN only] The URL encoded representation of the certificate
        :param unicode private_key: [APN only] The URL encoded representation of the private key
        :param bool sandbox: [APN only] Whether to send the credential to sandbox APNs
        :param unicode api_key: [GCM only] The API key for the project that was obtained from the Google Developer console for your GCM Service application credential
        :param unicode secret: [FCM only] The Server key of your project from Firebase console

        :returns: The updated CredentialInstance
        :rtype: twilio.rest.chat.v2.credential.CredentialInstance
        """
        return self._proxy.update(
            friendly_name=friendly_name,
            certificate=certificate,
            private_key=private_key,
            sandbox=sandbox,
            api_key=api_key,
            secret=secret,
        )

    def delete(self):
        """
        Deletes the CredentialInstance

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
        return '<Twilio.IpMessaging.V2.CredentialInstance {}>'.format(context)
