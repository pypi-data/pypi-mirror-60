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
from twilio.rest.serverless.v1.service.asset import AssetList
from twilio.rest.serverless.v1.service.build import BuildList
from twilio.rest.serverless.v1.service.environment import EnvironmentList
from twilio.rest.serverless.v1.service.function import FunctionList


class ServiceList(ListResource):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version):
        """
        Initialize the ServiceList

        :param Version version: Version that contains the resource

        :returns: twilio.rest.serverless.v1.service.ServiceList
        :rtype: twilio.rest.serverless.v1.service.ServiceList
        """
        super(ServiceList, self).__init__(version)

        # Path Solution
        self._solution = {}
        self._uri = '/Services'.format(**self._solution)

    def stream(self, limit=None, page_size=None):
        """
        Streams ServiceInstance records from the API as a generator stream.
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
        :rtype: list[twilio.rest.serverless.v1.service.ServiceInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(page_size=limits['page_size'], )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, limit=None, page_size=None):
        """
        Lists ServiceInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.serverless.v1.service.ServiceInstance]
        """
        return list(self.stream(limit=limit, page_size=page_size, ))

    def page(self, page_token=values.unset, page_number=values.unset,
             page_size=values.unset):
        """
        Retrieve a single page of ServiceInstance records from the API.
        Request is executed immediately

        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of ServiceInstance
        :rtype: twilio.rest.serverless.v1.service.ServicePage
        """
        data = values.of({'PageToken': page_token, 'Page': page_number, 'PageSize': page_size, })

        response = self._version.page(method='GET', uri=self._uri, params=data, )

        return ServicePage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of ServiceInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of ServiceInstance
        :rtype: twilio.rest.serverless.v1.service.ServicePage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return ServicePage(self._version, response, self._solution)

    def create(self, unique_name, friendly_name, include_credentials=values.unset):
        """
        Create the ServiceInstance

        :param unicode unique_name: An application-defined string that uniquely identifies the Service resource
        :param unicode friendly_name: A string to describe the Service resource
        :param bool include_credentials: Whether to inject Account credentials into a function invocation context

        :returns: The created ServiceInstance
        :rtype: twilio.rest.serverless.v1.service.ServiceInstance
        """
        data = values.of({
            'UniqueName': unique_name,
            'FriendlyName': friendly_name,
            'IncludeCredentials': include_credentials,
        })

        payload = self._version.create(method='POST', uri=self._uri, data=data, )

        return ServiceInstance(self._version, payload, )

    def get(self, sid):
        """
        Constructs a ServiceContext

        :param sid: The SID of the Service resource to fetch

        :returns: twilio.rest.serverless.v1.service.ServiceContext
        :rtype: twilio.rest.serverless.v1.service.ServiceContext
        """
        return ServiceContext(self._version, sid=sid, )

    def __call__(self, sid):
        """
        Constructs a ServiceContext

        :param sid: The SID of the Service resource to fetch

        :returns: twilio.rest.serverless.v1.service.ServiceContext
        :rtype: twilio.rest.serverless.v1.service.ServiceContext
        """
        return ServiceContext(self._version, sid=sid, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Serverless.V1.ServiceList>'


class ServicePage(Page):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, response, solution):
        """
        Initialize the ServicePage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API

        :returns: twilio.rest.serverless.v1.service.ServicePage
        :rtype: twilio.rest.serverless.v1.service.ServicePage
        """
        super(ServicePage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of ServiceInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.serverless.v1.service.ServiceInstance
        :rtype: twilio.rest.serverless.v1.service.ServiceInstance
        """
        return ServiceInstance(self._version, payload, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Serverless.V1.ServicePage>'


class ServiceContext(InstanceContext):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, sid):
        """
        Initialize the ServiceContext

        :param Version version: Version that contains the resource
        :param sid: The SID of the Service resource to fetch

        :returns: twilio.rest.serverless.v1.service.ServiceContext
        :rtype: twilio.rest.serverless.v1.service.ServiceContext
        """
        super(ServiceContext, self).__init__(version)

        # Path Solution
        self._solution = {'sid': sid, }
        self._uri = '/Services/{sid}'.format(**self._solution)

        # Dependents
        self._environments = None
        self._functions = None
        self._assets = None
        self._builds = None

    def fetch(self):
        """
        Fetch the ServiceInstance

        :returns: The fetched ServiceInstance
        :rtype: twilio.rest.serverless.v1.service.ServiceInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return ServiceInstance(self._version, payload, sid=self._solution['sid'], )

    def delete(self):
        """
        Deletes the ServiceInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._version.delete(method='DELETE', uri=self._uri, )

    def update(self, include_credentials=values.unset, friendly_name=values.unset):
        """
        Update the ServiceInstance

        :param bool include_credentials: Whether to inject Account credentials into a function invocation context
        :param unicode friendly_name: A string to describe the Service resource

        :returns: The updated ServiceInstance
        :rtype: twilio.rest.serverless.v1.service.ServiceInstance
        """
        data = values.of({'IncludeCredentials': include_credentials, 'FriendlyName': friendly_name, })

        payload = self._version.update(method='POST', uri=self._uri, data=data, )

        return ServiceInstance(self._version, payload, sid=self._solution['sid'], )

    @property
    def environments(self):
        """
        Access the environments

        :returns: twilio.rest.serverless.v1.service.environment.EnvironmentList
        :rtype: twilio.rest.serverless.v1.service.environment.EnvironmentList
        """
        if self._environments is None:
            self._environments = EnvironmentList(self._version, service_sid=self._solution['sid'], )
        return self._environments

    @property
    def functions(self):
        """
        Access the functions

        :returns: twilio.rest.serverless.v1.service.function.FunctionList
        :rtype: twilio.rest.serverless.v1.service.function.FunctionList
        """
        if self._functions is None:
            self._functions = FunctionList(self._version, service_sid=self._solution['sid'], )
        return self._functions

    @property
    def assets(self):
        """
        Access the assets

        :returns: twilio.rest.serverless.v1.service.asset.AssetList
        :rtype: twilio.rest.serverless.v1.service.asset.AssetList
        """
        if self._assets is None:
            self._assets = AssetList(self._version, service_sid=self._solution['sid'], )
        return self._assets

    @property
    def builds(self):
        """
        Access the builds

        :returns: twilio.rest.serverless.v1.service.build.BuildList
        :rtype: twilio.rest.serverless.v1.service.build.BuildList
        """
        if self._builds is None:
            self._builds = BuildList(self._version, service_sid=self._solution['sid'], )
        return self._builds

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Serverless.V1.ServiceContext {}>'.format(context)


class ServiceInstance(InstanceResource):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, payload, sid=None):
        """
        Initialize the ServiceInstance

        :returns: twilio.rest.serverless.v1.service.ServiceInstance
        :rtype: twilio.rest.serverless.v1.service.ServiceInstance
        """
        super(ServiceInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'sid': payload.get('sid'),
            'account_sid': payload.get('account_sid'),
            'friendly_name': payload.get('friendly_name'),
            'unique_name': payload.get('unique_name'),
            'include_credentials': payload.get('include_credentials'),
            'date_created': deserialize.iso8601_datetime(payload.get('date_created')),
            'date_updated': deserialize.iso8601_datetime(payload.get('date_updated')),
            'url': payload.get('url'),
            'links': payload.get('links'),
        }

        # Context
        self._context = None
        self._solution = {'sid': sid or self._properties['sid'], }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: ServiceContext for this ServiceInstance
        :rtype: twilio.rest.serverless.v1.service.ServiceContext
        """
        if self._context is None:
            self._context = ServiceContext(self._version, sid=self._solution['sid'], )
        return self._context

    @property
    def sid(self):
        """
        :returns: The unique string that identifies the Service resource
        :rtype: unicode
        """
        return self._properties['sid']

    @property
    def account_sid(self):
        """
        :returns: The SID of the Account that created the Service resource
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def friendly_name(self):
        """
        :returns: The string that you assigned to describe the Service resource
        :rtype: unicode
        """
        return self._properties['friendly_name']

    @property
    def unique_name(self):
        """
        :returns: An application-defined string that uniquely identifies the Service resource
        :rtype: unicode
        """
        return self._properties['unique_name']

    @property
    def include_credentials(self):
        """
        :returns: Whether to inject Account credentials into a function invocation context
        :rtype: bool
        """
        return self._properties['include_credentials']

    @property
    def date_created(self):
        """
        :returns: The ISO 8601 date and time in GMT when the Service resource was created
        :rtype: datetime
        """
        return self._properties['date_created']

    @property
    def date_updated(self):
        """
        :returns: The ISO 8601 date and time in GMT when the Service resource was last updated
        :rtype: datetime
        """
        return self._properties['date_updated']

    @property
    def url(self):
        """
        :returns: The absolute URL of the Service resource
        :rtype: unicode
        """
        return self._properties['url']

    @property
    def links(self):
        """
        :returns: The URLs of the Service's nested resources
        :rtype: unicode
        """
        return self._properties['links']

    def fetch(self):
        """
        Fetch the ServiceInstance

        :returns: The fetched ServiceInstance
        :rtype: twilio.rest.serverless.v1.service.ServiceInstance
        """
        return self._proxy.fetch()

    def delete(self):
        """
        Deletes the ServiceInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._proxy.delete()

    def update(self, include_credentials=values.unset, friendly_name=values.unset):
        """
        Update the ServiceInstance

        :param bool include_credentials: Whether to inject Account credentials into a function invocation context
        :param unicode friendly_name: A string to describe the Service resource

        :returns: The updated ServiceInstance
        :rtype: twilio.rest.serverless.v1.service.ServiceInstance
        """
        return self._proxy.update(include_credentials=include_credentials, friendly_name=friendly_name, )

    @property
    def environments(self):
        """
        Access the environments

        :returns: twilio.rest.serverless.v1.service.environment.EnvironmentList
        :rtype: twilio.rest.serverless.v1.service.environment.EnvironmentList
        """
        return self._proxy.environments

    @property
    def functions(self):
        """
        Access the functions

        :returns: twilio.rest.serverless.v1.service.function.FunctionList
        :rtype: twilio.rest.serverless.v1.service.function.FunctionList
        """
        return self._proxy.functions

    @property
    def assets(self):
        """
        Access the assets

        :returns: twilio.rest.serverless.v1.service.asset.AssetList
        :rtype: twilio.rest.serverless.v1.service.asset.AssetList
        """
        return self._proxy.assets

    @property
    def builds(self):
        """
        Access the builds

        :returns: twilio.rest.serverless.v1.service.build.BuildList
        :rtype: twilio.rest.serverless.v1.service.build.BuildList
        """
        return self._proxy.builds

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Serverless.V1.ServiceInstance {}>'.format(context)
