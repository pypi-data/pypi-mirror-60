# coding=utf-8
r"""
This code was generated by
\ / _    _  _|   _  _
 | (_)\/(_)(_|\/| |(/_  v1.0.0
      /       /
"""

from twilio.base import values
from twilio.base.instance_context import InstanceContext
from twilio.base.instance_resource import InstanceResource
from twilio.base.list_resource import ListResource
from twilio.base.page import Page


class NumberList(ListResource):
    """  """

    def __init__(self, version):
        """
        Initialize the NumberList

        :param Version version: Version that contains the resource

        :returns: twilio.rest.pricing.v2.voice.number.NumberList
        :rtype: twilio.rest.pricing.v2.voice.number.NumberList
        """
        super(NumberList, self).__init__(version)

        # Path Solution
        self._solution = {}

    def get(self, destination_number):
        """
        Constructs a NumberContext

        :param destination_number: The destination number for which to fetch pricing information

        :returns: twilio.rest.pricing.v2.voice.number.NumberContext
        :rtype: twilio.rest.pricing.v2.voice.number.NumberContext
        """
        return NumberContext(self._version, destination_number=destination_number, )

    def __call__(self, destination_number):
        """
        Constructs a NumberContext

        :param destination_number: The destination number for which to fetch pricing information

        :returns: twilio.rest.pricing.v2.voice.number.NumberContext
        :rtype: twilio.rest.pricing.v2.voice.number.NumberContext
        """
        return NumberContext(self._version, destination_number=destination_number, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Pricing.V2.NumberList>'


class NumberPage(Page):
    """  """

    def __init__(self, version, response, solution):
        """
        Initialize the NumberPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API

        :returns: twilio.rest.pricing.v2.voice.number.NumberPage
        :rtype: twilio.rest.pricing.v2.voice.number.NumberPage
        """
        super(NumberPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of NumberInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.pricing.v2.voice.number.NumberInstance
        :rtype: twilio.rest.pricing.v2.voice.number.NumberInstance
        """
        return NumberInstance(self._version, payload, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Pricing.V2.NumberPage>'


class NumberContext(InstanceContext):
    """  """

    def __init__(self, version, destination_number):
        """
        Initialize the NumberContext

        :param Version version: Version that contains the resource
        :param destination_number: The destination number for which to fetch pricing information

        :returns: twilio.rest.pricing.v2.voice.number.NumberContext
        :rtype: twilio.rest.pricing.v2.voice.number.NumberContext
        """
        super(NumberContext, self).__init__(version)

        # Path Solution
        self._solution = {'destination_number': destination_number, }
        self._uri = '/Voice/Numbers/{destination_number}'.format(**self._solution)

    def fetch(self, origination_number=values.unset):
        """
        Fetch the NumberInstance

        :param unicode origination_number: The origination number for which to fetch pricing information

        :returns: The fetched NumberInstance
        :rtype: twilio.rest.pricing.v2.voice.number.NumberInstance
        """
        data = values.of({'OriginationNumber': origination_number, })

        payload = self._version.fetch(method='GET', uri=self._uri, params=data, )

        return NumberInstance(
            self._version,
            payload,
            destination_number=self._solution['destination_number'],
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Pricing.V2.NumberContext {}>'.format(context)


class NumberInstance(InstanceResource):
    """  """

    def __init__(self, version, payload, destination_number=None):
        """
        Initialize the NumberInstance

        :returns: twilio.rest.pricing.v2.voice.number.NumberInstance
        :rtype: twilio.rest.pricing.v2.voice.number.NumberInstance
        """
        super(NumberInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'destination_number': payload.get('destination_number'),
            'origination_number': payload.get('origination_number'),
            'country': payload.get('country'),
            'iso_country': payload.get('iso_country'),
            'outbound_call_prices': payload.get('outbound_call_prices'),
            'inbound_call_price': payload.get('inbound_call_price'),
            'price_unit': payload.get('price_unit'),
            'url': payload.get('url'),
        }

        # Context
        self._context = None
        self._solution = {
            'destination_number': destination_number or self._properties['destination_number'],
        }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: NumberContext for this NumberInstance
        :rtype: twilio.rest.pricing.v2.voice.number.NumberContext
        """
        if self._context is None:
            self._context = NumberContext(
                self._version,
                destination_number=self._solution['destination_number'],
            )
        return self._context

    @property
    def destination_number(self):
        """
        :returns: The destination phone number, in E.164 format
        :rtype: unicode
        """
        return self._properties['destination_number']

    @property
    def origination_number(self):
        """
        :returns: The origination phone number, in E.164 format
        :rtype: unicode
        """
        return self._properties['origination_number']

    @property
    def country(self):
        """
        :returns: The name of the country
        :rtype: unicode
        """
        return self._properties['country']

    @property
    def iso_country(self):
        """
        :returns: The ISO country code
        :rtype: unicode
        """
        return self._properties['iso_country']

    @property
    def outbound_call_prices(self):
        """
        :returns: The list of OutboundCallPriceWithOrigin records
        :rtype: unicode
        """
        return self._properties['outbound_call_prices']

    @property
    def inbound_call_price(self):
        """
        :returns: The InboundCallPrice record
        :rtype: unicode
        """
        return self._properties['inbound_call_price']

    @property
    def price_unit(self):
        """
        :returns: The currency in which prices are measured, in ISO 4127 format (e.g. usd, eur, jpy)
        :rtype: unicode
        """
        return self._properties['price_unit']

    @property
    def url(self):
        """
        :returns: The absolute URL of the resource
        :rtype: unicode
        """
        return self._properties['url']

    def fetch(self, origination_number=values.unset):
        """
        Fetch the NumberInstance

        :param unicode origination_number: The origination number for which to fetch pricing information

        :returns: The fetched NumberInstance
        :rtype: twilio.rest.pricing.v2.voice.number.NumberInstance
        """
        return self._proxy.fetch(origination_number=origination_number, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Pricing.V2.NumberInstance {}>'.format(context)
