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


class FlowRevisionList(ListResource):
    """ PLEASE NOTE that this class contains beta products that are subject to
    change. Use them with caution. """

    def __init__(self, version, sid):
        """
        Initialize the FlowRevisionList

        :param Version version: Version that contains the resource
        :param sid: The unique string that identifies the resource

        :returns: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionList
        :rtype: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionList
        """
        super(FlowRevisionList, self).__init__(version)

        # Path Solution
        self._solution = {'sid': sid, }
        self._uri = '/Flows/{sid}/Revisions'.format(**self._solution)

    def stream(self, limit=None, page_size=None):
        """
        Streams FlowRevisionInstance records from the API as a generator stream.
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
        :rtype: list[twilio.rest.studio.v2.flow.flow_revision.FlowRevisionInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(page_size=limits['page_size'], )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, limit=None, page_size=None):
        """
        Lists FlowRevisionInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.studio.v2.flow.flow_revision.FlowRevisionInstance]
        """
        return list(self.stream(limit=limit, page_size=page_size, ))

    def page(self, page_token=values.unset, page_number=values.unset,
             page_size=values.unset):
        """
        Retrieve a single page of FlowRevisionInstance records from the API.
        Request is executed immediately

        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of FlowRevisionInstance
        :rtype: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionPage
        """
        data = values.of({'PageToken': page_token, 'Page': page_number, 'PageSize': page_size, })

        response = self._version.page(method='GET', uri=self._uri, params=data, )

        return FlowRevisionPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of FlowRevisionInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of FlowRevisionInstance
        :rtype: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return FlowRevisionPage(self._version, response, self._solution)

    def get(self, revision):
        """
        Constructs a FlowRevisionContext

        :param revision: Specific Revision number or can be `LatestPublished` and `LatestRevision`

        :returns: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionContext
        :rtype: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionContext
        """
        return FlowRevisionContext(self._version, sid=self._solution['sid'], revision=revision, )

    def __call__(self, revision):
        """
        Constructs a FlowRevisionContext

        :param revision: Specific Revision number or can be `LatestPublished` and `LatestRevision`

        :returns: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionContext
        :rtype: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionContext
        """
        return FlowRevisionContext(self._version, sid=self._solution['sid'], revision=revision, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Studio.V2.FlowRevisionList>'


class FlowRevisionPage(Page):
    """ PLEASE NOTE that this class contains beta products that are subject to
    change. Use them with caution. """

    def __init__(self, version, response, solution):
        """
        Initialize the FlowRevisionPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API
        :param sid: The unique string that identifies the resource

        :returns: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionPage
        :rtype: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionPage
        """
        super(FlowRevisionPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of FlowRevisionInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionInstance
        :rtype: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionInstance
        """
        return FlowRevisionInstance(self._version, payload, sid=self._solution['sid'], )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Studio.V2.FlowRevisionPage>'


class FlowRevisionContext(InstanceContext):
    """ PLEASE NOTE that this class contains beta products that are subject to
    change. Use them with caution. """

    def __init__(self, version, sid, revision):
        """
        Initialize the FlowRevisionContext

        :param Version version: Version that contains the resource
        :param sid: The SID that identifies the resource to fetch
        :param revision: Specific Revision number or can be `LatestPublished` and `LatestRevision`

        :returns: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionContext
        :rtype: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionContext
        """
        super(FlowRevisionContext, self).__init__(version)

        # Path Solution
        self._solution = {'sid': sid, 'revision': revision, }
        self._uri = '/Flows/{sid}/Revisions/{revision}'.format(**self._solution)

    def fetch(self):
        """
        Fetch the FlowRevisionInstance

        :returns: The fetched FlowRevisionInstance
        :rtype: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return FlowRevisionInstance(
            self._version,
            payload,
            sid=self._solution['sid'],
            revision=self._solution['revision'],
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Studio.V2.FlowRevisionContext {}>'.format(context)


class FlowRevisionInstance(InstanceResource):
    """ PLEASE NOTE that this class contains beta products that are subject to
    change. Use them with caution. """

    class Status(object):
        DRAFT = "draft"
        PUBLISHED = "published"

    def __init__(self, version, payload, sid, revision=None):
        """
        Initialize the FlowRevisionInstance

        :returns: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionInstance
        :rtype: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionInstance
        """
        super(FlowRevisionInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'sid': payload.get('sid'),
            'account_sid': payload.get('account_sid'),
            'friendly_name': payload.get('friendly_name'),
            'definition': payload.get('definition'),
            'status': payload.get('status'),
            'revision': deserialize.integer(payload.get('revision')),
            'commit_message': payload.get('commit_message'),
            'valid': payload.get('valid'),
            'errors': payload.get('errors'),
            'date_created': deserialize.iso8601_datetime(payload.get('date_created')),
            'date_updated': deserialize.iso8601_datetime(payload.get('date_updated')),
            'url': payload.get('url'),
        }

        # Context
        self._context = None
        self._solution = {'sid': sid, 'revision': revision or self._properties['revision'], }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: FlowRevisionContext for this FlowRevisionInstance
        :rtype: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionContext
        """
        if self._context is None:
            self._context = FlowRevisionContext(
                self._version,
                sid=self._solution['sid'],
                revision=self._solution['revision'],
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
    def friendly_name(self):
        """
        :returns: The string that you assigned to describe the Flow
        :rtype: unicode
        """
        return self._properties['friendly_name']

    @property
    def definition(self):
        """
        :returns: JSON representation of flow definition
        :rtype: dict
        """
        return self._properties['definition']

    @property
    def status(self):
        """
        :returns: The status of the Flow
        :rtype: FlowRevisionInstance.Status
        """
        return self._properties['status']

    @property
    def revision(self):
        """
        :returns: The latest revision number of the Flow's definition
        :rtype: unicode
        """
        return self._properties['revision']

    @property
    def commit_message(self):
        """
        :returns: Description on change made in the revision
        :rtype: unicode
        """
        return self._properties['commit_message']

    @property
    def valid(self):
        """
        :returns: Boolean if the flow definition is valid
        :rtype: bool
        """
        return self._properties['valid']

    @property
    def errors(self):
        """
        :returns: List of error in the flow definition
        :rtype: dict
        """
        return self._properties['errors']

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

    def fetch(self):
        """
        Fetch the FlowRevisionInstance

        :returns: The fetched FlowRevisionInstance
        :rtype: twilio.rest.studio.v2.flow.flow_revision.FlowRevisionInstance
        """
        return self._proxy.fetch()

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Studio.V2.FlowRevisionInstance {}>'.format(context)
