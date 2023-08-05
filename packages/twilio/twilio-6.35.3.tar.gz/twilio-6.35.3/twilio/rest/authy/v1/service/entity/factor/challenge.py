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


class ChallengeList(ListResource):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, service_sid, identity, factor_sid):
        """
        Initialize the ChallengeList

        :param Version version: Version that contains the resource
        :param service_sid: Service Sid.
        :param identity: Unique identity of the Entity
        :param factor_sid: Factor Sid.

        :returns: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeList
        :rtype: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeList
        """
        super(ChallengeList, self).__init__(version)

        # Path Solution
        self._solution = {'service_sid': service_sid, 'identity': identity, 'factor_sid': factor_sid, }
        self._uri = '/Services/{service_sid}/Entities/{identity}/Factors/{factor_sid}/Challenges'.format(**self._solution)

    def create(self, expiration_date=values.unset, details=values.unset,
               hidden_details=values.unset, twilio_authy_sandbox_mode=values.unset):
        """
        Create the ChallengeInstance

        :param datetime expiration_date: The future date in which this Challenge will expire
        :param unicode details: Public details provided to contextualize the Challenge
        :param unicode hidden_details: Hidden details provided to contextualize the Challenge
        :param unicode twilio_authy_sandbox_mode: The Twilio-Authy-Sandbox-Mode HTTP request header

        :returns: The created ChallengeInstance
        :rtype: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeInstance
        """
        data = values.of({
            'ExpirationDate': serialize.iso8601_datetime(expiration_date),
            'Details': details,
            'HiddenDetails': hidden_details,
        })
        headers = values.of({'Twilio-Authy-Sandbox-Mode': twilio_authy_sandbox_mode, })

        payload = self._version.create(method='POST', uri=self._uri, data=data, headers=headers, )

        return ChallengeInstance(
            self._version,
            payload,
            service_sid=self._solution['service_sid'],
            identity=self._solution['identity'],
            factor_sid=self._solution['factor_sid'],
        )

    def get(self, sid):
        """
        Constructs a ChallengeContext

        :param sid: A string that uniquely identifies this Challenge, or `latest`.

        :returns: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeContext
        :rtype: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeContext
        """
        return ChallengeContext(
            self._version,
            service_sid=self._solution['service_sid'],
            identity=self._solution['identity'],
            factor_sid=self._solution['factor_sid'],
            sid=sid,
        )

    def __call__(self, sid):
        """
        Constructs a ChallengeContext

        :param sid: A string that uniquely identifies this Challenge, or `latest`.

        :returns: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeContext
        :rtype: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeContext
        """
        return ChallengeContext(
            self._version,
            service_sid=self._solution['service_sid'],
            identity=self._solution['identity'],
            factor_sid=self._solution['factor_sid'],
            sid=sid,
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Authy.V1.ChallengeList>'


class ChallengePage(Page):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, response, solution):
        """
        Initialize the ChallengePage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API
        :param service_sid: Service Sid.
        :param identity: Unique identity of the Entity
        :param factor_sid: Factor Sid.

        :returns: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengePage
        :rtype: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengePage
        """
        super(ChallengePage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of ChallengeInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeInstance
        :rtype: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeInstance
        """
        return ChallengeInstance(
            self._version,
            payload,
            service_sid=self._solution['service_sid'],
            identity=self._solution['identity'],
            factor_sid=self._solution['factor_sid'],
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Authy.V1.ChallengePage>'


class ChallengeContext(InstanceContext):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, service_sid, identity, factor_sid, sid):
        """
        Initialize the ChallengeContext

        :param Version version: Version that contains the resource
        :param service_sid: Service Sid.
        :param identity: Unique identity of the Entity
        :param factor_sid: Factor Sid.
        :param sid: A string that uniquely identifies this Challenge, or `latest`.

        :returns: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeContext
        :rtype: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeContext
        """
        super(ChallengeContext, self).__init__(version)

        # Path Solution
        self._solution = {
            'service_sid': service_sid,
            'identity': identity,
            'factor_sid': factor_sid,
            'sid': sid,
        }
        self._uri = '/Services/{service_sid}/Entities/{identity}/Factors/{factor_sid}/Challenges/{sid}'.format(**self._solution)

    def delete(self, twilio_authy_sandbox_mode=values.unset):
        """
        Deletes the ChallengeInstance

        :param unicode twilio_authy_sandbox_mode: The Twilio-Authy-Sandbox-Mode HTTP request header

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        headers = values.of({'Twilio-Authy-Sandbox-Mode': twilio_authy_sandbox_mode, })

        return self._version.delete(method='DELETE', uri=self._uri, headers=headers, )

    def fetch(self, twilio_authy_sandbox_mode=values.unset):
        """
        Fetch the ChallengeInstance

        :param unicode twilio_authy_sandbox_mode: The Twilio-Authy-Sandbox-Mode HTTP request header

        :returns: The fetched ChallengeInstance
        :rtype: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeInstance
        """
        headers = values.of({'Twilio-Authy-Sandbox-Mode': twilio_authy_sandbox_mode, })

        payload = self._version.fetch(method='GET', uri=self._uri, headers=headers, )

        return ChallengeInstance(
            self._version,
            payload,
            service_sid=self._solution['service_sid'],
            identity=self._solution['identity'],
            factor_sid=self._solution['factor_sid'],
            sid=self._solution['sid'],
        )

    def update(self, auth_payload=values.unset,
               twilio_authy_sandbox_mode=values.unset):
        """
        Update the ChallengeInstance

        :param unicode auth_payload: Optional payload to verify the Challenge
        :param unicode twilio_authy_sandbox_mode: The Twilio-Authy-Sandbox-Mode HTTP request header

        :returns: The updated ChallengeInstance
        :rtype: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeInstance
        """
        data = values.of({'AuthPayload': auth_payload, })
        headers = values.of({'Twilio-Authy-Sandbox-Mode': twilio_authy_sandbox_mode, })

        payload = self._version.update(method='POST', uri=self._uri, data=data, headers=headers, )

        return ChallengeInstance(
            self._version,
            payload,
            service_sid=self._solution['service_sid'],
            identity=self._solution['identity'],
            factor_sid=self._solution['factor_sid'],
            sid=self._solution['sid'],
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Authy.V1.ChallengeContext {}>'.format(context)


class ChallengeInstance(InstanceResource):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    class ChallengeStatuses(object):
        PENDING = "pending"
        EXPIRED = "expired"
        APPROVED = "approved"
        DENIED = "denied"

    class ChallengeReasons(object):
        NONE = "none"
        NOT_NEEDED = "not_needed"
        NOT_REQUESTED = "not_requested"

    class FactorTypes(object):
        APP_PUSH = "app-push"
        SMS = "sms"
        TOTP = "totp"

    class FactorStrengths(object):
        UNKNOWN = "unknown"
        VERY_LOW = "very_low"
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        VERY_HIGH = "very_high"

    def __init__(self, version, payload, service_sid, identity, factor_sid,
                 sid=None):
        """
        Initialize the ChallengeInstance

        :returns: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeInstance
        :rtype: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeInstance
        """
        super(ChallengeInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'sid': payload.get('sid'),
            'account_sid': payload.get('account_sid'),
            'service_sid': payload.get('service_sid'),
            'entity_sid': payload.get('entity_sid'),
            'identity': payload.get('identity'),
            'factor_sid': payload.get('factor_sid'),
            'date_created': deserialize.iso8601_datetime(payload.get('date_created')),
            'date_updated': deserialize.iso8601_datetime(payload.get('date_updated')),
            'date_responded': deserialize.iso8601_datetime(payload.get('date_responded')),
            'expiration_date': deserialize.iso8601_datetime(payload.get('expiration_date')),
            'status': payload.get('status'),
            'responded_reason': payload.get('responded_reason'),
            'details': payload.get('details'),
            'hidden_details': payload.get('hidden_details'),
            'factor_type': payload.get('factor_type'),
            'factor_strength': payload.get('factor_strength'),
            'url': payload.get('url'),
        }

        # Context
        self._context = None
        self._solution = {
            'service_sid': service_sid,
            'identity': identity,
            'factor_sid': factor_sid,
            'sid': sid or self._properties['sid'],
        }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: ChallengeContext for this ChallengeInstance
        :rtype: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeContext
        """
        if self._context is None:
            self._context = ChallengeContext(
                self._version,
                service_sid=self._solution['service_sid'],
                identity=self._solution['identity'],
                factor_sid=self._solution['factor_sid'],
                sid=self._solution['sid'],
            )
        return self._context

    @property
    def sid(self):
        """
        :returns: A string that uniquely identifies this Challenge.
        :rtype: unicode
        """
        return self._properties['sid']

    @property
    def account_sid(self):
        """
        :returns: Account Sid.
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def service_sid(self):
        """
        :returns: Service Sid.
        :rtype: unicode
        """
        return self._properties['service_sid']

    @property
    def entity_sid(self):
        """
        :returns: Entity Sid.
        :rtype: unicode
        """
        return self._properties['entity_sid']

    @property
    def identity(self):
        """
        :returns: Unique identity of the Entity
        :rtype: unicode
        """
        return self._properties['identity']

    @property
    def factor_sid(self):
        """
        :returns: Factor Sid.
        :rtype: unicode
        """
        return self._properties['factor_sid']

    @property
    def date_created(self):
        """
        :returns: The date this Challenge was created
        :rtype: datetime
        """
        return self._properties['date_created']

    @property
    def date_updated(self):
        """
        :returns: The date this Challenge was updated
        :rtype: datetime
        """
        return self._properties['date_updated']

    @property
    def date_responded(self):
        """
        :returns: The date this Challenge was responded
        :rtype: datetime
        """
        return self._properties['date_responded']

    @property
    def expiration_date(self):
        """
        :returns: The date this Challenge is expired
        :rtype: datetime
        """
        return self._properties['expiration_date']

    @property
    def status(self):
        """
        :returns: The Status of this Challenge
        :rtype: ChallengeInstance.ChallengeStatuses
        """
        return self._properties['status']

    @property
    def responded_reason(self):
        """
        :returns: The Reason of this Challenge `status`
        :rtype: ChallengeInstance.ChallengeReasons
        """
        return self._properties['responded_reason']

    @property
    def details(self):
        """
        :returns: Public details provided to contextualize the Challenge
        :rtype: unicode
        """
        return self._properties['details']

    @property
    def hidden_details(self):
        """
        :returns: Hidden details provided to contextualize the Challenge
        :rtype: unicode
        """
        return self._properties['hidden_details']

    @property
    def factor_type(self):
        """
        :returns: The Factor Type of this Challenge
        :rtype: ChallengeInstance.FactorTypes
        """
        return self._properties['factor_type']

    @property
    def factor_strength(self):
        """
        :returns: The Factor Strength of this Challenge
        :rtype: ChallengeInstance.FactorStrengths
        """
        return self._properties['factor_strength']

    @property
    def url(self):
        """
        :returns: The URL of this resource.
        :rtype: unicode
        """
        return self._properties['url']

    def delete(self, twilio_authy_sandbox_mode=values.unset):
        """
        Deletes the ChallengeInstance

        :param unicode twilio_authy_sandbox_mode: The Twilio-Authy-Sandbox-Mode HTTP request header

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._proxy.delete(twilio_authy_sandbox_mode=twilio_authy_sandbox_mode, )

    def fetch(self, twilio_authy_sandbox_mode=values.unset):
        """
        Fetch the ChallengeInstance

        :param unicode twilio_authy_sandbox_mode: The Twilio-Authy-Sandbox-Mode HTTP request header

        :returns: The fetched ChallengeInstance
        :rtype: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeInstance
        """
        return self._proxy.fetch(twilio_authy_sandbox_mode=twilio_authy_sandbox_mode, )

    def update(self, auth_payload=values.unset,
               twilio_authy_sandbox_mode=values.unset):
        """
        Update the ChallengeInstance

        :param unicode auth_payload: Optional payload to verify the Challenge
        :param unicode twilio_authy_sandbox_mode: The Twilio-Authy-Sandbox-Mode HTTP request header

        :returns: The updated ChallengeInstance
        :rtype: twilio.rest.authy.v1.service.entity.factor.challenge.ChallengeInstance
        """
        return self._proxy.update(
            auth_payload=auth_payload,
            twilio_authy_sandbox_mode=twilio_authy_sandbox_mode,
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Authy.V1.ChallengeInstance {}>'.format(context)
