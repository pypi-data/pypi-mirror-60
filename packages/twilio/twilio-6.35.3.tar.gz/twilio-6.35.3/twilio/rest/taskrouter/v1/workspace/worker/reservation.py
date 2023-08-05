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


class ReservationList(ListResource):
    """  """

    def __init__(self, version, workspace_sid, worker_sid):
        """
        Initialize the ReservationList

        :param Version version: Version that contains the resource
        :param workspace_sid: The SID of the Workspace that this worker is contained within.
        :param worker_sid: The SID of the reserved Worker resource

        :returns: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationList
        :rtype: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationList
        """
        super(ReservationList, self).__init__(version)

        # Path Solution
        self._solution = {'workspace_sid': workspace_sid, 'worker_sid': worker_sid, }
        self._uri = '/Workspaces/{workspace_sid}/Workers/{worker_sid}/Reservations'.format(**self._solution)

    def stream(self, reservation_status=values.unset, limit=None, page_size=None):
        """
        Streams ReservationInstance records from the API as a generator stream.
        This operation lazily loads records as efficiently as possible until the limit
        is reached.
        The results are returned as a generator, so this operation is memory efficient.

        :param ReservationInstance.Status reservation_status: Returns the list of reservations for a worker with a specified ReservationStatus
        :param int limit: Upper limit for the number of records to return. stream()
                          guarantees to never return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, stream() will attempt to read the
                              limit with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(reservation_status=reservation_status, page_size=limits['page_size'], )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, reservation_status=values.unset, limit=None, page_size=None):
        """
        Lists ReservationInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param ReservationInstance.Status reservation_status: Returns the list of reservations for a worker with a specified ReservationStatus
        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationInstance]
        """
        return list(self.stream(reservation_status=reservation_status, limit=limit, page_size=page_size, ))

    def page(self, reservation_status=values.unset, page_token=values.unset,
             page_number=values.unset, page_size=values.unset):
        """
        Retrieve a single page of ReservationInstance records from the API.
        Request is executed immediately

        :param ReservationInstance.Status reservation_status: Returns the list of reservations for a worker with a specified ReservationStatus
        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of ReservationInstance
        :rtype: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationPage
        """
        data = values.of({
            'ReservationStatus': reservation_status,
            'PageToken': page_token,
            'Page': page_number,
            'PageSize': page_size,
        })

        response = self._version.page(method='GET', uri=self._uri, params=data, )

        return ReservationPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of ReservationInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of ReservationInstance
        :rtype: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return ReservationPage(self._version, response, self._solution)

    def get(self, sid):
        """
        Constructs a ReservationContext

        :param sid: The SID of the WorkerReservation resource to fetch

        :returns: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationContext
        :rtype: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationContext
        """
        return ReservationContext(
            self._version,
            workspace_sid=self._solution['workspace_sid'],
            worker_sid=self._solution['worker_sid'],
            sid=sid,
        )

    def __call__(self, sid):
        """
        Constructs a ReservationContext

        :param sid: The SID of the WorkerReservation resource to fetch

        :returns: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationContext
        :rtype: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationContext
        """
        return ReservationContext(
            self._version,
            workspace_sid=self._solution['workspace_sid'],
            worker_sid=self._solution['worker_sid'],
            sid=sid,
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Taskrouter.V1.ReservationList>'


class ReservationPage(Page):
    """  """

    def __init__(self, version, response, solution):
        """
        Initialize the ReservationPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API
        :param workspace_sid: The SID of the Workspace that this worker is contained within.
        :param worker_sid: The SID of the reserved Worker resource

        :returns: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationPage
        :rtype: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationPage
        """
        super(ReservationPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of ReservationInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationInstance
        :rtype: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationInstance
        """
        return ReservationInstance(
            self._version,
            payload,
            workspace_sid=self._solution['workspace_sid'],
            worker_sid=self._solution['worker_sid'],
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Taskrouter.V1.ReservationPage>'


class ReservationContext(InstanceContext):
    """  """

    def __init__(self, version, workspace_sid, worker_sid, sid):
        """
        Initialize the ReservationContext

        :param Version version: Version that contains the resource
        :param workspace_sid: The SID of the Workspace with the WorkerReservation resource to fetch
        :param worker_sid: The SID of the reserved Worker resource with the WorkerReservation resource to fetch
        :param sid: The SID of the WorkerReservation resource to fetch

        :returns: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationContext
        :rtype: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationContext
        """
        super(ReservationContext, self).__init__(version)

        # Path Solution
        self._solution = {'workspace_sid': workspace_sid, 'worker_sid': worker_sid, 'sid': sid, }
        self._uri = '/Workspaces/{workspace_sid}/Workers/{worker_sid}/Reservations/{sid}'.format(**self._solution)

    def fetch(self):
        """
        Fetch the ReservationInstance

        :returns: The fetched ReservationInstance
        :rtype: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return ReservationInstance(
            self._version,
            payload,
            workspace_sid=self._solution['workspace_sid'],
            worker_sid=self._solution['worker_sid'],
            sid=self._solution['sid'],
        )

    def update(self, reservation_status=values.unset,
               worker_activity_sid=values.unset, instruction=values.unset,
               dequeue_post_work_activity_sid=values.unset,
               dequeue_from=values.unset, dequeue_record=values.unset,
               dequeue_timeout=values.unset, dequeue_to=values.unset,
               dequeue_status_callback_url=values.unset, call_from=values.unset,
               call_record=values.unset, call_timeout=values.unset,
               call_to=values.unset, call_url=values.unset,
               call_status_callback_url=values.unset, call_accept=values.unset,
               redirect_call_sid=values.unset, redirect_accept=values.unset,
               redirect_url=values.unset, to=values.unset, from_=values.unset,
               status_callback=values.unset, status_callback_method=values.unset,
               status_callback_event=values.unset, timeout=values.unset,
               record=values.unset, muted=values.unset, beep=values.unset,
               start_conference_on_enter=values.unset,
               end_conference_on_exit=values.unset, wait_url=values.unset,
               wait_method=values.unset, early_media=values.unset,
               max_participants=values.unset,
               conference_status_callback=values.unset,
               conference_status_callback_method=values.unset,
               conference_status_callback_event=values.unset,
               conference_record=values.unset, conference_trim=values.unset,
               recording_channels=values.unset,
               recording_status_callback=values.unset,
               recording_status_callback_method=values.unset,
               conference_recording_status_callback=values.unset,
               conference_recording_status_callback_method=values.unset,
               region=values.unset, sip_auth_username=values.unset,
               sip_auth_password=values.unset,
               dequeue_status_callback_event=values.unset,
               post_work_activity_sid=values.unset,
               end_conference_on_customer_exit=values.unset,
               beep_on_customer_entrance=values.unset):
        """
        Update the ReservationInstance

        :param ReservationInstance.Status reservation_status: The new status of the reservation
        :param unicode worker_activity_sid: The new worker activity SID if rejecting a reservation
        :param unicode instruction: The assignment instruction for the reservation
        :param unicode dequeue_post_work_activity_sid: The SID of the Activity resource to start after executing a Dequeue instruction
        :param unicode dequeue_from: The caller ID of the call to the worker when executing a Dequeue instruction
        :param unicode dequeue_record: Whether to record both legs of a call when executing a Dequeue instruction
        :param unicode dequeue_timeout: The timeout for call when executing a Dequeue instruction
        :param unicode dequeue_to: The contact URI of the worker when executing a Dequeue instruction
        :param unicode dequeue_status_callback_url: The callback URL for completed call event when executing a Dequeue instruction
        :param unicode call_from: The Caller ID of the outbound call when executing a Call instruction
        :param unicode call_record: Whether to record both legs of a call when executing a Call instruction
        :param unicode call_timeout: The timeout for a call when executing a Call instruction
        :param unicode call_to: The contact URI of the worker when executing a Call instruction
        :param unicode call_url: TwiML URI executed on answering the worker's leg as a result of the Call instruction
        :param unicode call_status_callback_url: The URL to call for the completed call event when executing a Call instruction
        :param bool call_accept: Whether to accept a reservation when executing a Call instruction
        :param unicode redirect_call_sid: The Call SID of the call parked in the queue when executing a Redirect instruction
        :param bool redirect_accept: Whether the reservation should be accepted when executing a Redirect instruction
        :param unicode redirect_url: TwiML URI to redirect the call to when executing the Redirect instruction
        :param unicode to: The Contact URI of the worker when executing a Conference instruction
        :param unicode from_: The caller ID of the call to the worker when executing a Conference instruction
        :param unicode status_callback: The URL we should call to send status information to your application
        :param unicode status_callback_method: The HTTP method we should use to call status_callback
        :param ReservationInstance.CallStatus status_callback_event: The call progress events that we will send to status_callback
        :param unicode timeout: The timeout for a call when executing a Conference instruction
        :param bool record: Whether to record the participant and their conferences
        :param bool muted: Whether to mute the agent
        :param unicode beep: Whether to play a notification beep when the participant joins
        :param bool start_conference_on_enter: Whether the conference starts when the participant joins the conference
        :param bool end_conference_on_exit: Whether to end the conference when the agent leaves
        :param unicode wait_url: URL that hosts pre-conference hold music
        :param unicode wait_method: The HTTP method we should use to call `wait_url`
        :param bool early_media: Whether agents can hear the state of the outbound call
        :param unicode max_participants: The maximum number of agent conference participants
        :param unicode conference_status_callback: The callback URL for conference events
        :param unicode conference_status_callback_method: HTTP method for requesting `conference_status_callback` URL
        :param ReservationInstance.ConferenceEvent conference_status_callback_event: The conference status events that we will send to conference_status_callback
        :param unicode conference_record: Whether to record the conference the participant is joining
        :param unicode conference_trim: Whether to trim leading and trailing silence from your recorded conference audio files
        :param unicode recording_channels: Specify `mono` or `dual` recording channels
        :param unicode recording_status_callback: The URL that we should call using the `recording_status_callback_method` when the recording status changes
        :param unicode recording_status_callback_method: The HTTP method we should use when we call `recording_status_callback`
        :param unicode conference_recording_status_callback: The URL we should call using the `conference_recording_status_callback_method` when the conference recording is available
        :param unicode conference_recording_status_callback_method: The HTTP method we should use to call `conference_recording_status_callback`
        :param unicode region: The region where we should mix the conference audio
        :param unicode sip_auth_username: The SIP username used for authentication
        :param unicode sip_auth_password: The SIP password for authentication
        :param unicode dequeue_status_callback_event: The call progress events sent via webhooks as a result of a Dequeue instruction
        :param unicode post_work_activity_sid: The new worker activity SID after executing a Conference instruction
        :param bool end_conference_on_customer_exit: Whether to end the conference when the customer leaves
        :param bool beep_on_customer_entrance: Whether to play a notification beep when the customer joins

        :returns: The updated ReservationInstance
        :rtype: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationInstance
        """
        data = values.of({
            'ReservationStatus': reservation_status,
            'WorkerActivitySid': worker_activity_sid,
            'Instruction': instruction,
            'DequeuePostWorkActivitySid': dequeue_post_work_activity_sid,
            'DequeueFrom': dequeue_from,
            'DequeueRecord': dequeue_record,
            'DequeueTimeout': dequeue_timeout,
            'DequeueTo': dequeue_to,
            'DequeueStatusCallbackUrl': dequeue_status_callback_url,
            'CallFrom': call_from,
            'CallRecord': call_record,
            'CallTimeout': call_timeout,
            'CallTo': call_to,
            'CallUrl': call_url,
            'CallStatusCallbackUrl': call_status_callback_url,
            'CallAccept': call_accept,
            'RedirectCallSid': redirect_call_sid,
            'RedirectAccept': redirect_accept,
            'RedirectUrl': redirect_url,
            'To': to,
            'From': from_,
            'StatusCallback': status_callback,
            'StatusCallbackMethod': status_callback_method,
            'StatusCallbackEvent': serialize.map(status_callback_event, lambda e: e),
            'Timeout': timeout,
            'Record': record,
            'Muted': muted,
            'Beep': beep,
            'StartConferenceOnEnter': start_conference_on_enter,
            'EndConferenceOnExit': end_conference_on_exit,
            'WaitUrl': wait_url,
            'WaitMethod': wait_method,
            'EarlyMedia': early_media,
            'MaxParticipants': max_participants,
            'ConferenceStatusCallback': conference_status_callback,
            'ConferenceStatusCallbackMethod': conference_status_callback_method,
            'ConferenceStatusCallbackEvent': serialize.map(conference_status_callback_event, lambda e: e),
            'ConferenceRecord': conference_record,
            'ConferenceTrim': conference_trim,
            'RecordingChannels': recording_channels,
            'RecordingStatusCallback': recording_status_callback,
            'RecordingStatusCallbackMethod': recording_status_callback_method,
            'ConferenceRecordingStatusCallback': conference_recording_status_callback,
            'ConferenceRecordingStatusCallbackMethod': conference_recording_status_callback_method,
            'Region': region,
            'SipAuthUsername': sip_auth_username,
            'SipAuthPassword': sip_auth_password,
            'DequeueStatusCallbackEvent': serialize.map(dequeue_status_callback_event, lambda e: e),
            'PostWorkActivitySid': post_work_activity_sid,
            'EndConferenceOnCustomerExit': end_conference_on_customer_exit,
            'BeepOnCustomerEntrance': beep_on_customer_entrance,
        })

        payload = self._version.update(method='POST', uri=self._uri, data=data, )

        return ReservationInstance(
            self._version,
            payload,
            workspace_sid=self._solution['workspace_sid'],
            worker_sid=self._solution['worker_sid'],
            sid=self._solution['sid'],
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Taskrouter.V1.ReservationContext {}>'.format(context)


class ReservationInstance(InstanceResource):
    """  """

    class Status(object):
        PENDING = "pending"
        ACCEPTED = "accepted"
        REJECTED = "rejected"
        TIMEOUT = "timeout"
        CANCELED = "canceled"
        RESCINDED = "rescinded"
        WRAPPING = "wrapping"
        COMPLETED = "completed"

    class CallStatus(object):
        INITIATED = "initiated"
        RINGING = "ringing"
        ANSWERED = "answered"
        COMPLETED = "completed"

    class ConferenceEvent(object):
        START = "start"
        END = "end"
        JOIN = "join"
        LEAVE = "leave"
        MUTE = "mute"
        HOLD = "hold"
        SPEAKER = "speaker"

    def __init__(self, version, payload, workspace_sid, worker_sid, sid=None):
        """
        Initialize the ReservationInstance

        :returns: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationInstance
        :rtype: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationInstance
        """
        super(ReservationInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'account_sid': payload.get('account_sid'),
            'date_created': deserialize.iso8601_datetime(payload.get('date_created')),
            'date_updated': deserialize.iso8601_datetime(payload.get('date_updated')),
            'reservation_status': payload.get('reservation_status'),
            'sid': payload.get('sid'),
            'task_sid': payload.get('task_sid'),
            'worker_name': payload.get('worker_name'),
            'worker_sid': payload.get('worker_sid'),
            'workspace_sid': payload.get('workspace_sid'),
            'url': payload.get('url'),
            'links': payload.get('links'),
        }

        # Context
        self._context = None
        self._solution = {
            'workspace_sid': workspace_sid,
            'worker_sid': worker_sid,
            'sid': sid or self._properties['sid'],
        }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: ReservationContext for this ReservationInstance
        :rtype: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationContext
        """
        if self._context is None:
            self._context = ReservationContext(
                self._version,
                workspace_sid=self._solution['workspace_sid'],
                worker_sid=self._solution['worker_sid'],
                sid=self._solution['sid'],
            )
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
    def reservation_status(self):
        """
        :returns: The current status of the reservation
        :rtype: ReservationInstance.Status
        """
        return self._properties['reservation_status']

    @property
    def sid(self):
        """
        :returns: The unique string that identifies the resource
        :rtype: unicode
        """
        return self._properties['sid']

    @property
    def task_sid(self):
        """
        :returns: The SID of the reserved Task resource
        :rtype: unicode
        """
        return self._properties['task_sid']

    @property
    def worker_name(self):
        """
        :returns: The friendly_name of the Worker that is reserved
        :rtype: unicode
        """
        return self._properties['worker_name']

    @property
    def worker_sid(self):
        """
        :returns: The SID of the reserved Worker resource
        :rtype: unicode
        """
        return self._properties['worker_sid']

    @property
    def workspace_sid(self):
        """
        :returns: The SID of the Workspace that this worker is contained within.
        :rtype: unicode
        """
        return self._properties['workspace_sid']

    @property
    def url(self):
        """
        :returns: The absolute URL of the WorkerReservation resource
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

    def fetch(self):
        """
        Fetch the ReservationInstance

        :returns: The fetched ReservationInstance
        :rtype: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationInstance
        """
        return self._proxy.fetch()

    def update(self, reservation_status=values.unset,
               worker_activity_sid=values.unset, instruction=values.unset,
               dequeue_post_work_activity_sid=values.unset,
               dequeue_from=values.unset, dequeue_record=values.unset,
               dequeue_timeout=values.unset, dequeue_to=values.unset,
               dequeue_status_callback_url=values.unset, call_from=values.unset,
               call_record=values.unset, call_timeout=values.unset,
               call_to=values.unset, call_url=values.unset,
               call_status_callback_url=values.unset, call_accept=values.unset,
               redirect_call_sid=values.unset, redirect_accept=values.unset,
               redirect_url=values.unset, to=values.unset, from_=values.unset,
               status_callback=values.unset, status_callback_method=values.unset,
               status_callback_event=values.unset, timeout=values.unset,
               record=values.unset, muted=values.unset, beep=values.unset,
               start_conference_on_enter=values.unset,
               end_conference_on_exit=values.unset, wait_url=values.unset,
               wait_method=values.unset, early_media=values.unset,
               max_participants=values.unset,
               conference_status_callback=values.unset,
               conference_status_callback_method=values.unset,
               conference_status_callback_event=values.unset,
               conference_record=values.unset, conference_trim=values.unset,
               recording_channels=values.unset,
               recording_status_callback=values.unset,
               recording_status_callback_method=values.unset,
               conference_recording_status_callback=values.unset,
               conference_recording_status_callback_method=values.unset,
               region=values.unset, sip_auth_username=values.unset,
               sip_auth_password=values.unset,
               dequeue_status_callback_event=values.unset,
               post_work_activity_sid=values.unset,
               end_conference_on_customer_exit=values.unset,
               beep_on_customer_entrance=values.unset):
        """
        Update the ReservationInstance

        :param ReservationInstance.Status reservation_status: The new status of the reservation
        :param unicode worker_activity_sid: The new worker activity SID if rejecting a reservation
        :param unicode instruction: The assignment instruction for the reservation
        :param unicode dequeue_post_work_activity_sid: The SID of the Activity resource to start after executing a Dequeue instruction
        :param unicode dequeue_from: The caller ID of the call to the worker when executing a Dequeue instruction
        :param unicode dequeue_record: Whether to record both legs of a call when executing a Dequeue instruction
        :param unicode dequeue_timeout: The timeout for call when executing a Dequeue instruction
        :param unicode dequeue_to: The contact URI of the worker when executing a Dequeue instruction
        :param unicode dequeue_status_callback_url: The callback URL for completed call event when executing a Dequeue instruction
        :param unicode call_from: The Caller ID of the outbound call when executing a Call instruction
        :param unicode call_record: Whether to record both legs of a call when executing a Call instruction
        :param unicode call_timeout: The timeout for a call when executing a Call instruction
        :param unicode call_to: The contact URI of the worker when executing a Call instruction
        :param unicode call_url: TwiML URI executed on answering the worker's leg as a result of the Call instruction
        :param unicode call_status_callback_url: The URL to call for the completed call event when executing a Call instruction
        :param bool call_accept: Whether to accept a reservation when executing a Call instruction
        :param unicode redirect_call_sid: The Call SID of the call parked in the queue when executing a Redirect instruction
        :param bool redirect_accept: Whether the reservation should be accepted when executing a Redirect instruction
        :param unicode redirect_url: TwiML URI to redirect the call to when executing the Redirect instruction
        :param unicode to: The Contact URI of the worker when executing a Conference instruction
        :param unicode from_: The caller ID of the call to the worker when executing a Conference instruction
        :param unicode status_callback: The URL we should call to send status information to your application
        :param unicode status_callback_method: The HTTP method we should use to call status_callback
        :param ReservationInstance.CallStatus status_callback_event: The call progress events that we will send to status_callback
        :param unicode timeout: The timeout for a call when executing a Conference instruction
        :param bool record: Whether to record the participant and their conferences
        :param bool muted: Whether to mute the agent
        :param unicode beep: Whether to play a notification beep when the participant joins
        :param bool start_conference_on_enter: Whether the conference starts when the participant joins the conference
        :param bool end_conference_on_exit: Whether to end the conference when the agent leaves
        :param unicode wait_url: URL that hosts pre-conference hold music
        :param unicode wait_method: The HTTP method we should use to call `wait_url`
        :param bool early_media: Whether agents can hear the state of the outbound call
        :param unicode max_participants: The maximum number of agent conference participants
        :param unicode conference_status_callback: The callback URL for conference events
        :param unicode conference_status_callback_method: HTTP method for requesting `conference_status_callback` URL
        :param ReservationInstance.ConferenceEvent conference_status_callback_event: The conference status events that we will send to conference_status_callback
        :param unicode conference_record: Whether to record the conference the participant is joining
        :param unicode conference_trim: Whether to trim leading and trailing silence from your recorded conference audio files
        :param unicode recording_channels: Specify `mono` or `dual` recording channels
        :param unicode recording_status_callback: The URL that we should call using the `recording_status_callback_method` when the recording status changes
        :param unicode recording_status_callback_method: The HTTP method we should use when we call `recording_status_callback`
        :param unicode conference_recording_status_callback: The URL we should call using the `conference_recording_status_callback_method` when the conference recording is available
        :param unicode conference_recording_status_callback_method: The HTTP method we should use to call `conference_recording_status_callback`
        :param unicode region: The region where we should mix the conference audio
        :param unicode sip_auth_username: The SIP username used for authentication
        :param unicode sip_auth_password: The SIP password for authentication
        :param unicode dequeue_status_callback_event: The call progress events sent via webhooks as a result of a Dequeue instruction
        :param unicode post_work_activity_sid: The new worker activity SID after executing a Conference instruction
        :param bool end_conference_on_customer_exit: Whether to end the conference when the customer leaves
        :param bool beep_on_customer_entrance: Whether to play a notification beep when the customer joins

        :returns: The updated ReservationInstance
        :rtype: twilio.rest.taskrouter.v1.workspace.worker.reservation.ReservationInstance
        """
        return self._proxy.update(
            reservation_status=reservation_status,
            worker_activity_sid=worker_activity_sid,
            instruction=instruction,
            dequeue_post_work_activity_sid=dequeue_post_work_activity_sid,
            dequeue_from=dequeue_from,
            dequeue_record=dequeue_record,
            dequeue_timeout=dequeue_timeout,
            dequeue_to=dequeue_to,
            dequeue_status_callback_url=dequeue_status_callback_url,
            call_from=call_from,
            call_record=call_record,
            call_timeout=call_timeout,
            call_to=call_to,
            call_url=call_url,
            call_status_callback_url=call_status_callback_url,
            call_accept=call_accept,
            redirect_call_sid=redirect_call_sid,
            redirect_accept=redirect_accept,
            redirect_url=redirect_url,
            to=to,
            from_=from_,
            status_callback=status_callback,
            status_callback_method=status_callback_method,
            status_callback_event=status_callback_event,
            timeout=timeout,
            record=record,
            muted=muted,
            beep=beep,
            start_conference_on_enter=start_conference_on_enter,
            end_conference_on_exit=end_conference_on_exit,
            wait_url=wait_url,
            wait_method=wait_method,
            early_media=early_media,
            max_participants=max_participants,
            conference_status_callback=conference_status_callback,
            conference_status_callback_method=conference_status_callback_method,
            conference_status_callback_event=conference_status_callback_event,
            conference_record=conference_record,
            conference_trim=conference_trim,
            recording_channels=recording_channels,
            recording_status_callback=recording_status_callback,
            recording_status_callback_method=recording_status_callback_method,
            conference_recording_status_callback=conference_recording_status_callback,
            conference_recording_status_callback_method=conference_recording_status_callback_method,
            region=region,
            sip_auth_username=sip_auth_username,
            sip_auth_password=sip_auth_password,
            dequeue_status_callback_event=dequeue_status_callback_event,
            post_work_activity_sid=post_work_activity_sid,
            end_conference_on_customer_exit=end_conference_on_customer_exit,
            beep_on_customer_entrance=beep_on_customer_entrance,
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Taskrouter.V1.ReservationInstance {}>'.format(context)
