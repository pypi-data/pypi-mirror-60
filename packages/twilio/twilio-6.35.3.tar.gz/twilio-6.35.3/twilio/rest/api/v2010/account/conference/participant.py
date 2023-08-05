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


class ParticipantList(ListResource):
    """  """

    def __init__(self, version, account_sid, conference_sid):
        """
        Initialize the ParticipantList

        :param Version version: Version that contains the resource
        :param account_sid: The SID of the Account that created the resource
        :param conference_sid: The SID of the conference the participant is in

        :returns: twilio.rest.api.v2010.account.conference.participant.ParticipantList
        :rtype: twilio.rest.api.v2010.account.conference.participant.ParticipantList
        """
        super(ParticipantList, self).__init__(version)

        # Path Solution
        self._solution = {'account_sid': account_sid, 'conference_sid': conference_sid, }
        self._uri = '/Accounts/{account_sid}/Conferences/{conference_sid}/Participants.json'.format(**self._solution)

    def create(self, from_, to, status_callback=values.unset,
               status_callback_method=values.unset,
               status_callback_event=values.unset, timeout=values.unset,
               record=values.unset, muted=values.unset, beep=values.unset,
               start_conference_on_enter=values.unset,
               end_conference_on_exit=values.unset, wait_url=values.unset,
               wait_method=values.unset, early_media=values.unset,
               max_participants=values.unset, conference_record=values.unset,
               conference_trim=values.unset,
               conference_status_callback=values.unset,
               conference_status_callback_method=values.unset,
               conference_status_callback_event=values.unset,
               recording_channels=values.unset,
               recording_status_callback=values.unset,
               recording_status_callback_method=values.unset,
               sip_auth_username=values.unset, sip_auth_password=values.unset,
               region=values.unset,
               conference_recording_status_callback=values.unset,
               conference_recording_status_callback_method=values.unset,
               recording_status_callback_event=values.unset,
               conference_recording_status_callback_event=values.unset,
               coaching=values.unset, call_sid_to_coach=values.unset):
        """
        Create the ParticipantInstance

        :param unicode from_: The `from` phone number used to invite a participant
        :param unicode to: The number, client id, or sip address of the new participant
        :param unicode status_callback: The URL we should call to send status information to your application
        :param unicode status_callback_method: The HTTP method we should use to call `status_callback`
        :param unicode status_callback_event: Set state change events that will trigger a callback
        :param unicode timeout: he number of seconds that we should wait for an answer
        :param bool record: Whether to record the participant and their conferences
        :param bool muted: Whether to mute the agent
        :param unicode beep: Whether to play a notification beep to the conference when the participant joins
        :param bool start_conference_on_enter: Whether the conference starts when the participant joins the conference
        :param bool end_conference_on_exit: Whether to end the conference when the participant leaves
        :param unicode wait_url: URL that hosts pre-conference hold music
        :param unicode wait_method: The HTTP method we should use to call `wait_url`
        :param bool early_media: Whether agents can hear the state of the outbound call
        :param unicode max_participants: The maximum number of agent conference participants
        :param unicode conference_record: Whether to record the conference the participant is joining
        :param unicode conference_trim: Whether to trim leading and trailing silence from your recorded conference audio files
        :param unicode conference_status_callback: The callback URL for conference events
        :param unicode conference_status_callback_method: HTTP method for requesting `conference_status_callback` URL
        :param unicode conference_status_callback_event: The conference state changes that should generate a call to `conference_status_callback`
        :param unicode recording_channels: Specify `mono` or `dual` recording channels
        :param unicode recording_status_callback: The URL that we should call using the `recording_status_callback_method` when the recording status changes
        :param unicode recording_status_callback_method: The HTTP method we should use when we call `recording_status_callback`
        :param unicode sip_auth_username: The SIP username used for authentication
        :param unicode sip_auth_password: The SIP password for authentication
        :param unicode region: The region where we should mix the conference audio
        :param unicode conference_recording_status_callback: The URL we should call using the `conference_recording_status_callback_method` when the conference recording is available
        :param unicode conference_recording_status_callback_method: The HTTP method we should use to call `conference_recording_status_callback`
        :param unicode recording_status_callback_event: The recording state changes that should generate a call to `recording_status_callback`
        :param unicode conference_recording_status_callback_event: The conference recording state changes that should generate a call to `conference_recording_status_callback`
        :param bool coaching: Indicates if the participant changed to coach
        :param unicode call_sid_to_coach: The SID of the participant who is being `coached`

        :returns: The created ParticipantInstance
        :rtype: twilio.rest.api.v2010.account.conference.participant.ParticipantInstance
        """
        data = values.of({
            'From': from_,
            'To': to,
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
            'ConferenceRecord': conference_record,
            'ConferenceTrim': conference_trim,
            'ConferenceStatusCallback': conference_status_callback,
            'ConferenceStatusCallbackMethod': conference_status_callback_method,
            'ConferenceStatusCallbackEvent': serialize.map(conference_status_callback_event, lambda e: e),
            'RecordingChannels': recording_channels,
            'RecordingStatusCallback': recording_status_callback,
            'RecordingStatusCallbackMethod': recording_status_callback_method,
            'SipAuthUsername': sip_auth_username,
            'SipAuthPassword': sip_auth_password,
            'Region': region,
            'ConferenceRecordingStatusCallback': conference_recording_status_callback,
            'ConferenceRecordingStatusCallbackMethod': conference_recording_status_callback_method,
            'RecordingStatusCallbackEvent': serialize.map(recording_status_callback_event, lambda e: e),
            'ConferenceRecordingStatusCallbackEvent': serialize.map(conference_recording_status_callback_event, lambda e: e),
            'Coaching': coaching,
            'CallSidToCoach': call_sid_to_coach,
        })

        payload = self._version.create(method='POST', uri=self._uri, data=data, )

        return ParticipantInstance(
            self._version,
            payload,
            account_sid=self._solution['account_sid'],
            conference_sid=self._solution['conference_sid'],
        )

    def stream(self, muted=values.unset, hold=values.unset, coaching=values.unset,
               limit=None, page_size=None):
        """
        Streams ParticipantInstance records from the API as a generator stream.
        This operation lazily loads records as efficiently as possible until the limit
        is reached.
        The results are returned as a generator, so this operation is memory efficient.

        :param bool muted: Whether to return only participants that are muted
        :param bool hold: Whether to return only participants that are on hold
        :param bool coaching: Whether to return only participants who are coaching another call
        :param int limit: Upper limit for the number of records to return. stream()
                          guarantees to never return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, stream() will attempt to read the
                              limit with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.api.v2010.account.conference.participant.ParticipantInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(muted=muted, hold=hold, coaching=coaching, page_size=limits['page_size'], )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, muted=values.unset, hold=values.unset, coaching=values.unset,
             limit=None, page_size=None):
        """
        Lists ParticipantInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param bool muted: Whether to return only participants that are muted
        :param bool hold: Whether to return only participants that are on hold
        :param bool coaching: Whether to return only participants who are coaching another call
        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.api.v2010.account.conference.participant.ParticipantInstance]
        """
        return list(self.stream(
            muted=muted,
            hold=hold,
            coaching=coaching,
            limit=limit,
            page_size=page_size,
        ))

    def page(self, muted=values.unset, hold=values.unset, coaching=values.unset,
             page_token=values.unset, page_number=values.unset,
             page_size=values.unset):
        """
        Retrieve a single page of ParticipantInstance records from the API.
        Request is executed immediately

        :param bool muted: Whether to return only participants that are muted
        :param bool hold: Whether to return only participants that are on hold
        :param bool coaching: Whether to return only participants who are coaching another call
        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of ParticipantInstance
        :rtype: twilio.rest.api.v2010.account.conference.participant.ParticipantPage
        """
        data = values.of({
            'Muted': muted,
            'Hold': hold,
            'Coaching': coaching,
            'PageToken': page_token,
            'Page': page_number,
            'PageSize': page_size,
        })

        response = self._version.page(method='GET', uri=self._uri, params=data, )

        return ParticipantPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of ParticipantInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of ParticipantInstance
        :rtype: twilio.rest.api.v2010.account.conference.participant.ParticipantPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return ParticipantPage(self._version, response, self._solution)

    def get(self, call_sid):
        """
        Constructs a ParticipantContext

        :param call_sid: The Call SID of the resource to fetch

        :returns: twilio.rest.api.v2010.account.conference.participant.ParticipantContext
        :rtype: twilio.rest.api.v2010.account.conference.participant.ParticipantContext
        """
        return ParticipantContext(
            self._version,
            account_sid=self._solution['account_sid'],
            conference_sid=self._solution['conference_sid'],
            call_sid=call_sid,
        )

    def __call__(self, call_sid):
        """
        Constructs a ParticipantContext

        :param call_sid: The Call SID of the resource to fetch

        :returns: twilio.rest.api.v2010.account.conference.participant.ParticipantContext
        :rtype: twilio.rest.api.v2010.account.conference.participant.ParticipantContext
        """
        return ParticipantContext(
            self._version,
            account_sid=self._solution['account_sid'],
            conference_sid=self._solution['conference_sid'],
            call_sid=call_sid,
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Api.V2010.ParticipantList>'


class ParticipantPage(Page):
    """  """

    def __init__(self, version, response, solution):
        """
        Initialize the ParticipantPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API
        :param account_sid: The SID of the Account that created the resource
        :param conference_sid: The SID of the conference the participant is in

        :returns: twilio.rest.api.v2010.account.conference.participant.ParticipantPage
        :rtype: twilio.rest.api.v2010.account.conference.participant.ParticipantPage
        """
        super(ParticipantPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of ParticipantInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.api.v2010.account.conference.participant.ParticipantInstance
        :rtype: twilio.rest.api.v2010.account.conference.participant.ParticipantInstance
        """
        return ParticipantInstance(
            self._version,
            payload,
            account_sid=self._solution['account_sid'],
            conference_sid=self._solution['conference_sid'],
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Api.V2010.ParticipantPage>'


class ParticipantContext(InstanceContext):
    """  """

    def __init__(self, version, account_sid, conference_sid, call_sid):
        """
        Initialize the ParticipantContext

        :param Version version: Version that contains the resource
        :param account_sid: The SID of the Account that created the resource to fetch
        :param conference_sid: The SID of the conference with the participant to fetch
        :param call_sid: The Call SID of the resource to fetch

        :returns: twilio.rest.api.v2010.account.conference.participant.ParticipantContext
        :rtype: twilio.rest.api.v2010.account.conference.participant.ParticipantContext
        """
        super(ParticipantContext, self).__init__(version)

        # Path Solution
        self._solution = {
            'account_sid': account_sid,
            'conference_sid': conference_sid,
            'call_sid': call_sid,
        }
        self._uri = '/Accounts/{account_sid}/Conferences/{conference_sid}/Participants/{call_sid}.json'.format(**self._solution)

    def fetch(self):
        """
        Fetch the ParticipantInstance

        :returns: The fetched ParticipantInstance
        :rtype: twilio.rest.api.v2010.account.conference.participant.ParticipantInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return ParticipantInstance(
            self._version,
            payload,
            account_sid=self._solution['account_sid'],
            conference_sid=self._solution['conference_sid'],
            call_sid=self._solution['call_sid'],
        )

    def update(self, muted=values.unset, hold=values.unset, hold_url=values.unset,
               hold_method=values.unset, announce_url=values.unset,
               announce_method=values.unset, wait_url=values.unset,
               wait_method=values.unset, beep_on_exit=values.unset,
               end_conference_on_exit=values.unset, coaching=values.unset,
               call_sid_to_coach=values.unset):
        """
        Update the ParticipantInstance

        :param bool muted: Whether the participant should be muted
        :param bool hold: Whether the participant should be on hold
        :param unicode hold_url: The URL we call using the `hold_method` for  music that plays when the participant is on hold
        :param unicode hold_method: The HTTP method we should use to call hold_url
        :param unicode announce_url: The URL we call using the `announce_method` for an announcement to the participant
        :param unicode announce_method: The HTTP method we should use to call announce_url
        :param unicode wait_url: URL that hosts pre-conference hold music
        :param unicode wait_method: The HTTP method we should use to call `wait_url`
        :param bool beep_on_exit: Whether to play a notification beep to the conference when the participant exit
        :param bool end_conference_on_exit: Whether to end the conference when the participant leaves
        :param bool coaching: Indicates if the participant changed to coach
        :param unicode call_sid_to_coach: The SID of the participant who is being `coached`

        :returns: The updated ParticipantInstance
        :rtype: twilio.rest.api.v2010.account.conference.participant.ParticipantInstance
        """
        data = values.of({
            'Muted': muted,
            'Hold': hold,
            'HoldUrl': hold_url,
            'HoldMethod': hold_method,
            'AnnounceUrl': announce_url,
            'AnnounceMethod': announce_method,
            'WaitUrl': wait_url,
            'WaitMethod': wait_method,
            'BeepOnExit': beep_on_exit,
            'EndConferenceOnExit': end_conference_on_exit,
            'Coaching': coaching,
            'CallSidToCoach': call_sid_to_coach,
        })

        payload = self._version.update(method='POST', uri=self._uri, data=data, )

        return ParticipantInstance(
            self._version,
            payload,
            account_sid=self._solution['account_sid'],
            conference_sid=self._solution['conference_sid'],
            call_sid=self._solution['call_sid'],
        )

    def delete(self):
        """
        Deletes the ParticipantInstance

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
        return '<Twilio.Api.V2010.ParticipantContext {}>'.format(context)


class ParticipantInstance(InstanceResource):
    """  """

    class Status(object):
        QUEUED = "queued"
        CONNECTING = "connecting"
        RINGING = "ringing"
        CONNECTED = "connected"
        COMPLETE = "complete"
        FAILED = "failed"

    def __init__(self, version, payload, account_sid, conference_sid,
                 call_sid=None):
        """
        Initialize the ParticipantInstance

        :returns: twilio.rest.api.v2010.account.conference.participant.ParticipantInstance
        :rtype: twilio.rest.api.v2010.account.conference.participant.ParticipantInstance
        """
        super(ParticipantInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'account_sid': payload.get('account_sid'),
            'call_sid': payload.get('call_sid'),
            'call_sid_to_coach': payload.get('call_sid_to_coach'),
            'coaching': payload.get('coaching'),
            'conference_sid': payload.get('conference_sid'),
            'date_created': deserialize.rfc2822_datetime(payload.get('date_created')),
            'date_updated': deserialize.rfc2822_datetime(payload.get('date_updated')),
            'end_conference_on_exit': payload.get('end_conference_on_exit'),
            'muted': payload.get('muted'),
            'hold': payload.get('hold'),
            'start_conference_on_enter': payload.get('start_conference_on_enter'),
            'status': payload.get('status'),
            'uri': payload.get('uri'),
        }

        # Context
        self._context = None
        self._solution = {
            'account_sid': account_sid,
            'conference_sid': conference_sid,
            'call_sid': call_sid or self._properties['call_sid'],
        }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: ParticipantContext for this ParticipantInstance
        :rtype: twilio.rest.api.v2010.account.conference.participant.ParticipantContext
        """
        if self._context is None:
            self._context = ParticipantContext(
                self._version,
                account_sid=self._solution['account_sid'],
                conference_sid=self._solution['conference_sid'],
                call_sid=self._solution['call_sid'],
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
    def call_sid(self):
        """
        :returns: The SID of the Call the resource is associated with
        :rtype: unicode
        """
        return self._properties['call_sid']

    @property
    def call_sid_to_coach(self):
        """
        :returns: The SID of the participant who is being `coached`
        :rtype: unicode
        """
        return self._properties['call_sid_to_coach']

    @property
    def coaching(self):
        """
        :returns: Indicates if the participant changed to coach
        :rtype: bool
        """
        return self._properties['coaching']

    @property
    def conference_sid(self):
        """
        :returns: The SID of the conference the participant is in
        :rtype: unicode
        """
        return self._properties['conference_sid']

    @property
    def date_created(self):
        """
        :returns: The RFC 2822 date and time in GMT that the resource was created
        :rtype: datetime
        """
        return self._properties['date_created']

    @property
    def date_updated(self):
        """
        :returns: The RFC 2822 date and time in GMT that the resource was last updated
        :rtype: datetime
        """
        return self._properties['date_updated']

    @property
    def end_conference_on_exit(self):
        """
        :returns: Whether the conference ends when the participant leaves
        :rtype: bool
        """
        return self._properties['end_conference_on_exit']

    @property
    def muted(self):
        """
        :returns: Whether the participant is muted
        :rtype: bool
        """
        return self._properties['muted']

    @property
    def hold(self):
        """
        :returns: Whether the participant is on hold
        :rtype: bool
        """
        return self._properties['hold']

    @property
    def start_conference_on_enter(self):
        """
        :returns: Whether the conference starts when the participant joins the conference
        :rtype: bool
        """
        return self._properties['start_conference_on_enter']

    @property
    def status(self):
        """
        :returns: The status of the participant's call in a session
        :rtype: ParticipantInstance.Status
        """
        return self._properties['status']

    @property
    def uri(self):
        """
        :returns: The URI of the resource, relative to `https://api.twilio.com`
        :rtype: unicode
        """
        return self._properties['uri']

    def fetch(self):
        """
        Fetch the ParticipantInstance

        :returns: The fetched ParticipantInstance
        :rtype: twilio.rest.api.v2010.account.conference.participant.ParticipantInstance
        """
        return self._proxy.fetch()

    def update(self, muted=values.unset, hold=values.unset, hold_url=values.unset,
               hold_method=values.unset, announce_url=values.unset,
               announce_method=values.unset, wait_url=values.unset,
               wait_method=values.unset, beep_on_exit=values.unset,
               end_conference_on_exit=values.unset, coaching=values.unset,
               call_sid_to_coach=values.unset):
        """
        Update the ParticipantInstance

        :param bool muted: Whether the participant should be muted
        :param bool hold: Whether the participant should be on hold
        :param unicode hold_url: The URL we call using the `hold_method` for  music that plays when the participant is on hold
        :param unicode hold_method: The HTTP method we should use to call hold_url
        :param unicode announce_url: The URL we call using the `announce_method` for an announcement to the participant
        :param unicode announce_method: The HTTP method we should use to call announce_url
        :param unicode wait_url: URL that hosts pre-conference hold music
        :param unicode wait_method: The HTTP method we should use to call `wait_url`
        :param bool beep_on_exit: Whether to play a notification beep to the conference when the participant exit
        :param bool end_conference_on_exit: Whether to end the conference when the participant leaves
        :param bool coaching: Indicates if the participant changed to coach
        :param unicode call_sid_to_coach: The SID of the participant who is being `coached`

        :returns: The updated ParticipantInstance
        :rtype: twilio.rest.api.v2010.account.conference.participant.ParticipantInstance
        """
        return self._proxy.update(
            muted=muted,
            hold=hold,
            hold_url=hold_url,
            hold_method=hold_method,
            announce_url=announce_url,
            announce_method=announce_method,
            wait_url=wait_url,
            wait_method=wait_method,
            beep_on_exit=beep_on_exit,
            end_conference_on_exit=end_conference_on_exit,
            coaching=coaching,
            call_sid_to_coach=call_sid_to_coach,
        )

    def delete(self):
        """
        Deletes the ParticipantInstance

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
        return '<Twilio.Api.V2010.ParticipantInstance {}>'.format(context)
