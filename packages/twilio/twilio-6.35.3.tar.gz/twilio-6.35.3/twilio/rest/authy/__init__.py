# coding=utf-8
r"""
This code was generated by
\ / _    _  _|   _  _
 | (_)\/(_)(_|\/| |(/_  v1.0.0
      /       /
"""

from twilio.base.domain import Domain
from twilio.rest.authy.v1 import V1


class Authy(Domain):

    def __init__(self, twilio):
        """
        Initialize the Authy Domain

        :returns: Domain for Authy
        :rtype: twilio.rest.authy.Authy
        """
        super(Authy, self).__init__(twilio)

        self.base_url = 'https://authy.twilio.com'

        # Versions
        self._v1 = None

    @property
    def v1(self):
        """
        :returns: Version v1 of authy
        :rtype: twilio.rest.authy.v1.V1
        """
        if self._v1 is None:
            self._v1 = V1(self)
        return self._v1

    @property
    def forms(self):
        """
        :rtype: twilio.rest.authy.v1.form.FormList
        """
        return self.v1.forms

    @property
    def services(self):
        """
        :rtype: twilio.rest.authy.v1.service.ServiceList
        """
        return self.v1.services

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        return '<Twilio.Authy>'
