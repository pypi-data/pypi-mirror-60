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
from twilio.rest.api.v2010.account.address.dependent_phone_number import DependentPhoneNumberList


class AddressList(ListResource):
    """  """

    def __init__(self, version, account_sid):
        """
        Initialize the AddressList

        :param Version version: Version that contains the resource
        :param account_sid: The SID of the Account that is responsible for the resource

        :returns: twilio.rest.api.v2010.account.address.AddressList
        :rtype: twilio.rest.api.v2010.account.address.AddressList
        """
        super(AddressList, self).__init__(version)

        # Path Solution
        self._solution = {'account_sid': account_sid, }
        self._uri = '/Accounts/{account_sid}/Addresses.json'.format(**self._solution)

    def create(self, customer_name, street, city, region, postal_code, iso_country,
               friendly_name=values.unset, emergency_enabled=values.unset,
               auto_correct_address=values.unset):
        """
        Create the AddressInstance

        :param unicode customer_name: The name to associate with the new address
        :param unicode street: The number and street address of the new address
        :param unicode city: The city of the new address
        :param unicode region: The state or region of the new address
        :param unicode postal_code: The postal code of the new address
        :param unicode iso_country: The ISO country code of the new address
        :param unicode friendly_name: A string to describe the new resource
        :param bool emergency_enabled: Whether to enable emergency calling on the new address
        :param bool auto_correct_address: Whether we should automatically correct the address

        :returns: The created AddressInstance
        :rtype: twilio.rest.api.v2010.account.address.AddressInstance
        """
        data = values.of({
            'CustomerName': customer_name,
            'Street': street,
            'City': city,
            'Region': region,
            'PostalCode': postal_code,
            'IsoCountry': iso_country,
            'FriendlyName': friendly_name,
            'EmergencyEnabled': emergency_enabled,
            'AutoCorrectAddress': auto_correct_address,
        })

        payload = self._version.create(method='POST', uri=self._uri, data=data, )

        return AddressInstance(self._version, payload, account_sid=self._solution['account_sid'], )

    def stream(self, customer_name=values.unset, friendly_name=values.unset,
               iso_country=values.unset, limit=None, page_size=None):
        """
        Streams AddressInstance records from the API as a generator stream.
        This operation lazily loads records as efficiently as possible until the limit
        is reached.
        The results are returned as a generator, so this operation is memory efficient.

        :param unicode customer_name: The `customer_name` of the Address resources to read
        :param unicode friendly_name: The string that identifies the Address resources to read
        :param unicode iso_country: The ISO country code of the Address resources to read
        :param int limit: Upper limit for the number of records to return. stream()
                          guarantees to never return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, stream() will attempt to read the
                              limit with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.api.v2010.account.address.AddressInstance]
        """
        limits = self._version.read_limits(limit, page_size)

        page = self.page(
            customer_name=customer_name,
            friendly_name=friendly_name,
            iso_country=iso_country,
            page_size=limits['page_size'],
        )

        return self._version.stream(page, limits['limit'], limits['page_limit'])

    def list(self, customer_name=values.unset, friendly_name=values.unset,
             iso_country=values.unset, limit=None, page_size=None):
        """
        Lists AddressInstance records from the API as a list.
        Unlike stream(), this operation is eager and will load `limit` records into
        memory before returning.

        :param unicode customer_name: The `customer_name` of the Address resources to read
        :param unicode friendly_name: The string that identifies the Address resources to read
        :param unicode iso_country: The ISO country code of the Address resources to read
        :param int limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param int page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)

        :returns: Generator that will yield up to limit results
        :rtype: list[twilio.rest.api.v2010.account.address.AddressInstance]
        """
        return list(self.stream(
            customer_name=customer_name,
            friendly_name=friendly_name,
            iso_country=iso_country,
            limit=limit,
            page_size=page_size,
        ))

    def page(self, customer_name=values.unset, friendly_name=values.unset,
             iso_country=values.unset, page_token=values.unset,
             page_number=values.unset, page_size=values.unset):
        """
        Retrieve a single page of AddressInstance records from the API.
        Request is executed immediately

        :param unicode customer_name: The `customer_name` of the Address resources to read
        :param unicode friendly_name: The string that identifies the Address resources to read
        :param unicode iso_country: The ISO country code of the Address resources to read
        :param str page_token: PageToken provided by the API
        :param int page_number: Page Number, this value is simply for client state
        :param int page_size: Number of records to return, defaults to 50

        :returns: Page of AddressInstance
        :rtype: twilio.rest.api.v2010.account.address.AddressPage
        """
        data = values.of({
            'CustomerName': customer_name,
            'FriendlyName': friendly_name,
            'IsoCountry': iso_country,
            'PageToken': page_token,
            'Page': page_number,
            'PageSize': page_size,
        })

        response = self._version.page(method='GET', uri=self._uri, params=data, )

        return AddressPage(self._version, response, self._solution)

    def get_page(self, target_url):
        """
        Retrieve a specific page of AddressInstance records from the API.
        Request is executed immediately

        :param str target_url: API-generated URL for the requested results page

        :returns: Page of AddressInstance
        :rtype: twilio.rest.api.v2010.account.address.AddressPage
        """
        response = self._version.domain.twilio.request(
            'GET',
            target_url,
        )

        return AddressPage(self._version, response, self._solution)

    def get(self, sid):
        """
        Constructs a AddressContext

        :param sid: The unique string that identifies the resource

        :returns: twilio.rest.api.v2010.account.address.AddressContext
        :rtype: twilio.rest.api.v2010.account.address.AddressContext
        """
        return AddressContext(self._version, account_sid=self._solution['account_sid'], sid=sid, )

    def __call__(self, sid):
        """
        Constructs a AddressContext

        :param sid: The unique string that identifies the resource

        :returns: twilio.rest.api.v2010.account.address.AddressContext
        :rtype: twilio.rest.api.v2010.account.address.AddressContext
        """
        return AddressContext(self._version, account_sid=self._solution['account_sid'], sid=sid, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Api.V2010.AddressList>'


class AddressPage(Page):
    """  """

    def __init__(self, version, response, solution):
        """
        Initialize the AddressPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API
        :param account_sid: The SID of the Account that is responsible for the resource

        :returns: twilio.rest.api.v2010.account.address.AddressPage
        :rtype: twilio.rest.api.v2010.account.address.AddressPage
        """
        super(AddressPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of AddressInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.api.v2010.account.address.AddressInstance
        :rtype: twilio.rest.api.v2010.account.address.AddressInstance
        """
        return AddressInstance(self._version, payload, account_sid=self._solution['account_sid'], )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Api.V2010.AddressPage>'


class AddressContext(InstanceContext):
    """  """

    def __init__(self, version, account_sid, sid):
        """
        Initialize the AddressContext

        :param Version version: Version that contains the resource
        :param account_sid: The SID of the Account that is responsible for this address
        :param sid: The unique string that identifies the resource

        :returns: twilio.rest.api.v2010.account.address.AddressContext
        :rtype: twilio.rest.api.v2010.account.address.AddressContext
        """
        super(AddressContext, self).__init__(version)

        # Path Solution
        self._solution = {'account_sid': account_sid, 'sid': sid, }
        self._uri = '/Accounts/{account_sid}/Addresses/{sid}.json'.format(**self._solution)

        # Dependents
        self._dependent_phone_numbers = None

    def delete(self):
        """
        Deletes the AddressInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._version.delete(method='DELETE', uri=self._uri, )

    def fetch(self):
        """
        Fetch the AddressInstance

        :returns: The fetched AddressInstance
        :rtype: twilio.rest.api.v2010.account.address.AddressInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return AddressInstance(
            self._version,
            payload,
            account_sid=self._solution['account_sid'],
            sid=self._solution['sid'],
        )

    def update(self, friendly_name=values.unset, customer_name=values.unset,
               street=values.unset, city=values.unset, region=values.unset,
               postal_code=values.unset, emergency_enabled=values.unset,
               auto_correct_address=values.unset):
        """
        Update the AddressInstance

        :param unicode friendly_name: A string to describe the resource
        :param unicode customer_name: The name to associate with the address
        :param unicode street: The number and street address of the address
        :param unicode city: The city of the address
        :param unicode region: The state or region of the address
        :param unicode postal_code: The postal code of the address
        :param bool emergency_enabled: Whether to enable emergency calling on the address
        :param bool auto_correct_address: Whether we should automatically correct the address

        :returns: The updated AddressInstance
        :rtype: twilio.rest.api.v2010.account.address.AddressInstance
        """
        data = values.of({
            'FriendlyName': friendly_name,
            'CustomerName': customer_name,
            'Street': street,
            'City': city,
            'Region': region,
            'PostalCode': postal_code,
            'EmergencyEnabled': emergency_enabled,
            'AutoCorrectAddress': auto_correct_address,
        })

        payload = self._version.update(method='POST', uri=self._uri, data=data, )

        return AddressInstance(
            self._version,
            payload,
            account_sid=self._solution['account_sid'],
            sid=self._solution['sid'],
        )

    @property
    def dependent_phone_numbers(self):
        """
        Access the dependent_phone_numbers

        :returns: twilio.rest.api.v2010.account.address.dependent_phone_number.DependentPhoneNumberList
        :rtype: twilio.rest.api.v2010.account.address.dependent_phone_number.DependentPhoneNumberList
        """
        if self._dependent_phone_numbers is None:
            self._dependent_phone_numbers = DependentPhoneNumberList(
                self._version,
                account_sid=self._solution['account_sid'],
                address_sid=self._solution['sid'],
            )
        return self._dependent_phone_numbers

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Api.V2010.AddressContext {}>'.format(context)


class AddressInstance(InstanceResource):
    """  """

    def __init__(self, version, payload, account_sid, sid=None):
        """
        Initialize the AddressInstance

        :returns: twilio.rest.api.v2010.account.address.AddressInstance
        :rtype: twilio.rest.api.v2010.account.address.AddressInstance
        """
        super(AddressInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'account_sid': payload.get('account_sid'),
            'city': payload.get('city'),
            'customer_name': payload.get('customer_name'),
            'date_created': deserialize.rfc2822_datetime(payload.get('date_created')),
            'date_updated': deserialize.rfc2822_datetime(payload.get('date_updated')),
            'friendly_name': payload.get('friendly_name'),
            'iso_country': payload.get('iso_country'),
            'postal_code': payload.get('postal_code'),
            'region': payload.get('region'),
            'sid': payload.get('sid'),
            'street': payload.get('street'),
            'uri': payload.get('uri'),
            'emergency_enabled': payload.get('emergency_enabled'),
            'validated': payload.get('validated'),
            'verified': payload.get('verified'),
        }

        # Context
        self._context = None
        self._solution = {'account_sid': account_sid, 'sid': sid or self._properties['sid'], }

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: AddressContext for this AddressInstance
        :rtype: twilio.rest.api.v2010.account.address.AddressContext
        """
        if self._context is None:
            self._context = AddressContext(
                self._version,
                account_sid=self._solution['account_sid'],
                sid=self._solution['sid'],
            )
        return self._context

    @property
    def account_sid(self):
        """
        :returns: The SID of the Account that is responsible for the resource
        :rtype: unicode
        """
        return self._properties['account_sid']

    @property
    def city(self):
        """
        :returns: The city in which the address is located
        :rtype: unicode
        """
        return self._properties['city']

    @property
    def customer_name(self):
        """
        :returns: The name associated with the address
        :rtype: unicode
        """
        return self._properties['customer_name']

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
    def friendly_name(self):
        """
        :returns: The string that you assigned to describe the resource
        :rtype: unicode
        """
        return self._properties['friendly_name']

    @property
    def iso_country(self):
        """
        :returns: The ISO country code of the address
        :rtype: unicode
        """
        return self._properties['iso_country']

    @property
    def postal_code(self):
        """
        :returns: The postal code of the address
        :rtype: unicode
        """
        return self._properties['postal_code']

    @property
    def region(self):
        """
        :returns: The state or region of the address
        :rtype: unicode
        """
        return self._properties['region']

    @property
    def sid(self):
        """
        :returns: The unique string that identifies the resource
        :rtype: unicode
        """
        return self._properties['sid']

    @property
    def street(self):
        """
        :returns: The number and street address of the address
        :rtype: unicode
        """
        return self._properties['street']

    @property
    def uri(self):
        """
        :returns: The URI of the resource, relative to `https://api.twilio.com`
        :rtype: unicode
        """
        return self._properties['uri']

    @property
    def emergency_enabled(self):
        """
        :returns: Whether emergency calling has been enabled on this number
        :rtype: bool
        """
        return self._properties['emergency_enabled']

    @property
    def validated(self):
        """
        :returns: Whether the address has been validated to comply with local regulation
        :rtype: bool
        """
        return self._properties['validated']

    @property
    def verified(self):
        """
        :returns: Whether the address has been verified to comply with regulation
        :rtype: bool
        """
        return self._properties['verified']

    def delete(self):
        """
        Deletes the AddressInstance

        :returns: True if delete succeeds, False otherwise
        :rtype: bool
        """
        return self._proxy.delete()

    def fetch(self):
        """
        Fetch the AddressInstance

        :returns: The fetched AddressInstance
        :rtype: twilio.rest.api.v2010.account.address.AddressInstance
        """
        return self._proxy.fetch()

    def update(self, friendly_name=values.unset, customer_name=values.unset,
               street=values.unset, city=values.unset, region=values.unset,
               postal_code=values.unset, emergency_enabled=values.unset,
               auto_correct_address=values.unset):
        """
        Update the AddressInstance

        :param unicode friendly_name: A string to describe the resource
        :param unicode customer_name: The name to associate with the address
        :param unicode street: The number and street address of the address
        :param unicode city: The city of the address
        :param unicode region: The state or region of the address
        :param unicode postal_code: The postal code of the address
        :param bool emergency_enabled: Whether to enable emergency calling on the address
        :param bool auto_correct_address: Whether we should automatically correct the address

        :returns: The updated AddressInstance
        :rtype: twilio.rest.api.v2010.account.address.AddressInstance
        """
        return self._proxy.update(
            friendly_name=friendly_name,
            customer_name=customer_name,
            street=street,
            city=city,
            region=region,
            postal_code=postal_code,
            emergency_enabled=emergency_enabled,
            auto_correct_address=auto_correct_address,
        )

    @property
    def dependent_phone_numbers(self):
        """
        Access the dependent_phone_numbers

        :returns: twilio.rest.api.v2010.account.address.dependent_phone_number.DependentPhoneNumberList
        :rtype: twilio.rest.api.v2010.account.address.dependent_phone_number.DependentPhoneNumberList
        """
        return self._proxy.dependent_phone_numbers

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Api.V2010.AddressInstance {}>'.format(context)
