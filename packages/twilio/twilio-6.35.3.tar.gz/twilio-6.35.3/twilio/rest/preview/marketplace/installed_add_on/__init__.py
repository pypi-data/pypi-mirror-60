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
from twilio.rest.preview.marketplace.installed_add_on.installed_add_on_extension import InstalledAddOnExtensionList


class InstalledAddOnList(ListResource):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version):
        """
        Initialize the InstalledAddOnList

        :param Version version: Version that contains the resource

        :returns: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnList
        :rtype: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnList
        """
        super(InstalledAddOnList, self).__init__(version)

        # Path Solution
        self._solution = {}
        self._uri = '/InstalledAddOns'.format(**self._solution)

    def create(self, available_add_on_sid, accept_terms_of_service,
               configuration=values.unset, unique_name=values.unset):
        """
        Create the InstalledAddOnInstance

        :param unicode available_add_on_sid: The SID of the AvaliableAddOn to install
        :param bool accept_terms_of_service: Whether the Terms of Service were accepted
        :param dict configuration: The JSON object representing the configuration
        :param unicode unique_name: An application-defined string that uniquely identifies the resource

        :returns: The created InstalledAddOnInstance
        :rtype: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnInstance
        """
        data = values.of({
            'AvailableAddOnSid': available_add_on_sid,
            'AcceptTermsOfService': accept_terms_of_service,
            'Configuration': serialize.object(configuration),
            'UniqueName': unique_name,
        })

        payload = self._version.create(method='POST', uri=self._uri, data=data, )

        return InstalledAddOnInstance(self._version, payload, )

    def stream(self, limit=None, page_size=None):
        """
        Streams InstalledAddOnInstance records from the API as a generator stream.
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
        :rtype: list[twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(page_size=limits['page_size'], )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, limit=None, page_size=None):
        """
        Lists InstalledAddOnInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnInstance]
        """
        return list(self.stream(limit=limit, page_size=page_size, ))

    def page(self, page_token=values.unset, page_number=values.unset,
             page_size=values.unset):
        """
        Retrieve a single page of InstalledAddOnInstance records from the API.
        Request is executed immediately

        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of InstalledAddOnInstance
        :rtype: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnPage
        """
        data = values.of({'PageToken': page_token, 'Page': page_number, 'PageSize': page_size, })

        response = self._version.page(method='GET', uri=self._uri, params=data, )

        return InstalledAddOnPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of InstalledAddOnInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of InstalledAddOnInstance
        :rtype: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return InstalledAddOnPage(self._version, response, self._solution)

    def get(self, sid):
        """
        Constructs a InstalledAddOnContext

        :param sid: The SID of the InstalledAddOn resource to fetch

        :returns: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnContext
        :rtype: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnContext
        """
        return InstalledAddOnContext(self._version, sid=sid, )

    def __call__(self, sid):
        """
        Constructs a InstalledAddOnContext

        :param sid: The SID of the InstalledAddOn resource to fetch

        :returns: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnContext
        :rtype: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnContext
        """
        return InstalledAddOnContext(self._version, sid=sid, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Preview.Marketplace.InstalledAddOnList>'


class InstalledAddOnPage(Page):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, response, solution):
        """
        Initialize the InstalledAddOnPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API

        :returns: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnPage
        :rtype: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnPage
        """
        super(InstalledAddOnPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of InstalledAddOnInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnInstance
        :rtype: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnInstance
        """
        return InstalledAddOnInstance(self._version, payload, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Preview.Marketplace.InstalledAddOnPage>'


class InstalledAddOnContext(InstanceContext):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, sid):
        """
        Initialize the InstalledAddOnContext

        :param Version version: Version that contains the resource
        :param sid: The SID of the InstalledAddOn resource to fetch

        :returns: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnContext
        :rtype: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnContext
        """
        super(InstalledAddOnContext, self).__init__(version)

        # Path Solution
        self._solution = {'sid': sid, }
        self._uri = '/InstalledAddOns/{sid}'.format(**self._solution)

        # Dependents
        self._extensions = None

    def delete(self):
        """
        Deletes the InstalledAddOnInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._version.delete(method='DELETE', uri=self._uri, )

    def fetch(self):
        """
        Fetch the InstalledAddOnInstance

        :returns: The fetched InstalledAddOnInstance
        :rtype: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return InstalledAddOnInstance(self._version, payload, sid=self._solution['sid'], )

    def update(self, configuration=values.unset, unique_name=values.unset):
        """
        Update the InstalledAddOnInstance

        :param dict configuration: The JSON object representing the configuration
        :param unicode unique_name: An application-defined string that uniquely identifies the resource

        :returns: The updated InstalledAddOnInstance
        :rtype: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnInstance
        """
        data = values.of({'Configuration': serialize.object(configuration), 'UniqueName': unique_name, })

        payload = self._version.update(method='POST', uri=self._uri, data=data, )

        return InstalledAddOnInstance(self._version, payload, sid=self._solution['sid'], )

    @property
    def extensions(self):
        """
        Access the extensions

        :returns: twilio.rest.preview.marketplace.installed_add_on.installed_add_on_extension.InstalledAddOnExtensionList
        :rtype: twilio.rest.preview.marketplace.installed_add_on.installed_add_on_extension.InstalledAddOnExtensionList
        """
        if self._extensions is None:
            self._extensions = InstalledAddOnExtensionList(
                self._version,
                installed_add_on_sid=self._solution['sid'],
            )
        return self._extensions

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Preview.Marketplace.InstalledAddOnContext {}>'.format(context)


class InstalledAddOnInstance(InstanceResource):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, payload, sid=None):
        """
        Initialize the InstalledAddOnInstance

        :returns: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnInstance
        :rtype: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnInstance
        """
        super(InstalledAddOnInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'sid': payload.get('sid'),
            'account_sid': payload.get('account_sid'),
            'friendly_name': payload.get('friendly_name'),
            'description': payload.get('description'),
            'configuration': payload.get('configuration'),
            'unique_name': payload.get('unique_name'),
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

        :returns: InstalledAddOnContext for this InstalledAddOnInstance
        :rtype: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnContext
        """
        if self._context is None:
            self._context = InstalledAddOnContext(self._version, sid=self._solution['sid'], )
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
    def description(self):
        """
        :returns: A short description of the Add-on's functionality
        :rtype: unicode
        """
        return self._properties['description']

    @property
    def configuration(self):
        """
        :returns: The JSON object that represents the current configuration of installed Add-on
        :rtype: dict
        """
        return self._properties['configuration']

    @property
    def unique_name(self):
        """
        :returns: An application-defined string that uniquely identifies the resource
        :rtype: unicode
        """
        return self._properties['unique_name']

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
        :returns: The absolute URL of the resource
        :rtype: unicode
        """
        return self._properties['url']

    @property
    def links(self):
        """
        :returns: The URLs of related resources
        :rtype: unicode
        """
        return self._properties['links']

    def delete(self):
        """
        Deletes the InstalledAddOnInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._proxy.delete()

    def fetch(self):
        """
        Fetch the InstalledAddOnInstance

        :returns: The fetched InstalledAddOnInstance
        :rtype: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnInstance
        """
        return self._proxy.fetch()

    def update(self, configuration=values.unset, unique_name=values.unset):
        """
        Update the InstalledAddOnInstance

        :param dict configuration: The JSON object representing the configuration
        :param unicode unique_name: An application-defined string that uniquely identifies the resource

        :returns: The updated InstalledAddOnInstance
        :rtype: twilio.rest.preview.marketplace.installed_add_on.InstalledAddOnInstance
        """
        return self._proxy.update(configuration=configuration, unique_name=unique_name, )

    @property
    def extensions(self):
        """
        Access the extensions

        :returns: twilio.rest.preview.marketplace.installed_add_on.installed_add_on_extension.InstalledAddOnExtensionList
        :rtype: twilio.rest.preview.marketplace.installed_add_on.installed_add_on_extension.InstalledAddOnExtensionList
        """
        return self._proxy.extensions

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Preview.Marketplace.InstalledAddOnInstance {}>'.format(context)
