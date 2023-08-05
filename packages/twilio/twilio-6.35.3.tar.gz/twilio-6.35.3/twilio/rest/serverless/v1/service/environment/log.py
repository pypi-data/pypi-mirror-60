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


class LogList(ListResource):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, service_sid, environment_sid):
        """
        Initialize the LogList

        :param Version version: Version that contains the resource
        :param service_sid: The SID of the Service that the Log resource is associated with
        :param environment_sid: The SID of the environment in which the log occurred

        :returns: twilio.rest.serverless.v1.service.environment.log.LogList
        :rtype: twilio.rest.serverless.v1.service.environment.log.LogList
        """
        super(LogList, self).__init__(version)

        # Path Solution
        self._solution = {'service_sid': service_sid, 'environment_sid': environment_sid, }
        self._uri = '/Services/{service_sid}/Environments/{environment_sid}/Logs'.format(**self._solution)

    def stream(self, function_sid=values.unset, start_date=values.unset,
               end_date=values.unset, limit=None, page_size=None):
        """
        Streams LogInstance records from the API as a generator stream.
        This operation lazily loads records as efficiently as possible until the limit
        is reached.
        The results are returned as a generator, so this operation is memory efficient.

        :param unicode function_sid: The SID of the function whose invocation produced the Log resources to read
        :param datetime start_date: The date and time after which the Log resources must have been created.
        :param datetime end_date: The date and time before which the Log resource must have been created.
        :param int limit: Upper limit for the number of records to return. stream()
                          guarantees to never return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, stream() will attempt to read the
                              limit with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.serverless.v1.service.environment.log.LogInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(
            function_sid=function_sid,
            start_date=start_date,
            end_date=end_date,
            page_size=limits['page_size'],
        )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, function_sid=values.unset, start_date=values.unset,
             end_date=values.unset, limit=None, page_size=None):
        """
        Lists LogInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param unicode function_sid: The SID of the function whose invocation produced the Log resources to read
        :param datetime start_date: The date and time after which the Log resources must have been created.
        :param datetime end_date: The date and time before which the Log resource must have been created.
        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.serverless.v1.service.environment.log.LogInstance]
        """
        return list(self.stream(
            function_sid=function_sid,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            page_size=page_size,
        ))

    def page(self, function_sid=values.unset, start_date=values.unset,
             end_date=values.unset, page_token=values.unset,
             page_number=values.unset, page_size=values.unset):
        """
        Retrieve a single page of LogInstance records from the API.
        Request is executed immediately

        :param unicode function_sid: The SID of the function whose invocation produced the Log resources to read
        :param datetime start_date: The date and time after which the Log resources must have been created.
        :param datetime end_date: The date and time before which the Log resource must have been created.
        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of LogInstance
        :rtype: twilio.rest.serverless.v1.service.environment.log.LogPage
        """
        data = values.of({
            'FunctionSid': function_sid,
            'StartDate': serialize.iso8601_datetime(start_date),
            'EndDate': serialize.iso8601_datetime(end_date),
            'PageToken': page_token,
            'Page': page_number,
            'PageSize': page_size,
        })

        response = self._version.page(method='GET', uri=self._uri, params=data, )

        return LogPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of LogInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of LogInstance
        :rtype: twilio.rest.serverless.v1.service.environment.log.LogPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return LogPage(self._version, response, self._solution)

    def get(self, sid):
        """
        Constructs a LogContext

        :param sid: The SID that identifies the Log resource to fetch

        :returns: twilio.rest.serverless.v1.service.environment.log.LogContext
        :rtype: twilio.rest.serverless.v1.service.environment.log.LogContext
        """
        return LogContext(
            self._version,
            service_sid=self._solution['service_sid'],
            environment_sid=self._solution['environment_sid'],
            sid=sid,
        )

    def __call__(self, sid):
        """
        Constructs a LogContext

        :param sid: The SID that identifies the Log resource to fetch

        :returns: twilio.rest.serverless.v1.service.environment.log.LogContext
        :rtype: twilio.rest.serverless.v1.service.environment.log.LogContext
        """
        return LogContext(
            self._version,
            service_sid=self._solution['service_sid'],
            environment_sid=self._solution['environment_sid'],
            sid=sid,
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Serverless.V1.LogList>'


class LogPage(Page):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, response, solution):
        """
        Initialize the LogPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API
        :param service_sid: The SID of the Service that the Log resource is associated with
        :param environment_sid: The SID of the environment in which the log occurred

        :returns: twilio.rest.serverless.v1.service.environment.log.LogPage
        :rtype: twilio.rest.serverless.v1.service.environment.log.LogPage
        """
        super(LogPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of LogInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.serverless.v1.service.environment.log.LogInstance
        :rtype: twilio.rest.serverless.v1.service.environment.log.LogInstance
        """
        return LogInstance(
            self._version,
            payload,
            service_sid=self._solution['service_sid'],
            environment_sid=self._solution['environment_sid'],
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Serverless.V1.LogPage>'


class LogContext(InstanceContext):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, service_sid, environment_sid, sid):
        """
        Initialize the LogContext

        :param Version version: Version that contains the resource
        :param service_sid: The SID of the Service to fetch the Log resource from
        :param environment_sid: The SID of the environment with the Log resource to fetch
        :param sid: The SID that identifies the Log resource to fetch

        :returns: twilio.rest.serverless.v1.service.environment.log.LogContext
        :rtype: twilio.rest.serverless.v1.service.environment.log.LogContext
        """
        super(LogContext, self).__init__(version)

        # Path Solution
        self._solution = {'service_sid': service_sid, 'environment_sid': environment_sid, 'sid': sid, }
        self._uri = '/Services/{service_sid}/Environments/{environment_sid}/Logs/{sid}'.format(**self._solution)

    def fetch(self):
        """
        Fetch the LogInstance

        :returns: The fetched LogInstance
        :rtype: twilio.rest.serverless.v1.service.environment.log.LogInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return LogInstance(
            self._version,
            payload,
            service_sid=self._solution['service_sid'],
            environment_sid=self._solution['environment_sid'],
            sid=self._solution['sid'],
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Serverless.V1.LogContext {}>'.format(context)


class LogInstance(InstanceResource):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    class Level(object):
        INFO = "info"
        WARN = "warn"
        ERROR = "error"

    def __init__(self, version, payload, service_sid, environment_sid, sid=None):
        """
        Initialize the LogInstance

        :returns: twilio.rest.serverless.v1.service.environment.log.LogInstance
        :rtype: twilio.rest.serverless.v1.service.environment.log.LogInstance
        """
        super(LogInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'sid': payload.get('sid'),
            'account_sid': payload.get('account_sid'),
            'service_sid': payload.get('service_sid'),
            'environment_sid': payload.get('environment_sid'),
            'deployment_sid': payload.get('deployment_sid'),
            'function_sid': payload.get('function_sid'),
            'request_sid': payload.get('request_sid'),
            'level': payload.get('level'),
            'message': payload.get('message'),
            'date_created': deserialize.iso8601_datetime(payload.get('date_created')),
            'url': payload.get('url'),
        }

        # Context
        self._context = None
        self._solution = {
            'service_sid': service_sid,
            'environment_sid': environment_sid,
            'sid': sid or self._properties['sid'],
        }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: LogContext for this LogInstance
        :rtype: twilio.rest.serverless.v1.service.environment.log.LogContext
        """
        if self._context is None:
            self._context = LogContext(
                self._version,
                service_sid=self._solution['service_sid'],
                environment_sid=self._solution['environment_sid'],
                sid=self._solution['sid'],
            )
        return self._context

    @property
    def sid(self):
        """
        :returns: The unique string that identifies the Log resource
        :rtype: unicode
        """
        return self._properties['sid']

    @property
    def account_sid(self):
        """
        :returns: The SID of the Account that created the Log resource
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def service_sid(self):
        """
        :returns: The SID of the Service that the Log resource is associated with
        :rtype: unicode
        """
        return self._properties['service_sid']

    @property
    def environment_sid(self):
        """
        :returns: The SID of the environment in which the log occurred
        :rtype: unicode
        """
        return self._properties['environment_sid']

    @property
    def deployment_sid(self):
        """
        :returns: The SID of the deployment that corresponds to the log
        :rtype: unicode
        """
        return self._properties['deployment_sid']

    @property
    def function_sid(self):
        """
        :returns: The SID of the function whose invocation produced the log
        :rtype: unicode
        """
        return self._properties['function_sid']

    @property
    def request_sid(self):
        """
        :returns: The SID of the request associated with the log
        :rtype: unicode
        """
        return self._properties['request_sid']

    @property
    def level(self):
        """
        :returns: The log level
        :rtype: LogInstance.Level
        """
        return self._properties['level']

    @property
    def message(self):
        """
        :returns: The log message
        :rtype: unicode
        """
        return self._properties['message']

    @property
    def date_created(self):
        """
        :returns: The ISO 8601 date and time in GMT when the Log resource was created
        :rtype: datetime
        """
        return self._properties['date_created']

    @property
    def url(self):
        """
        :returns: The absolute URL of the Log resource
        :rtype: unicode
        """
        return self._properties['url']

    def fetch(self):
        """
        Fetch the LogInstance

        :returns: The fetched LogInstance
        :rtype: twilio.rest.serverless.v1.service.environment.log.LogInstance
        """
        return self._proxy.fetch()

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Serverless.V1.LogInstance {}>'.format(context)
