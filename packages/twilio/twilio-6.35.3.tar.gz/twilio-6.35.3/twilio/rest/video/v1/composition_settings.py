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


class CompositionSettingsList(ListResource):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version):
        """
        Initialize the CompositionSettingsList

        :param Version version: Version that contains the resource

        :returns: twilio.rest.video.v1.composition_settings.CompositionSettingsList
        :rtype: twilio.rest.video.v1.composition_settings.CompositionSettingsList
        """
        super(CompositionSettingsList, self).__init__(version)

        # Path Solution
        self._solution = {}

    def get(self):
        """
        Constructs a CompositionSettingsContext

        :returns: twilio.rest.video.v1.composition_settings.CompositionSettingsContext
        :rtype: twilio.rest.video.v1.composition_settings.CompositionSettingsContext
        """
        return CompositionSettingsContext(self._version, )

    def __call__(self):
        """
        Constructs a CompositionSettingsContext

        :returns: twilio.rest.video.v1.composition_settings.CompositionSettingsContext
        :rtype: twilio.rest.video.v1.composition_settings.CompositionSettingsContext
        """
        return CompositionSettingsContext(self._version, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Video.V1.CompositionSettingsList>'


class CompositionSettingsPage(Page):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, response, solution):
        """
        Initialize the CompositionSettingsPage

        :param Version version: Version that contains the resource
        :param Response response: Response from the API

        :returns: twilio.rest.video.v1.composition_settings.CompositionSettingsPage
        :rtype: twilio.rest.video.v1.composition_settings.CompositionSettingsPage
        """
        super(CompositionSettingsPage, self).__init__(version, response)

        # Path Solution
        self._solution = solution

    def get_instance(self, payload):
        """
        Build an instance of CompositionSettingsInstance

        :param dict payload: Payload response from the API

        :returns: twilio.rest.video.v1.composition_settings.CompositionSettingsInstance
        :rtype: twilio.rest.video.v1.composition_settings.CompositionSettingsInstance
        """
        return CompositionSettingsInstance(self._version, payload, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Video.V1.CompositionSettingsPage>'


class CompositionSettingsContext(InstanceContext):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version):
        """
        Initialize the CompositionSettingsContext

        :param Version version: Version that contains the resource

        :returns: twilio.rest.video.v1.composition_settings.CompositionSettingsContext
        :rtype: twilio.rest.video.v1.composition_settings.CompositionSettingsContext
        """
        super(CompositionSettingsContext, self).__init__(version)

        # Path Solution
        self._solution = {}
        self._uri = '/CompositionSettings/Default'.format(**self._solution)

    def fetch(self):
        """
        Fetch the CompositionSettingsInstance

        :returns: The fetched CompositionSettingsInstance
        :rtype: twilio.rest.video.v1.composition_settings.CompositionSettingsInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return CompositionSettingsInstance(self._version, payload, )

    def create(self, friendly_name, aws_credentials_sid=values.unset,
               encryption_key_sid=values.unset, aws_s3_url=values.unset,
               aws_storage_enabled=values.unset, encryption_enabled=values.unset):
        """
        Create the CompositionSettingsInstance

        :param unicode friendly_name: A descriptive string that you create to describe the resource
        :param unicode aws_credentials_sid: The SID of the stored Credential resource
        :param unicode encryption_key_sid: The SID of the Public Key resource to use for encryption
        :param unicode aws_s3_url: The URL of the AWS S3 bucket where the compositions should be stored
        :param bool aws_storage_enabled: Whether all compositions should be written to the aws_s3_url
        :param bool encryption_enabled: Whether all compositions should be stored in an encrypted form

        :returns: The created CompositionSettingsInstance
        :rtype: twilio.rest.video.v1.composition_settings.CompositionSettingsInstance
        """
        data = values.of({
            'FriendlyName': friendly_name,
            'AwsCredentialsSid': aws_credentials_sid,
            'EncryptionKeySid': encryption_key_sid,
            'AwsS3Url': aws_s3_url,
            'AwsStorageEnabled': aws_storage_enabled,
            'EncryptionEnabled': encryption_enabled,
        })

        payload = self._version.create(method='POST', uri=self._uri, data=data, )

        return CompositionSettingsInstance(self._version, payload, )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Video.V1.CompositionSettingsContext {}>'.format(context)


class CompositionSettingsInstance(InstanceResource):
    """ PLEASE NOTE that this class contains preview products that are subject
    to change. Use them with caution. If you currently do not have developer
    preview access, please contact help@twilio.com. """

    def __init__(self, version, payload):
        """
        Initialize the CompositionSettingsInstance

        :returns: twilio.rest.video.v1.composition_settings.CompositionSettingsInstance
        :rtype: twilio.rest.video.v1.composition_settings.CompositionSettingsInstance
        """
        super(CompositionSettingsInstance, self).__init__(version)

        # Marshaled Properties
        self._properties = {
            'account_sid': payload.get('account_sid'),
            'friendly_name': payload.get('friendly_name'),
            'aws_credentials_sid': payload.get('aws_credentials_sid'),
            'aws_s3_url': payload.get('aws_s3_url'),
            'aws_storage_enabled': payload.get('aws_storage_enabled'),
            'encryption_key_sid': payload.get('encryption_key_sid'),
            'encryption_enabled': payload.get('encryption_enabled'),
            'url': payload.get('url'),
        }

        # Context
        self._context = None
        self._solution = {}

    @property
    def _proxy(self):
        """
        Generate an instance context for the instance, the context is capable of
        performing various actions.  All instance actions are proxied to the context

        :returns: CompositionSettingsContext for this CompositionSettingsInstance
        :rtype: twilio.rest.video.v1.composition_settings.CompositionSettingsContext
        """
        if self._context is None:
            self._context = CompositionSettingsContext(self._version, )
        return self._context

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
    def aws_credentials_sid(self):
        """
        :returns: The SID of the stored Credential resource
        :rtype: unicode
        """
        return self._properties['aws_credentials_sid']

    @property
    def aws_s3_url(self):
        """
        :returns: The URL of the AWS S3 bucket where the compositions are stored
        :rtype: unicode
        """
        return self._properties['aws_s3_url']

    @property
    def aws_storage_enabled(self):
        """
        :returns: Whether all compositions are written to the aws_s3_url
        :rtype: bool
        """
        return self._properties['aws_storage_enabled']

    @property
    def encryption_key_sid(self):
        """
        :returns: The SID of the Public Key resource used for encryption
        :rtype: unicode
        """
        return self._properties['encryption_key_sid']

    @property
    def encryption_enabled(self):
        """
        :returns: Whether all compositions are stored in an encrypted form
        :rtype: bool
        """
        return self._properties['encryption_enabled']

    @property
    def url(self):
        """
        :returns: The absolute URL of the resource
        :rtype: unicode
        """
        return self._properties['url']

    def fetch(self):
        """
        Fetch the CompositionSettingsInstance

        :returns: The fetched CompositionSettingsInstance
        :rtype: twilio.rest.video.v1.composition_settings.CompositionSettingsInstance
        """
        return self._proxy.fetch()

    def create(self, friendly_name, aws_credentials_sid=values.unset,
               encryption_key_sid=values.unset, aws_s3_url=values.unset,
               aws_storage_enabled=values.unset, encryption_enabled=values.unset):
        """
        Create the CompositionSettingsInstance

        :param unicode friendly_name: A descriptive string that you create to describe the resource
        :param unicode aws_credentials_sid: The SID of the stored Credential resource
        :param unicode encryption_key_sid: The SID of the Public Key resource to use for encryption
        :param unicode aws_s3_url: The URL of the AWS S3 bucket where the compositions should be stored
        :param bool aws_storage_enabled: Whether all compositions should be written to the aws_s3_url
        :param bool encryption_enabled: Whether all compositions should be stored in an encrypted form

        :returns: The created CompositionSettingsInstance
        :rtype: twilio.rest.video.v1.composition_settings.CompositionSettingsInstance
        """
        return self._proxy.create(
            friendly_name,
            aws_credentials_sid=aws_credentials_sid,
            encryption_key_sid=encryption_key_sid,
            aws_s3_url=aws_s3_url,
            aws_storage_enabled=aws_storage_enabled,
            encryption_enabled=encryption_enabled,
        )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Twilio.Video.V1.CompositionSettingsInstance {}>'.format(context)
