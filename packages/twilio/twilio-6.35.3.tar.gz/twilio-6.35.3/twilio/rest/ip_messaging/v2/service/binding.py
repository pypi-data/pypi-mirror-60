# coding=utf-8
r"""
This code was generated by
\ / _    _  _|   _  _
 | (_)\/(_)(_|\/| |(/_  v1.0.0
      /       /
"""

from twilio.base import deserialize
from twilio.base import serialize
from twilio.base import values
from twilio.base.instance_context import InstanceContext
from twilio.base.instance_resource import InstanceResource
from twilio.base.list_resource import ListResource
from twilio.base.page import Page


class BindingList(ListResource):
    """  """

    def __init__(self, version, service_sid):
        """
        Initialize the BindingList

        :param Version version: Version that contains the resource
        :param service_sid: The SID of the Service that the Binding resource is associated with

        :returns: twilio.rest.chat.v2.service.binding.BindingList
        :rtype: twilio.rest.chat.v2.service.binding.BindingList
        """
        super(BindingList, self).__init__(version)

        # Path Solution
        self._solution = {'service_sid': service_sid, }
        self._uri = '/Services/{service_sid}/Bindings'.format(**self._solution)

    def stream(self, binding_type=values.unset, identity=values.unset, limit=None,
               page_size=None):
        """
        Streams BindingInstance records from the API as a generator stream.
        This operation lazily loads records as efficiently as possible until the limit
        is reached.
        The results are returned as a generator, so this operation is memory efficient.

        :param BindingInstance.BindingType binding_type: The push technology used by the Binding resources to read
        :param unicode identity: The `identity` value of the resources to read
        :param int limit: Upper limit for the number of records to return. stream()
                          guarantees to never return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, stream() will attempt to read the
                              limit with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.chat.v2.service.binding.BindingInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(binding_type=binding_type, identity=identity, page_size=limits['page_size'], )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, binding_type=values.unset, identity=values.unset, limit=None,
             page_size=None):
        """
        Lists BindingInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param BindingInstance.BindingType binding_type: The push technology used by the Binding resources to read
        :param unicode identity: The `identity` value of the resources to read
        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.chat.v2.service.binding.BindingInstance]
        """
        return list(self.stream(
            binding_type=binding_type,
            identity=identity,
            limit=limit,
            page_size=page_size,
        ))

    def page(self, binding_type=values.unset, identity=values.unset,
             page_token=values.unset, page_number=values.unset,
             page_size=values.unset):
        """
        Retrieve a single page of BindingInstance records from the API.
        Request is executed immediately

        :param BindingInstance.BindingType binding_type: The push technology used by the Binding resources to read
        :param unicode identity: The `identity` value of the resources to read
        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of BindingInstance
        :rtype: twilio.rest.chat.v2.service.binding.BindingPage
        """
        data = values.of({
            'BindingType': serialize.map(binding_type, lambda e: e),
            'Identity': serialize.map(identity, lambda e: e),
            'PageToken': page_token,
            'Page': page_number,
            'PageSize': page_size,
        })

        response = self._version.page(method='GET', uri=self._uri, params=data, )

        return BindingPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of BindingInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of BindingInstance
        :rtype: twilio.rest.chat.v2.service.binding.BindingPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return BindingPage(self._version, response, self._solution)

    def get(self, sid):
        """
        Constructs a BindingContext

        :param sid: The SID of the resource to fetch

        :returns: twilio.rest.chat.v2.service.binding.BindingContext
        :rtype: twilio.rest.chat.v2.service.binding.BindingContext
        """
        return BindingContext(self._version, service_sid=self._solution['service_sid'], sid=sid, )

    def __call__(self, sid):
        """
        Constructs a BindingContext

        :param sid: The SID of the resource to fetch

        :returns: twilio.rest.chat.v2.service.binding.BindingContext
        :rtype: twilio.rest.chat.v2.service.binding.BindingContext
        """
        return BindingContext(self._version, service_sid=self._solution['service_sid'], sid=sid, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.IpMessaging.V2.BindingList>'


class BindingPage(Page):
    """  """

    def __init__(self, version, response, solution):
        """
        Initialize the BindingPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API
        :param service_sid: The SID of the Service that the Binding resource is associated with

        :returns: twilio.rest.chat.v2.service.binding.BindingPage
        :rtype: twilio.rest.chat.v2.service.binding.BindingPage
        """
        super(BindingPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of BindingInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.chat.v2.service.binding.BindingInstance
        :rtype: twilio.rest.chat.v2.service.binding.BindingInstance
        """
        return BindingInstance(self._version, payload, service_sid=self._solution['service_sid'], )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.IpMessaging.V2.BindingPage>'


class BindingContext(InstanceContext):
    """  """

    def __init__(self, version, service_sid, sid):
        """
        Initialize the BindingContext

        :param Version version: Version that contains the resource
        :param service_sid: The SID of the Service to fetch the resource from
        :param sid: The SID of the resource to fetch

        :returns: twilio.rest.chat.v2.service.binding.BindingContext
        :rtype: twilio.rest.chat.v2.service.binding.BindingContext
        """
        super(BindingContext, self).__init__(version)

        # Path Solution
        self._solution = {'service_sid': service_sid, 'sid': sid, }
        self._uri = '/Services/{service_sid}/Bindings/{sid}'.format(**self._solution)

    def fetch(self):
        """
        Fetch the BindingInstance

        :returns: The fetched BindingInstance
        :rtype: twilio.rest.chat.v2.service.binding.BindingInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return BindingInstance(
            self._version,
            payload,
            service_sid=self._solution['service_sid'],
            sid=self._solution['sid'],
        )

    def delete(self):
        """
        Deletes the BindingInstance

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
        return '<Twilio.IpMessaging.V2.BindingContext {}>'.format(context)


class BindingInstance(InstanceResource):
    """  """

    class BindingType(object):
        GCM = "gcm"
        APN = "apn"
        FCM = "fcm"

    def __init__(self, version, payload, service_sid, sid=None):
        """
        Initialize the BindingInstance

        :returns: twilio.rest.chat.v2.service.binding.BindingInstance
        :rtype: twilio.rest.chat.v2.service.binding.BindingInstance
        """
        super(BindingInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'sid': payload.get('sid'),
            'account_sid': payload.get('account_sid'),
            'service_sid': payload.get('service_sid'),
            'date_created': deserialize.iso8601_datetime(payload.get('date_created')),
            'date_updated': deserialize.iso8601_datetime(payload.get('date_updated')),
            'endpoint': payload.get('endpoint'),
            'identity': payload.get('identity'),
            'credential_sid': payload.get('credential_sid'),
            'binding_type': payload.get('binding_type'),
            'message_types': payload.get('message_types'),
            'url': payload.get('url'),
            'links': payload.get('links'),
        }

        # Context
        self._context = None
        self._solution = {'service_sid': service_sid, 'sid': sid or self._properties['sid'], }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: BindingContext for this BindingInstance
        :rtype: twilio.rest.chat.v2.service.binding.BindingContext
        """
        if self._context is None:
            self._context = BindingContext(
                self._version,
                service_sid=self._solution['service_sid'],
                sid=self._solution['sid'],
            )
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
    def service_sid(self):
        """
        :returns: The SID of the Service that the Binding resource is associated with
        :rtype: unicode
        """
        return self._properties['service_sid']

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
    def endpoint(self):
        """
        :returns: The unique endpoint identifier for the Binding
        :rtype: unicode
        """
        return self._properties['endpoint']

    @property
    def identity(self):
        """
        :returns: The string that identifies the resource's User
        :rtype: unicode
        """
        return self._properties['identity']

    @property
    def credential_sid(self):
        """
        :returns: The SID of the Credential for the binding
        :rtype: unicode
        """
        return self._properties['credential_sid']

    @property
    def binding_type(self):
        """
        :returns: The push technology to use for the binding
        :rtype: BindingInstance.BindingType
        """
        return self._properties['binding_type']

    @property
    def message_types(self):
        """
        :returns: The Programmable Chat message types the binding is subscribed to
        :rtype: unicode
        """
        return self._properties['message_types']

    @property
    def url(self):
        """
        :returns: The absolute URL of the Binding resource
        :rtype: unicode
        """
        return self._properties['url']

    @property
    def links(self):
        """
        :returns: The absolute URLs of the Binding's User
        :rtype: unicode
        """
        return self._properties['links']

    def fetch(self):
        """
        Fetch the BindingInstance

        :returns: The fetched BindingInstance
        :rtype: twilio.rest.chat.v2.service.binding.BindingInstance
        """
        return self._proxy.fetch()

    def delete(self):
        """
        Deletes the BindingInstance

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
        return '<Twilio.IpMessaging.V2.BindingInstance {}>'.format(context)
