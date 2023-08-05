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


class MemberList(ListResource):
    """  """

    def __init__(self, version, account_sid, queue_sid):
        """
        Initialize the MemberList

        :param Version version: Version that contains the resource
        :param account_sid: The SID of the Account that created this resource
        :param queue_sid: The SID of the Queue the member is in

        :returns: twilio.rest.api.v2010.account.queue.member.MemberList
        :rtype: twilio.rest.api.v2010.account.queue.member.MemberList
        """
        super(MemberList, self).__init__(version)

        # Path Solution
        self._solution = {'account_sid': account_sid, 'queue_sid': queue_sid, }
        self._uri = '/Accounts/{account_sid}/Queues/{queue_sid}/Members.json'.format(**self._solution)

    def stream(self, limit=None, page_size=None):
        """
        Streams MemberInstance records from the API as a generator stream.
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
        :rtype: list[twilio.rest.api.v2010.account.queue.member.MemberInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(page_size=limits['page_size'], )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, limit=None, page_size=None):
        """
        Lists MemberInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.api.v2010.account.queue.member.MemberInstance]
        """
        return list(self.stream(limit=limit, page_size=page_size, ))

    def page(self, page_token=values.unset, page_number=values.unset,
             page_size=values.unset):
        """
        Retrieve a single page of MemberInstance records from the API.
        Request is executed immediately

        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of MemberInstance
        :rtype: twilio.rest.api.v2010.account.queue.member.MemberPage
        """
        data = values.of({'PageToken': page_token, 'Page': page_number, 'PageSize': page_size, })

        response = self._version.page(method='GET', uri=self._uri, params=data, )

        return MemberPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of MemberInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of MemberInstance
        :rtype: twilio.rest.api.v2010.account.queue.member.MemberPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return MemberPage(self._version, response, self._solution)

    def get(self, call_sid):
        """
        Constructs a MemberContext

        :param call_sid: The Call SID of the resource(s) to fetch

        :returns: twilio.rest.api.v2010.account.queue.member.MemberContext
        :rtype: twilio.rest.api.v2010.account.queue.member.MemberContext
        """
        return MemberContext(
            self._version,
            account_sid=self._solution['account_sid'],
            queue_sid=self._solution['queue_sid'],
            call_sid=call_sid,
        )

    def __call__(self, call_sid):
        """
        Constructs a MemberContext

        :param call_sid: The Call SID of the resource(s) to fetch

        :returns: twilio.rest.api.v2010.account.queue.member.MemberContext
        :rtype: twilio.rest.api.v2010.account.queue.member.MemberContext
        """
        return MemberContext(
            self._version,
            account_sid=self._solution['account_sid'],
            queue_sid=self._solution['queue_sid'],
            call_sid=call_sid,
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Api.V2010.MemberList>'


class MemberPage(Page):
    """  """

    def __init__(self, version, response, solution):
        """
        Initialize the MemberPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API
        :param account_sid: The SID of the Account that created this resource
        :param queue_sid: The SID of the Queue the member is in

        :returns: twilio.rest.api.v2010.account.queue.member.MemberPage
        :rtype: twilio.rest.api.v2010.account.queue.member.MemberPage
        """
        super(MemberPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of MemberInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.api.v2010.account.queue.member.MemberInstance
        :rtype: twilio.rest.api.v2010.account.queue.member.MemberInstance
        """
        return MemberInstance(
            self._version,
            payload,
            account_sid=self._solution['account_sid'],
            queue_sid=self._solution['queue_sid'],
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Api.V2010.MemberPage>'


class MemberContext(InstanceContext):
    """  """

    def __init__(self, version, account_sid, queue_sid, call_sid):
        """
        Initialize the MemberContext

        :param Version version: Version that contains the resource
        :param account_sid: The SID of the Account that created the resource(s) to fetch
        :param queue_sid: The SID of the Queue in which to find the members
        :param call_sid: The Call SID of the resource(s) to fetch

        :returns: twilio.rest.api.v2010.account.queue.member.MemberContext
        :rtype: twilio.rest.api.v2010.account.queue.member.MemberContext
        """
        super(MemberContext, self).__init__(version)

        # Path Solution
        self._solution = {'account_sid': account_sid, 'queue_sid': queue_sid, 'call_sid': call_sid, }
        self._uri = '/Accounts/{account_sid}/Queues/{queue_sid}/Members/{call_sid}.json'.format(**self._solution)

    def fetch(self):
        """
        Fetch the MemberInstance

        :returns: The fetched MemberInstance
        :rtype: twilio.rest.api.v2010.account.queue.member.MemberInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return MemberInstance(
            self._version,
            payload,
            account_sid=self._solution['account_sid'],
            queue_sid=self._solution['queue_sid'],
            call_sid=self._solution['call_sid'],
        )

    def update(self, url, method=values.unset):
        """
        Update the MemberInstance

        :param unicode url: The absolute URL of the Queue resource
        :param unicode method: How to pass the update request data

        :returns: The updated MemberInstance
        :rtype: twilio.rest.api.v2010.account.queue.member.MemberInstance
        """
        data = values.of({'Url': url, 'Method': method, })

        payload = self._version.update(method='POST', uri=self._uri, data=data, )

        return MemberInstance(
            self._version,
            payload,
            account_sid=self._solution['account_sid'],
            queue_sid=self._solution['queue_sid'],
            call_sid=self._solution['call_sid'],
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Api.V2010.MemberContext {}>'.format(context)


class MemberInstance(InstanceResource):
    """  """

    def __init__(self, version, payload, account_sid, queue_sid, call_sid=None):
        """
        Initialize the MemberInstance

        :returns: twilio.rest.api.v2010.account.queue.member.MemberInstance
        :rtype: twilio.rest.api.v2010.account.queue.member.MemberInstance
        """
        super(MemberInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'call_sid': payload.get('call_sid'),
            'date_enqueued': deserialize.rfc2822_datetime(payload.get('date_enqueued')),
            'position': deserialize.integer(payload.get('position')),
            'uri': payload.get('uri'),
            'wait_time': deserialize.integer(payload.get('wait_time')),
            'queue_sid': payload.get('queue_sid'),
        }

        # Context
        self._context = None
        self._solution = {
            'account_sid': account_sid,
            'queue_sid': queue_sid,
            'call_sid': call_sid or self._properties['call_sid'],
        }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: MemberContext for this MemberInstance
        :rtype: twilio.rest.api.v2010.account.queue.member.MemberContext
        """
        if self._context is None:
            self._context = MemberContext(
                self._version,
                account_sid=self._solution['account_sid'],
                queue_sid=self._solution['queue_sid'],
                call_sid=self._solution['call_sid'],
            )
        return self._context

    @property
    def call_sid(self):
        """
        :returns: The SID of the Call the resource is associated with
        :rtype: unicode
        """
        return self._properties['call_sid']

    @property
    def date_enqueued(self):
        """
        :returns: The date the member was enqueued
        :rtype: datetime
        """
        return self._properties['date_enqueued']

    @property
    def position(self):
        """
        :returns: This member's current position in the queue.
        :rtype: unicode
        """
        return self._properties['position']

    @property
    def uri(self):
        """
        :returns: The URI of the resource, relative to `https://api.twilio.com`
        :rtype: unicode
        """
        return self._properties['uri']

    @property
    def wait_time(self):
        """
        :returns: The number of seconds the member has been in the queue.
        :rtype: unicode
        """
        return self._properties['wait_time']

    @property
    def queue_sid(self):
        """
        :returns: The SID of the Queue the member is in
        :rtype: unicode
        """
        return self._properties['queue_sid']

    def fetch(self):
        """
        Fetch the MemberInstance

        :returns: The fetched MemberInstance
        :rtype: twilio.rest.api.v2010.account.queue.member.MemberInstance
        """
        return self._proxy.fetch()

    def update(self, url, method=values.unset):
        """
        Update the MemberInstance

        :param unicode url: The absolute URL of the Queue resource
        :param unicode method: How to pass the update request data

        :returns: The updated MemberInstance
        :rtype: twilio.rest.api.v2010.account.queue.member.MemberInstance
        """
        return self._proxy.update(url, method=method, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Api.V2010.MemberInstance {}>'.format(context)
