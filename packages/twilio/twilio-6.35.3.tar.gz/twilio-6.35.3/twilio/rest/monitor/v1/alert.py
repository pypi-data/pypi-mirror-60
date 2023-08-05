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


class AlertList(ListResource):
    """  """

    def __init__(self, version):
        """
        Initialize the AlertList

        :param Version version: Version that contains the resource

        :returns: twilio.rest.monitor.v1.alert.AlertList
        :rtype: twilio.rest.monitor.v1.alert.AlertList
        """
        super(AlertList, self).__init__(version)

        # Path Solution
        self._solution = {}
        self._uri = '/Alerts'.format(**self._solution)

    def stream(self, log_level=values.unset, start_date=values.unset,
               end_date=values.unset, limit=None, page_size=None):
        """
        Streams AlertInstance records from the API as a generator stream.
        This operation lazily loads records as efficiently as possible until the limit
        is reached.
        The results are returned as a generator, so this operation is memory efficient.

        :param unicode log_level: Only show alerts for this log-level
        :param date start_date: Only include alerts that occurred on or after this date
        :param date end_date: Only include alerts that occurred on or before this date
        :param int limit: Upper limit for the number of records to return. stream()
                          guarantees to never return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, stream() will attempt to read the
                              limit with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.monitor.v1.alert.AlertInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(
            log_level=log_level,
            start_date=start_date,
            end_date=end_date,
            page_size=limits['page_size'],
        )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, log_level=values.unset, start_date=values.unset,
             end_date=values.unset, limit=None, page_size=None):
        """
        Lists AlertInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param unicode log_level: Only show alerts for this log-level
        :param date start_date: Only include alerts that occurred on or after this date
        :param date end_date: Only include alerts that occurred on or before this date
        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.monitor.v1.alert.AlertInstance]
        """
        return list(self.stream(
            log_level=log_level,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            page_size=page_size,
        ))

    def page(self, log_level=values.unset, start_date=values.unset,
             end_date=values.unset, page_token=values.unset,
             page_number=values.unset, page_size=values.unset):
        """
        Retrieve a single page of AlertInstance records from the API.
        Request is executed immediately

        :param unicode log_level: Only show alerts for this log-level
        :param date start_date: Only include alerts that occurred on or after this date
        :param date end_date: Only include alerts that occurred on or before this date
        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of AlertInstance
        :rtype: twilio.rest.monitor.v1.alert.AlertPage
        """
        data = values.of({
            'LogLevel': log_level,
            'StartDate': serialize.iso8601_date(start_date),
            'EndDate': serialize.iso8601_date(end_date),
            'PageToken': page_token,
            'Page': page_number,
            'PageSize': page_size,
        })

        response = self._version.page(method='GET', uri=self._uri, params=data, )

        return AlertPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of AlertInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of AlertInstance
        :rtype: twilio.rest.monitor.v1.alert.AlertPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return AlertPage(self._version, response, self._solution)

    def get(self, sid):
        """
        Constructs a AlertContext

        :param sid: The SID that identifies the resource to fetch

        :returns: twilio.rest.monitor.v1.alert.AlertContext
        :rtype: twilio.rest.monitor.v1.alert.AlertContext
        """
        return AlertContext(self._version, sid=sid, )

    def __call__(self, sid):
        """
        Constructs a AlertContext

        :param sid: The SID that identifies the resource to fetch

        :returns: twilio.rest.monitor.v1.alert.AlertContext
        :rtype: twilio.rest.monitor.v1.alert.AlertContext
        """
        return AlertContext(self._version, sid=sid, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Monitor.V1.AlertList>'


class AlertPage(Page):
    """  """

    def __init__(self, version, response, solution):
        """
        Initialize the AlertPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API

        :returns: twilio.rest.monitor.v1.alert.AlertPage
        :rtype: twilio.rest.monitor.v1.alert.AlertPage
        """
        super(AlertPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of AlertInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.monitor.v1.alert.AlertInstance
        :rtype: twilio.rest.monitor.v1.alert.AlertInstance
        """
        return AlertInstance(self._version, payload, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Monitor.V1.AlertPage>'


class AlertContext(InstanceContext):
    """  """

    def __init__(self, version, sid):
        """
        Initialize the AlertContext

        :param Version version: Version that contains the resource
        :param sid: The SID that identifies the resource to fetch

        :returns: twilio.rest.monitor.v1.alert.AlertContext
        :rtype: twilio.rest.monitor.v1.alert.AlertContext
        """
        super(AlertContext, self).__init__(version)

        # Path Solution
        self._solution = {'sid': sid, }
        self._uri = '/Alerts/{sid}'.format(**self._solution)

    def fetch(self):
        """
        Fetch the AlertInstance

        :returns: The fetched AlertInstance
        :rtype: twilio.rest.monitor.v1.alert.AlertInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return AlertInstance(self._version, payload, sid=self._solution['sid'], )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Monitor.V1.AlertContext {}>'.format(context)


class AlertInstance(InstanceResource):
    """  """

    def __init__(self, version, payload, sid=None):
        """
        Initialize the AlertInstance

        :returns: twilio.rest.monitor.v1.alert.AlertInstance
        :rtype: twilio.rest.monitor.v1.alert.AlertInstance
        """
        super(AlertInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'account_sid': payload.get('account_sid'),
            'alert_text': payload.get('alert_text'),
            'api_version': payload.get('api_version'),
            'date_created': deserialize.iso8601_datetime(payload.get('date_created')),
            'date_generated': deserialize.iso8601_datetime(payload.get('date_generated')),
            'date_updated': deserialize.iso8601_datetime(payload.get('date_updated')),
            'error_code': payload.get('error_code'),
            'log_level': payload.get('log_level'),
            'more_info': payload.get('more_info'),
            'request_method': payload.get('request_method'),
            'request_url': payload.get('request_url'),
            'request_variables': payload.get('request_variables'),
            'resource_sid': payload.get('resource_sid'),
            'response_body': payload.get('response_body'),
            'response_headers': payload.get('response_headers'),
            'sid': payload.get('sid'),
            'url': payload.get('url'),
            'request_headers': payload.get('request_headers'),
            'service_sid': payload.get('service_sid'),
        }

        # Context
        self._context = None
        self._solution = {'sid': sid or self._properties['sid'], }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: AlertContext for this AlertInstance
        :rtype: twilio.rest.monitor.v1.alert.AlertContext
        """
        if self._context is None:
            self._context = AlertContext(self._version, sid=self._solution['sid'], )
        return self._context

    @property
    def account_sid(self):
        """
        :returns: The SID of the Account that created the resource
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def alert_text(self):
        """
        :returns: The text of the alert
        :rtype: unicode
        """
        return self._properties['alert_text']

    @property
    def api_version(self):
        """
        :returns: The API version used when the alert was generated
        :rtype: unicode
        """
        return self._properties['api_version']

    @property
    def date_created(self):
        """
        :returns: The ISO 8601 date and time in GMT when the resource was created
        :rtype: datetime
        """
        return self._properties['date_created']

    @property
    def date_generated(self):
        """
        :returns: The date and time when the alert was generated specified in ISO 8601 format
        :rtype: datetime
        """
        return self._properties['date_generated']

    @property
    def date_updated(self):
        """
        :returns: The ISO 8601 date and time in GMT when the resource was last updated
        :rtype: datetime
        """
        return self._properties['date_updated']

    @property
    def error_code(self):
        """
        :returns: The error code for the condition that generated the alert
        :rtype: unicode
        """
        return self._properties['error_code']

    @property
    def log_level(self):
        """
        :returns: The log level
        :rtype: unicode
        """
        return self._properties['log_level']

    @property
    def more_info(self):
        """
        :returns: The URL of the page in our Error Dictionary with more information about the error condition
        :rtype: unicode
        """
        return self._properties['more_info']

    @property
    def request_method(self):
        """
        :returns: The method used by the request that generated the alert
        :rtype: unicode
        """
        return self._properties['request_method']

    @property
    def request_url(self):
        """
        :returns: The URL of the request that generated the alert
        :rtype: unicode
        """
        return self._properties['request_url']

    @property
    def request_variables(self):
        """
        :returns: The variables passed in the request that generated the alert
        :rtype: unicode
        """
        return self._properties['request_variables']

    @property
    def resource_sid(self):
        """
        :returns: The SID of the resource for which the alert was generated
        :rtype: unicode
        """
        return self._properties['resource_sid']

    @property
    def response_body(self):
        """
        :returns: The response body of the request that generated the alert
        :rtype: unicode
        """
        return self._properties['response_body']

    @property
    def response_headers(self):
        """
        :returns: The response headers of the request that generated the alert
        :rtype: unicode
        """
        return self._properties['response_headers']

    @property
    def sid(self):
        """
        :returns: The unique string that identifies the resource
        :rtype: unicode
        """
        return self._properties['sid']

    @property
    def url(self):
        """
        :returns: The absolute URL of the Alert resource
        :rtype: unicode
        """
        return self._properties['url']

    @property
    def request_headers(self):
        """
        :returns: The request headers of the request that generated the alert
        :rtype: unicode
        """
        return self._properties['request_headers']

    @property
    def service_sid(self):
        """
        :returns: The SID of the service or resource that generated the alert
        :rtype: unicode
        """
        return self._properties['service_sid']

    def fetch(self):
        """
        Fetch the AlertInstance

        :returns: The fetched AlertInstance
        :rtype: twilio.rest.monitor.v1.alert.AlertInstance
        """
        return self._proxy.fetch()

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Monitor.V1.AlertInstance {}>'.format(context)
