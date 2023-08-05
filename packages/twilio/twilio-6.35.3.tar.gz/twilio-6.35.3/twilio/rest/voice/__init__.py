# coding=utf-8
r"""
This code was generated by
\ / _    _  _|   _  _
 | (_)\/(_)(_|\/| |(/_  v1.0.0
      /       /
"""

from twilio.base.domain import Domain
from twilio.rest.voice.v1 import V1


class Voice(Domain):

    def __init__(self, twilio):
        """
        Initialize the Voice Domain

        :returns: Domain for Voice
        :rtype: twilio.rest.voice.Voice
        """
        super(Voice, self).__init__(twilio)

        self.base_url = 'https://voice.twilio.com'

        # Versions
        self._v1 = None

    @property
    def v1(self):
        """
        :returns: Version v1 of voice
        :rtype: twilio.rest.voice.v1.V1
        """
        if self._v1 is None:
            self._v1 = V1(self)
        return self._v1

    @property
    def dialing_permissions(self):
        """
        :rtype: twilio.rest.voice.v1.dialing_permissions.DialingPermissionsList
        """
        return self.v1.dialing_permissions

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Voice>'
