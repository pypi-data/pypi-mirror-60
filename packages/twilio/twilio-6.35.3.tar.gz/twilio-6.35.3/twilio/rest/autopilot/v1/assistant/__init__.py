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
from twilio.rest.autopilot.v1.assistant.defaults import DefaultsList
from twilio.rest.autopilot.v1.assistant.dialogue import DialogueList
from twilio.rest.autopilot.v1.assistant.export_assistant import ExportAssistantList
from twilio.rest.autopilot.v1.assistant.field_type import FieldTypeList
from twilio.rest.autopilot.v1.assistant.model_build import ModelBuildList
from twilio.rest.autopilot.v1.assistant.query import QueryList
from twilio.rest.autopilot.v1.assistant.style_sheet import StyleSheetList
from twilio.rest.autopilot.v1.assistant.task import TaskList
from twilio.rest.autopilot.v1.assistant.webhook import WebhookList


class AssistantList(ListResource):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version):
        """
        Initialize the AssistantList

        :param Version version: Version that contains the resource

        :returns: twilio.rest.autopilot.v1.assistant.AssistantList
        :rtype: twilio.rest.autopilot.v1.assistant.AssistantList
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
        :rtype: list[twilio.rest.autopilot.v1.assistant.AssistantInstance]
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
        :rtype: list[twilio.rest.autopilot.v1.assistant.AssistantInstance]
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
        :rtype: twilio.rest.autopilot.v1.assistant.AssistantPage
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
        :rtype: twilio.rest.autopilot.v1.assistant.AssistantPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return AssistantPage(self._version, response, self._solution)

    def create(self, friendly_name=values.unset, log_queries=values.unset,
               unique_name=values.unset, callback_url=values.unset,
               callback_events=values.unset, style_sheet=values.unset,
               defaults=values.unset):
        """
        Create the AssistantInstance

        :param unicode friendly_name: A string to describe the new resource
        :param bool log_queries: Whether queries should be logged and kept after training
        :param unicode unique_name: An application-defined string that uniquely identifies the new resource
        :param unicode callback_url: Reserved
        :param unicode callback_events: Reserved
        :param dict style_sheet: A JSON string that defines the Assistant's style sheet
        :param dict defaults: A JSON object that defines the Assistant's default tasks for various scenarios

        :returns: The created AssistantInstance
        :rtype: twilio.rest.autopilot.v1.assistant.AssistantInstance
        """
        data = values.of({
            'FriendlyName': friendly_name,
            'LogQueries': log_queries,
            'UniqueName': unique_name,
            'CallbackUrl': callback_url,
            'CallbackEvents': callback_events,
            'StyleSheet': serialize.object(style_sheet),
            'Defaults': serialize.object(defaults),
        })

        payload = self._version.create(method='POST', uri=self._uri, data=data, )

        return AssistantInstance(self._version, payload, )

    def get(self, sid):
        """
        Constructs a AssistantContext

        :param sid: The unique string that identifies the resource

        :returns: twilio.rest.autopilot.v1.assistant.AssistantContext
        :rtype: twilio.rest.autopilot.v1.assistant.AssistantContext
        """
        return AssistantContext(self._version, sid=sid, )

    def __call__(self, sid):
        """
        Constructs a AssistantContext

        :param sid: The unique string that identifies the resource

        :returns: twilio.rest.autopilot.v1.assistant.AssistantContext
        :rtype: twilio.rest.autopilot.v1.assistant.AssistantContext
        """
        return AssistantContext(self._version, sid=sid, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Autopilot.V1.AssistantList>'


class AssistantPage(Page):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, response, solution):
        """
        Initialize the AssistantPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API

        :returns: twilio.rest.autopilot.v1.assistant.AssistantPage
        :rtype: twilio.rest.autopilot.v1.assistant.AssistantPage
        """
        super(AssistantPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of AssistantInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.autopilot.v1.assistant.AssistantInstance
        :rtype: twilio.rest.autopilot.v1.assistant.AssistantInstance
        """
        return AssistantInstance(self._version, payload, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Autopilot.V1.AssistantPage>'


class AssistantContext(InstanceContext):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, sid):
        """
        Initialize the AssistantContext

        :param Version version: Version that contains the resource
        :param sid: The unique string that identifies the resource

        :returns: twilio.rest.autopilot.v1.assistant.AssistantContext
        :rtype: twilio.rest.autopilot.v1.assistant.AssistantContext
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
        self._style_sheet = None
        self._defaults = None
        self._dialogues = None
        self._webhooks = None
        self._export_assistant = None

    def fetch(self):
        """
        Fetch the AssistantInstance

        :returns: The fetched AssistantInstance
        :rtype: twilio.rest.autopilot.v1.assistant.AssistantInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return AssistantInstance(self._version, payload, sid=self._solution['sid'], )

    def update(self, friendly_name=values.unset, log_queries=values.unset,
               unique_name=values.unset, callback_url=values.unset,
               callback_events=values.unset, style_sheet=values.unset,
               defaults=values.unset, development_stage=values.unset):
        """
        Update the AssistantInstance

        :param unicode friendly_name: A string to describe the resource
        :param bool log_queries: Whether queries should be logged and kept after training
        :param unicode unique_name: An application-defined string that uniquely identifies the resource
        :param unicode callback_url: Reserved
        :param unicode callback_events: Reserved
        :param dict style_sheet: A JSON string that defines the Assistant's style sheet
        :param dict defaults: A JSON object that defines the Assistant's [default tasks](https://www.twilio.com/docs/autopilot/api/assistant/defaults) for various scenarios
        :param unicode development_stage: A string describing the state of the assistant.

        :returns: The updated AssistantInstance
        :rtype: twilio.rest.autopilot.v1.assistant.AssistantInstance
        """
        data = values.of({
            'FriendlyName': friendly_name,
            'LogQueries': log_queries,
            'UniqueName': unique_name,
            'CallbackUrl': callback_url,
            'CallbackEvents': callback_events,
            'StyleSheet': serialize.object(style_sheet),
            'Defaults': serialize.object(defaults),
            'DevelopmentStage': development_stage,
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

        :returns: twilio.rest.autopilot.v1.assistant.field_type.FieldTypeList
        :rtype: twilio.rest.autopilot.v1.assistant.field_type.FieldTypeList
        """
        if self._field_types is None:
            self._field_types = FieldTypeList(self._version, assistant_sid=self._solution['sid'], )
        return self._field_types

    @property
    def tasks(self):
        """
        Access the tasks

        :returns: twilio.rest.autopilot.v1.assistant.task.TaskList
        :rtype: twilio.rest.autopilot.v1.assistant.task.TaskList
        """
        if self._tasks is None:
            self._tasks = TaskList(self._version, assistant_sid=self._solution['sid'], )
        return self._tasks

    @property
    def model_builds(self):
        """
        Access the model_builds

        :returns: twilio.rest.autopilot.v1.assistant.model_build.ModelBuildList
        :rtype: twilio.rest.autopilot.v1.assistant.model_build.ModelBuildList
        """
        if self._model_builds is None:
            self._model_builds = ModelBuildList(self._version, assistant_sid=self._solution['sid'], )
        return self._model_builds

    @property
    def queries(self):
        """
        Access the queries

        :returns: twilio.rest.autopilot.v1.assistant.query.QueryList
        :rtype: twilio.rest.autopilot.v1.assistant.query.QueryList
        """
        if self._queries is None:
            self._queries = QueryList(self._version, assistant_sid=self._solution['sid'], )
        return self._queries

    @property
    def style_sheet(self):
        """
        Access the style_sheet

        :returns: twilio.rest.autopilot.v1.assistant.style_sheet.StyleSheetList
        :rtype: twilio.rest.autopilot.v1.assistant.style_sheet.StyleSheetList
        """
        if self._style_sheet is None:
            self._style_sheet = StyleSheetList(self._version, assistant_sid=self._solution['sid'], )
        return self._style_sheet

    @property
    def defaults(self):
        """
        Access the defaults

        :returns: twilio.rest.autopilot.v1.assistant.defaults.DefaultsList
        :rtype: twilio.rest.autopilot.v1.assistant.defaults.DefaultsList
        """
        if self._defaults is None:
            self._defaults = DefaultsList(self._version, assistant_sid=self._solution['sid'], )
        return self._defaults

    @property
    def dialogues(self):
        """
        Access the dialogues

        :returns: twilio.rest.autopilot.v1.assistant.dialogue.DialogueList
        :rtype: twilio.rest.autopilot.v1.assistant.dialogue.DialogueList
        """
        if self._dialogues is None:
            self._dialogues = DialogueList(self._version, assistant_sid=self._solution['sid'], )
        return self._dialogues

    @property
    def webhooks(self):
        """
        Access the webhooks

        :returns: twilio.rest.autopilot.v1.assistant.webhook.WebhookList
        :rtype: twilio.rest.autopilot.v1.assistant.webhook.WebhookList
        """
        if self._webhooks is None:
            self._webhooks = WebhookList(self._version, assistant_sid=self._solution['sid'], )
        return self._webhooks

    @property
    def export_assistant(self):
        """
        Access the export_assistant

        :returns: twilio.rest.autopilot.v1.assistant.export_assistant.ExportAssistantList
        :rtype: twilio.rest.autopilot.v1.assistant.export_assistant.ExportAssistantList
        """
        if self._export_assistant is None:
            self._export_assistant = ExportAssistantList(self._version, assistant_sid=self._solution['sid'], )
        return self._export_assistant

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Autopilot.V1.AssistantContext {}>'.format(context)


class AssistantInstance(InstanceResource):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, payload, sid=None):
        """
        Initialize the AssistantInstance

        :returns: twilio.rest.autopilot.v1.assistant.AssistantInstance
        :rtype: twilio.rest.autopilot.v1.assistant.AssistantInstance
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
            'development_stage': payload.get('development_stage'),
            'needs_model_build': payload.get('needs_model_build'),
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
        :rtype: twilio.rest.autopilot.v1.assistant.AssistantContext
        """
        if self._context is None:
            self._context = AssistantContext(self._version, sid=self._solution['sid'], )
        return self._context

    @property
    def account_sid(self):
        """
        :returns: The SID of the Account that created the resource
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def date_created(self):
        """
        :returns: The RFC 2822 date and time in GMT when the resource was created
        :rtype: datetime
        """
        return self._properties['date_created']

    @property
    def date_updated(self):
        """
        :returns: The RFC 2822 date and time in GMT when the resource was last updated
        :rtype: datetime
        """
        return self._properties['date_updated']

    @property
    def friendly_name(self):
        """
        :returns: The string that you assigned to describe the resource
        :rtype: unicode
        """
        return self._properties['friendly_name']

    @property
    def latest_model_build_sid(self):
        """
        :returns: Reserved
        :rtype: unicode
        """
        return self._properties['latest_model_build_sid']

    @property
    def links(self):
        """
        :returns: A list of the URLs of the Assistant's related resources
        :rtype: unicode
        """
        return self._properties['links']

    @property
    def log_queries(self):
        """
        :returns: Whether queries should be logged and kept after training
        :rtype: bool
        """
        return self._properties['log_queries']

    @property
    def development_stage(self):
        """
        :returns: A string describing the state of the assistant.
        :rtype: unicode
        """
        return self._properties['development_stage']

    @property
    def needs_model_build(self):
        """
        :returns: Whether model needs to be rebuilt
        :rtype: bool
        """
        return self._properties['needs_model_build']

    @property
    def sid(self):
        """
        :returns: The unique string that identifies the resource
        :rtype: unicode
        """
        return self._properties['sid']

    @property
    def unique_name(self):
        """
        :returns: An application-defined string that uniquely identifies the resource
        :rtype: unicode
        """
        return self._properties['unique_name']

    @property
    def url(self):
        """
        :returns: The absolute URL of the Assistant resource
        :rtype: unicode
        """
        return self._properties['url']

    @property
    def callback_url(self):
        """
        :returns: Reserved
        :rtype: unicode
        """
        return self._properties['callback_url']

    @property
    def callback_events(self):
        """
        :returns: Reserved
        :rtype: unicode
        """
        return self._properties['callback_events']

    def fetch(self):
        """
        Fetch the AssistantInstance

        :returns: The fetched AssistantInstance
        :rtype: twilio.rest.autopilot.v1.assistant.AssistantInstance
        """
        return self._proxy.fetch()

    def update(self, friendly_name=values.unset, log_queries=values.unset,
               unique_name=values.unset, callback_url=values.unset,
               callback_events=values.unset, style_sheet=values.unset,
               defaults=values.unset, development_stage=values.unset):
        """
        Update the AssistantInstance

        :param unicode friendly_name: A string to describe the resource
        :param bool log_queries: Whether queries should be logged and kept after training
        :param unicode unique_name: An application-defined string that uniquely identifies the resource
        :param unicode callback_url: Reserved
        :param unicode callback_events: Reserved
        :param dict style_sheet: A JSON string that defines the Assistant's style sheet
        :param dict defaults: A JSON object that defines the Assistant's [default tasks](https://www.twilio.com/docs/autopilot/api/assistant/defaults) for various scenarios
        :param unicode development_stage: A string describing the state of the assistant.

        :returns: The updated AssistantInstance
        :rtype: twilio.rest.autopilot.v1.assistant.AssistantInstance
        """
        return self._proxy.update(
            friendly_name=friendly_name,
            log_queries=log_queries,
            unique_name=unique_name,
            callback_url=callback_url,
            callback_events=callback_events,
            style_sheet=style_sheet,
            defaults=defaults,
            development_stage=development_stage,
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

        :returns: twilio.rest.autopilot.v1.assistant.field_type.FieldTypeList
        :rtype: twilio.rest.autopilot.v1.assistant.field_type.FieldTypeList
        """
        return self._proxy.field_types

    @property
    def tasks(self):
        """
        Access the tasks

        :returns: twilio.rest.autopilot.v1.assistant.task.TaskList
        :rtype: twilio.rest.autopilot.v1.assistant.task.TaskList
        """
        return self._proxy.tasks

    @property
    def model_builds(self):
        """
        Access the model_builds

        :returns: twilio.rest.autopilot.v1.assistant.model_build.ModelBuildList
        :rtype: twilio.rest.autopilot.v1.assistant.model_build.ModelBuildList
        """
        return self._proxy.model_builds

    @property
    def queries(self):
        """
        Access the queries

        :returns: twilio.rest.autopilot.v1.assistant.query.QueryList
        :rtype: twilio.rest.autopilot.v1.assistant.query.QueryList
        """
        return self._proxy.queries

    @property
    def style_sheet(self):
        """
        Access the style_sheet

        :returns: twilio.rest.autopilot.v1.assistant.style_sheet.StyleSheetList
        :rtype: twilio.rest.autopilot.v1.assistant.style_sheet.StyleSheetList
        """
        return self._proxy.style_sheet

    @property
    def defaults(self):
        """
        Access the defaults

        :returns: twilio.rest.autopilot.v1.assistant.defaults.DefaultsList
        :rtype: twilio.rest.autopilot.v1.assistant.defaults.DefaultsList
        """
        return self._proxy.defaults

    @property
    def dialogues(self):
        """
        Access the dialogues

        :returns: twilio.rest.autopilot.v1.assistant.dialogue.DialogueList
        :rtype: twilio.rest.autopilot.v1.assistant.dialogue.DialogueList
        """
        return self._proxy.dialogues

    @property
    def webhooks(self):
        """
        Access the webhooks

        :returns: twilio.rest.autopilot.v1.assistant.webhook.WebhookList
        :rtype: twilio.rest.autopilot.v1.assistant.webhook.WebhookList
        """
        return self._proxy.webhooks

    @property
    def export_assistant(self):
        """
        Access the export_assistant

        :returns: twilio.rest.autopilot.v1.assistant.export_assistant.ExportAssistantList
        :rtype: twilio.rest.autopilot.v1.assistant.export_assistant.ExportAssistantList
        """
        return self._proxy.export_assistant

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Autopilot.V1.AssistantInstance {}>'.format(context)
