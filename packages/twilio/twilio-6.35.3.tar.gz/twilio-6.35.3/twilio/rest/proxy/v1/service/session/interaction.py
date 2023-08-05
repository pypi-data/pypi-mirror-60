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


class InteractionList(ListResource):
    """ PLEASE NOTE that this class contains beta products that are subject to
    change. Use them with caution. """

    def __init__(self, version, service_sid, session_sid):
        """
        Initialize the InteractionList

        :param Version version: Version that contains the resource
        :param service_sid: The SID of the resource's parent Service
        :param session_sid: The SID of the resource's parent Session

        :returns: twilio.rest.proxy.v1.service.session.interaction.InteractionList
        :rtype: twilio.rest.proxy.v1.service.session.interaction.InteractionList
        """
        super(InteractionList, self).__init__(version)

        # Path Solution
        self._solution = {'service_sid': service_sid, 'session_sid': session_sid, }
        self._uri = '/Services/{service_sid}/Sessions/{session_sid}/Interactions'.format(**self._solution)

    def stream(self, limit=None, page_size=None):
        """
        Streams InteractionInstance records from the API as a generator stream.
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
        :rtype: list[twilio.rest.proxy.v1.service.session.interaction.InteractionInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(page_size=limits['page_size'], )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, limit=None, page_size=None):
        """
        Lists InteractionInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.proxy.v1.service.session.interaction.InteractionInstance]
        """
        return list(self.stream(limit=limit, page_size=page_size, ))

    def page(self, page_token=values.unset, page_number=values.unset,
             page_size=values.unset):
        """
        Retrieve a single page of InteractionInstance records from the API.
        Request is executed immediately

        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of InteractionInstance
        :rtype: twilio.rest.proxy.v1.service.session.interaction.InteractionPage
        """
        data = values.of({'PageToken': page_token, 'Page': page_number, 'PageSize': page_size, })

        response = self._version.page(method='GET', uri=self._uri, params=data, )

        return InteractionPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of InteractionInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of InteractionInstance
        :rtype: twilio.rest.proxy.v1.service.session.interaction.InteractionPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return InteractionPage(self._version, response, self._solution)

    def get(self, sid):
        """
        Constructs a InteractionContext

        :param sid: The unique string that identifies the resource

        :returns: twilio.rest.proxy.v1.service.session.interaction.InteractionContext
        :rtype: twilio.rest.proxy.v1.service.session.interaction.InteractionContext
        """
        return InteractionContext(
            self._version,
            service_sid=self._solution['service_sid'],
            session_sid=self._solution['session_sid'],
            sid=sid,
        )

    def __call__(self, sid):
        """
        Constructs a InteractionContext

        :param sid: The unique string that identifies the resource

        :returns: twilio.rest.proxy.v1.service.session.interaction.InteractionContext
        :rtype: twilio.rest.proxy.v1.service.session.interaction.InteractionContext
        """
        return InteractionContext(
            self._version,
            service_sid=self._solution['service_sid'],
            session_sid=self._solution['session_sid'],
            sid=sid,
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Proxy.V1.InteractionList>'


class InteractionPage(Page):
    """ PLEASE NOTE that this class contains beta products that are subject to
    change. Use them with caution. """

    def __init__(self, version, response, solution):
        """
        Initialize the InteractionPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API
        :param service_sid: The SID of the resource's parent Service
        :param session_sid: The SID of the resource's parent Session

        :returns: twilio.rest.proxy.v1.service.session.interaction.InteractionPage
        :rtype: twilio.rest.proxy.v1.service.session.interaction.InteractionPage
        """
        super(InteractionPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of InteractionInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.proxy.v1.service.session.interaction.InteractionInstance
        :rtype: twilio.rest.proxy.v1.service.session.interaction.InteractionInstance
        """
        return InteractionInstance(
            self._version,
            payload,
            service_sid=self._solution['service_sid'],
            session_sid=self._solution['session_sid'],
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Proxy.V1.InteractionPage>'


class InteractionContext(InstanceContext):
    """ PLEASE NOTE that this class contains beta products that are subject to
    change. Use them with caution. """

    def __init__(self, version, service_sid, session_sid, sid):
        """
        Initialize the InteractionContext

        :param Version version: Version that contains the resource
        :param service_sid: The SID of the parent Service of the resource to fetch
        :param session_sid: he SID of the parent Session of the resource to fetch
        :param sid: The unique string that identifies the resource

        :returns: twilio.rest.proxy.v1.service.session.interaction.InteractionContext
        :rtype: twilio.rest.proxy.v1.service.session.interaction.InteractionContext
        """
        super(InteractionContext, self).__init__(version)

        # Path Solution
        self._solution = {'service_sid': service_sid, 'session_sid': session_sid, 'sid': sid, }
        self._uri = '/Services/{service_sid}/Sessions/{session_sid}/Interactions/{sid}'.format(**self._solution)

    def fetch(self):
        """
        Fetch the InteractionInstance

        :returns: The fetched InteractionInstance
        :rtype: twilio.rest.proxy.v1.service.session.interaction.InteractionInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return InteractionInstance(
            self._version,
            payload,
            service_sid=self._solution['service_sid'],
            session_sid=self._solution['session_sid'],
            sid=self._solution['sid'],
        )

    def delete(self):
        """
        Deletes the InteractionInstance

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
        return '<Twilio.Proxy.V1.InteractionContext {}>'.format(context)


class InteractionInstance(InstanceResource):
    """ PLEASE NOTE that this class contains beta products that are subject to
    change. Use them with caution. """

    class Type(object):
        MESSAGE = "message"
        VOICE = "voice"
        UNKNOWN = "unknown"

    class ResourceStatus(object):
        ACCEPTED = "accepted"
        ANSWERED = "answered"
        BUSY = "busy"
        CANCELED = "canceled"
        COMPLETED = "completed"
        DELETED = "deleted"
        DELIVERED = "delivered"
        DELIVERY_UNKNOWN = "delivery-unknown"
        FAILED = "failed"
        IN_PROGRESS = "in-progress"
        INITIATED = "initiated"
        NO_ANSWER = "no-answer"
        QUEUED = "queued"
        RECEIVED = "received"
        RECEIVING = "receiving"
        RINGING = "ringing"
        SCHEDULED = "scheduled"
        SENDING = "sending"
        SENT = "sent"
        UNDELIVERED = "undelivered"
        UNKNOWN = "unknown"

    def __init__(self, version, payload, service_sid, session_sid, sid=None):
        """
        Initialize the InteractionInstance

        :returns: twilio.rest.proxy.v1.service.session.interaction.InteractionInstance
        :rtype: twilio.rest.proxy.v1.service.session.interaction.InteractionInstance
        """
        super(InteractionInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'sid': payload.get('sid'),
            'session_sid': payload.get('session_sid'),
            'service_sid': payload.get('service_sid'),
            'account_sid': payload.get('account_sid'),
            'data': payload.get('data'),
            'type': payload.get('type'),
            'inbound_participant_sid': payload.get('inbound_participant_sid'),
            'inbound_resource_sid': payload.get('inbound_resource_sid'),
            'inbound_resource_status': payload.get('inbound_resource_status'),
            'inbound_resource_type': payload.get('inbound_resource_type'),
            'inbound_resource_url': payload.get('inbound_resource_url'),
            'outbound_participant_sid': payload.get('outbound_participant_sid'),
            'outbound_resource_sid': payload.get('outbound_resource_sid'),
            'outbound_resource_status': payload.get('outbound_resource_status'),
            'outbound_resource_type': payload.get('outbound_resource_type'),
            'outbound_resource_url': payload.get('outbound_resource_url'),
            'date_created': deserialize.iso8601_datetime(payload.get('date_created')),
            'date_updated': deserialize.iso8601_datetime(payload.get('date_updated')),
            'url': payload.get('url'),
        }

        # Context
        self._context = None
        self._solution = {
            'service_sid': service_sid,
            'session_sid': session_sid,
            'sid': sid or self._properties['sid'],
        }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: InteractionContext for this InteractionInstance
        :rtype: twilio.rest.proxy.v1.service.session.interaction.InteractionContext
        """
        if self._context is None:
            self._context = InteractionContext(
                self._version,
                service_sid=self._solution['service_sid'],
                session_sid=self._solution['session_sid'],
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
    def session_sid(self):
        """
        :returns: The SID of the resource's parent Session
        :rtype: unicode
        """
        return self._properties['session_sid']

    @property
    def service_sid(self):
        """
        :returns: The SID of the resource's parent Service
        :rtype: unicode
        """
        return self._properties['service_sid']

    @property
    def account_sid(self):
        """
        :returns: The SID of the Account that created the resource
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def data(self):
        """
        :returns: A JSON string that includes the message body of message interactions
        :rtype: unicode
        """
        return self._properties['data']

    @property
    def type(self):
        """
        :returns: The Type of the Interaction
        :rtype: InteractionInstance.Type
        """
        return self._properties['type']

    @property
    def inbound_participant_sid(self):
        """
        :returns: The SID of the inbound Participant resource
        :rtype: unicode
        """
        return self._properties['inbound_participant_sid']

    @property
    def inbound_resource_sid(self):
        """
        :returns: The SID of the inbound resource
        :rtype: unicode
        """
        return self._properties['inbound_resource_sid']

    @property
    def inbound_resource_status(self):
        """
        :returns: The inbound resource status of the Interaction
        :rtype: InteractionInstance.ResourceStatus
        """
        return self._properties['inbound_resource_status']

    @property
    def inbound_resource_type(self):
        """
        :returns: The inbound resource type
        :rtype: unicode
        """
        return self._properties['inbound_resource_type']

    @property
    def inbound_resource_url(self):
        """
        :returns: The URL of the Twilio inbound resource
        :rtype: unicode
        """
        return self._properties['inbound_resource_url']

    @property
    def outbound_participant_sid(self):
        """
        :returns: The SID of the outbound Participant
        :rtype: unicode
        """
        return self._properties['outbound_participant_sid']

    @property
    def outbound_resource_sid(self):
        """
        :returns: The SID of the outbound resource
        :rtype: unicode
        """
        return self._properties['outbound_resource_sid']

    @property
    def outbound_resource_status(self):
        """
        :returns: The outbound resource status of the Interaction
        :rtype: InteractionInstance.ResourceStatus
        """
        return self._properties['outbound_resource_status']

    @property
    def outbound_resource_type(self):
        """
        :returns: The outbound resource type
        :rtype: unicode
        """
        return self._properties['outbound_resource_type']

    @property
    def outbound_resource_url(self):
        """
        :returns: The URL of the Twilio outbound resource
        :rtype: unicode
        """
        return self._properties['outbound_resource_url']

    @property
    def date_created(self):
        """
        :returns: The ISO 8601 date and time in GMT when the Interaction was created
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
        :returns: The absolute URL of the Interaction resource
        :rtype: unicode
        """
        return self._properties['url']

    def fetch(self):
        """
        Fetch the InteractionInstance

        :returns: The fetched InteractionInstance
        :rtype: twilio.rest.proxy.v1.service.session.interaction.InteractionInstance
        """
        return self._proxy.fetch()

    def delete(self):
        """
        Deletes the InteractionInstance

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
        return '<Twilio.Proxy.V1.InteractionInstance {}>'.format(context)
