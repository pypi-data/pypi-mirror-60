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
from twilio.rest.preview.understand.assistant.assistant_fallback_actions import AssistantFallbackActionsList
from twilio.rest.preview.understand.assistant.assistant_initiation_actions import AssistantInitiationActionsList
from twilio.rest.preview.understand.assistant.dialogue import DialogueList
from twilio.rest.preview.understand.assistant.field_type import FieldTypeList
from twilio.rest.preview.understand.assistant.model_build import ModelBuildList
from twilio.rest.preview.understand.assistant.query import QueryList
from twilio.rest.preview.understand.assistant.style_sheet import StyleSheetList
from twilio.rest.preview.understand.assistant.task import TaskList


class AssistantList(ListResource):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version):
        """
        Initialize the AssistantList

        :param Version version: Version that contains the resource

        :returns: twilio.rest.preview.understand.assistant.AssistantList
        :rtype: twilio.rest.preview.understand.assistant.AssistantList
        """
        super(AssistantList, self).__init__(version)

        # Path Solution
        self._solution = {}
        self._uri = '/Assistants'.format(**self._solution)

    def stream(self, limit=None, page_size=None):
        """
        Streams AssistantInstance records from the API as a generator stream.
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
        :rtype: list[twilio.rest.preview.understand.assistant.AssistantInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(page_size=limits['page_size'], )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, limit=None, page_size=None):
        """
        Lists AssistantInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.preview.understand.assistant.AssistantInstance]
        """
        return list(self.stream(limit=limit, page_size=page_size, ))

    def page(self, page_token=values.unset, page_number=values.unset,
             page_size=values.unset):
        """
        Retrieve a single page of AssistantInstance records from the API.
        Request is executed immediately

        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of AssistantInstance
        :rtype: twilio.rest.preview.understand.assistant.AssistantPage
        """
        data = values.of({'PageToken': page_token, 'Page': page_number, 'PageSize': page_size, })

        response = self._version.page(method='GET', uri=self._uri, params=data, )

        return AssistantPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of AssistantInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of AssistantInstance
        :rtype: twilio.rest.preview.understand.assistant.AssistantPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return AssistantPage(self._version, response, self._solution)

    def create(self, friendly_name=values.unset, log_queries=values.unset,
               unique_name=values.unset, callback_url=values.unset,
               callback_events=values.unset, fallback_actions=values.unset,
               initiation_actions=values.unset, style_sheet=values.unset):
        """
        Create the AssistantInstance

        :param unicode friendly_name: A text description for the Assistant. It is non-unique and can up to 255 characters long.
        :param bool log_queries: A boolean that specifies whether queries should be logged for 30 days further training. If false, no queries will be stored, if true, queries will be stored for 30 days and deleted thereafter. Defaults to true if no value is provided.
        :param unicode unique_name: A user-provided string that uniquely identifies this resource as an alternative to the sid. Unique up to 64 characters long.
        :param unicode callback_url: A user-provided URL to send event callbacks to.
        :param unicode callback_events: Space-separated list of callback events that will trigger callbacks.
        :param dict fallback_actions: The JSON actions to be executed when the user's input is not recognized as matching any Task.
        :param dict initiation_actions: The JSON actions to be executed on inbound phone calls when the Assistant has to say something first.
        :param dict style_sheet: The JSON object that holds the style sheet for the assistant

        :returns: The created AssistantInstance
        :rtype: twilio.rest.preview.understand.assistant.AssistantInstance
        """
        data = values.of({
            'FriendlyName': friendly_name,
            'LogQueries': log_queries,
            'UniqueName': unique_name,
            'CallbackUrl': callback_url,
            'CallbackEvents': callback_events,
            'FallbackActions': serialize.object(fallback_actions),
            'InitiationActions': serialize.object(initiation_actions),
            'StyleSheet': serialize.object(style_sheet),
        })

        payload = self._version.create(method='POST', uri=self._uri, data=data, )

        return AssistantInstance(self._version, payload, )

    def get(self, sid):
        """
        Constructs a AssistantContext

        :param sid: A 34 character string that uniquely identifies this resource.

        :returns: twilio.rest.preview.understand.assistant.AssistantContext
        :rtype: twilio.rest.preview.understand.assistant.AssistantContext
        """
        return AssistantContext(self._version, sid=sid, )

    def __call__(self, sid):
        """
        Constructs a AssistantContext

        :param sid: A 34 character string that uniquely identifies this resource.

        :returns: twilio.rest.preview.understand.assistant.AssistantContext
        :rtype: twilio.rest.preview.understand.assistant.AssistantContext
        """
        return AssistantContext(self._version, sid=sid, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Preview.Understand.AssistantList>'


class AssistantPage(Page):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, response, solution):
        """
        Initialize the AssistantPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API

        :returns: twilio.rest.preview.understand.assistant.AssistantPage
        :rtype: twilio.rest.preview.understand.assistant.AssistantPage
        """
        super(AssistantPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of AssistantInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.preview.understand.assistant.AssistantInstance
        :rtype: twilio.rest.preview.understand.assistant.AssistantInstance
        """
        return AssistantInstance(self._version, payload, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Preview.Understand.AssistantPage>'


class AssistantContext(InstanceContext):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, sid):
        """
        Initialize the AssistantContext

        :param Version version: Version that contains the resource
        :param sid: A 34 character string that uniquely identifies this resource.

        :returns: twilio.rest.preview.understand.assistant.AssistantContext
        :rtype: twilio.rest.preview.understand.assistant.AssistantContext
        """
        super(AssistantContext, self).__init__(version)

        # Path Solution
        self._solution = {'sid': sid, }
        self._uri = '/Assistants/{sid}'.format(**self._solution)

        # Dependents
        self._field_types = None
        self._tasks = None
        self._model_builds = None
        self._queries = None
        self._assistant_fallback_actions = None
        self._assistant_initiation_actions = None
        self._dialogues = None
        self._style_sheet = None

    def fetch(self):
        """
        Fetch the AssistantInstance

        :returns: The fetched AssistantInstance
        :rtype: twilio.rest.preview.understand.assistant.AssistantInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return AssistantInstance(self._version, payload, sid=self._solution['sid'], )

    def update(self, friendly_name=values.unset, log_queries=values.unset,
               unique_name=values.unset, callback_url=values.unset,
               callback_events=values.unset, fallback_actions=values.unset,
               initiation_actions=values.unset, style_sheet=values.unset):
        """
        Update the AssistantInstance

        :param unicode friendly_name: A text description for the Assistant. It is non-unique and can up to 255 characters long.
        :param bool log_queries: A boolean that specifies whether queries should be logged for 30 days further training. If false, no queries will be stored, if true, queries will be stored for 30 days and deleted thereafter. Defaults to true if no value is provided.
        :param unicode unique_name: A user-provided string that uniquely identifies this resource as an alternative to the sid. Unique up to 64 characters long.
        :param unicode callback_url: A user-provided URL to send event callbacks to.
        :param unicode callback_events: Space-separated list of callback events that will trigger callbacks.
        :param dict fallback_actions: The JSON actions to be executed when the user's input is not recognized as matching any Task.
        :param dict initiation_actions: The JSON actions to be executed on inbound phone calls when the Assistant has to say something first.
        :param dict style_sheet: The JSON object that holds the style sheet for the assistant

        :returns: The updated AssistantInstance
        :rtype: twilio.rest.preview.understand.assistant.AssistantInstance
        """
        data = values.of({
            'FriendlyName': friendly_name,
            'LogQueries': log_queries,
            'UniqueName': unique_name,
            'CallbackUrl': callback_url,
            'CallbackEvents': callback_events,
            'FallbackActions': serialize.object(fallback_actions),
            'InitiationActions': serialize.object(initiation_actions),
            'StyleSheet': serialize.object(style_sheet),
        })

        payload = self._version.update(method='POST', uri=self._uri, data=data, )

        return AssistantInstance(self._version, payload, sid=self._solution['sid'], )

    def delete(self):
        """
        Deletes the AssistantInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._version.delete(method='DELETE', uri=self._uri, )

    @property
    def field_types(self):
        """
        Access the field_types

        :returns: twilio.rest.preview.understand.assistant.field_type.FieldTypeList
        :rtype: twilio.rest.preview.understand.assistant.field_type.FieldTypeList
        """
        if self._field_types is None:
            self._field_types = FieldTypeList(self._version, assistant_sid=self._solution['sid'], )
        return self._field_types

    @property
    def tasks(self):
        """
        Access the tasks

        :returns: twilio.rest.preview.understand.assistant.task.TaskList
        :rtype: twilio.rest.preview.understand.assistant.task.TaskList
        """
        if self._tasks is None:
            self._tasks = TaskList(self._version, assistant_sid=self._solution['sid'], )
        return self._tasks

    @property
    def model_builds(self):
        """
        Access the model_builds

        :returns: twilio.rest.preview.understand.assistant.model_build.ModelBuildList
        :rtype: twilio.rest.preview.understand.assistant.model_build.ModelBuildList
        """
        if self._model_builds is None:
            self._model_builds = ModelBuildList(self._version, assistant_sid=self._solution['sid'], )
        return self._model_builds

    @property
    def queries(self):
        """
        Access the queries

        :returns: twilio.rest.preview.understand.assistant.query.QueryList
        :rtype: twilio.rest.preview.understand.assistant.query.QueryList
        """
        if self._queries is None:
            self._queries = QueryList(self._version, assistant_sid=self._solution['sid'], )
        return self._queries

    @property
    def assistant_fallback_actions(self):
        """
        Access the assistant_fallback_actions

        :returns: twilio.rest.preview.understand.assistant.assistant_fallback_actions.AssistantFallbackActionsList
        :rtype: twilio.rest.preview.understand.assistant.assistant_fallback_actions.AssistantFallbackActionsList
        """
        if self._assistant_fallback_actions is None:
            self._assistant_fallback_actions = AssistantFallbackActionsList(
                self._version,
                assistant_sid=self._solution['sid'],
            )
        return self._assistant_fallback_actions

    @property
    def assistant_initiation_actions(self):
        """
        Access the assistant_initiation_actions

        :returns: twilio.rest.preview.understand.assistant.assistant_initiation_actions.AssistantInitiationActionsList
        :rtype: twilio.rest.preview.understand.assistant.assistant_initiation_actions.AssistantInitiationActionsList
        """
        if self._assistant_initiation_actions is None:
            self._assistant_initiation_actions = AssistantInitiationActionsList(
                self._version,
                assistant_sid=self._solution['sid'],
            )
        return self._assistant_initiation_actions

    @property
    def dialogues(self):
        """
        Access the dialogues

        :returns: twilio.rest.preview.understand.assistant.dialogue.DialogueList
        :rtype: twilio.rest.preview.understand.assistant.dialogue.DialogueList
        """
        if self._dialogues is None:
            self._dialogues = DialogueList(self._version, assistant_sid=self._solution['sid'], )
        return self._dialogues

    @property
    def style_sheet(self):
        """
        Access the style_sheet

        :returns: twilio.rest.preview.understand.assistant.style_sheet.StyleSheetList
        :rtype: twilio.rest.preview.understand.assistant.style_sheet.StyleSheetList
        """
        if self._style_sheet is None:
            self._style_sheet = StyleSheetList(self._version, assistant_sid=self._solution['sid'], )
        return self._style_sheet

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Preview.Understand.AssistantContext {}>'.format(context)


class AssistantInstance(InstanceResource):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, payload, sid=None):
        """
        Initialize the AssistantInstance

        :returns: twilio.rest.preview.understand.assistant.AssistantInstance
        :rtype: twilio.rest.preview.understand.assistant.AssistantInstance
        """
        super(AssistantInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'account_sid': payload.get('account_sid'),
            'date_created': deserialize.iso8601_datetime(payload.get('date_created')),
            'date_updated': deserialize.iso8601_datetime(payload.get('date_updated')),
            'friendly_name': payload.get('friendly_name'),
            'latest_model_build_sid': payload.get('latest_model_build_sid'),
            'links': payload.get('links'),
            'log_queries': payload.get('log_queries'),
            'sid': payload.get('sid'),
            'unique_name': payload.get('unique_name'),
            'url': payload.get('url'),
            'callback_url': payload.get('callback_url'),
            'callback_events': payload.get('callback_events'),
        }

        # Context
        self._context = None
        self._solution = {'sid': sid or self._properties['sid'], }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: AssistantContext for this AssistantInstance
        :rtype: twilio.rest.preview.understand.assistant.AssistantContext
        """
        if self._context is None:
            self._context = AssistantContext(self._version, sid=self._solution['sid'], )
        return self._context

    @property
    def account_sid(self):
        """
        :returns: The unique ID of the Account that created this Assistant.
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def date_created(self):
        """
        :returns: The date that this resource was created
        :rtype: datetime
        """
        return self._properties['date_created']

    @property
    def date_updated(self):
        """
        :returns: The date that this resource was last updated
        :rtype: datetime
        """
        return self._properties['date_updated']

    @property
    def friendly_name(self):
        """
        :returns: A text description for the Assistant. It is non-unique and can up to 255 characters long.
        :rtype: unicode
        """
        return self._properties['friendly_name']

    @property
    def latest_model_build_sid(self):
        """
        :returns: The unique ID (Sid) of the latest model build. Null if no model has been built.
        :rtype: unicode
        """
        return self._properties['latest_model_build_sid']

    @property
    def links(self):
        """
        :returns: The links
        :rtype: unicode
        """
        return self._properties['links']

    @property
    def log_queries(self):
        """
        :returns: A boolean that specifies whether queries should be logged for 30 days further training. If false, no queries will be stored, if true, queries will be stored for 30 days and deleted thereafter.
        :rtype: bool
        """
        return self._properties['log_queries']

    @property
    def sid(self):
        """
        :returns: A 34 character string that uniquely identifies this resource.
        :rtype: unicode
        """
        return self._properties['sid']

    @property
    def unique_name(self):
        """
        :returns: A user-provided string that uniquely identifies this resource as an alternative to the sid. You can use the unique name in the URL path. Unique up to 64 characters long.
        :rtype: unicode
        """
        return self._properties['unique_name']

    @property
    def url(self):
        """
        :returns: The url
        :rtype: unicode
        """
        return self._properties['url']

    @property
    def callback_url(self):
        """
        :returns: A user-provided URL to send event callbacks to.
        :rtype: unicode
        """
        return self._properties['callback_url']

    @property
    def callback_events(self):
        """
        :returns: Space-separated list of callback events that will trigger callbacks.
        :rtype: unicode
        """
        return self._properties['callback_events']

    def fetch(self):
        """
        Fetch the AssistantInstance

        :returns: The fetched AssistantInstance
        :rtype: twilio.rest.preview.understand.assistant.AssistantInstance
        """
        return self._proxy.fetch()

    def update(self, friendly_name=values.unset, log_queries=values.unset,
               unique_name=values.unset, callback_url=values.unset,
               callback_events=values.unset, fallback_actions=values.unset,
               initiation_actions=values.unset, style_sheet=values.unset):
        """
        Update the AssistantInstance

        :param unicode friendly_name: A text description for the Assistant. It is non-unique and can up to 255 characters long.
        :param bool log_queries: A boolean that specifies whether queries should be logged for 30 days further training. If false, no queries will be stored, if true, queries will be stored for 30 days and deleted thereafter. Defaults to true if no value is provided.
        :param unicode unique_name: A user-provided string that uniquely identifies this resource as an alternative to the sid. Unique up to 64 characters long.
        :param unicode callback_url: A user-provided URL to send event callbacks to.
        :param unicode callback_events: Space-separated list of callback events that will trigger callbacks.
        :param dict fallback_actions: The JSON actions to be executed when the user's input is not recognized as matching any Task.
        :param dict initiation_actions: The JSON actions to be executed on inbound phone calls when the Assistant has to say something first.
        :param dict style_sheet: The JSON object that holds the style sheet for the assistant

        :returns: The updated AssistantInstance
        :rtype: twilio.rest.preview.understand.assistant.AssistantInstance
        """
        return self._proxy.update(
            friendly_name=friendly_name,
            log_queries=log_queries,
            unique_name=unique_name,
            callback_url=callback_url,
            callback_events=callback_events,
            fallback_actions=fallback_actions,
            initiation_actions=initiation_actions,
            style_sheet=style_sheet,
        )

    def delete(self):
        """
        Deletes the AssistantInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._proxy.delete()

    @property
    def field_types(self):
        """
        Access the field_types

        :returns: twilio.rest.preview.understand.assistant.field_type.FieldTypeList
        :rtype: twilio.rest.preview.understand.assistant.field_type.FieldTypeList
        """
        return self._proxy.field_types

    @property
    def tasks(self):
        """
        Access the tasks

        :returns: twilio.rest.preview.understand.assistant.task.TaskList
        :rtype: twilio.rest.preview.understand.assistant.task.TaskList
        """
        return self._proxy.tasks

    @property
    def model_builds(self):
        """
        Access the model_builds

        :returns: twilio.rest.preview.understand.assistant.model_build.ModelBuildList
        :rtype: twilio.rest.preview.understand.assistant.model_build.ModelBuildList
        """
        return self._proxy.model_builds

    @property
    def queries(self):
        """
        Access the queries

        :returns: twilio.rest.preview.understand.assistant.query.QueryList
        :rtype: twilio.rest.preview.understand.assistant.query.QueryList
        """
        return self._proxy.queries

    @property
    def assistant_fallback_actions(self):
        """
        Access the assistant_fallback_actions

        :returns: twilio.rest.preview.understand.assistant.assistant_fallback_actions.AssistantFallbackActionsList
        :rtype: twilio.rest.preview.understand.assistant.assistant_fallback_actions.AssistantFallbackActionsList
        """
        return self._proxy.assistant_fallback_actions

    @property
    def assistant_initiation_actions(self):
        """
        Access the assistant_initiation_actions

        :returns: twilio.rest.preview.understand.assistant.assistant_initiation_actions.AssistantInitiationActionsList
        :rtype: twilio.rest.preview.understand.assistant.assistant_initiation_actions.AssistantInitiationActionsList
        """
        return self._proxy.assistant_initiation_actions

    @property
    def dialogues(self):
        """
        Access the dialogues

        :returns: twilio.rest.preview.understand.assistant.dialogue.DialogueList
        :rtype: twilio.rest.preview.understand.assistant.dialogue.DialogueList
        """
        return self._proxy.dialogues

    @property
    def style_sheet(self):
        """
        Access the style_sheet

        :returns: twilio.rest.preview.understand.assistant.style_sheet.StyleSheetList
        :rtype: twilio.rest.preview.understand.assistant.style_sheet.StyleSheetList
        """
        return self._proxy.style_sheet

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Preview.Understand.AssistantInstance {}>'.format(context)
