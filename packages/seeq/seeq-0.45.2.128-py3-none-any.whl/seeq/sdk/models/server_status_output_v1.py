# coding: utf-8

"""
    Seeq REST API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: 0.45.02-BETA
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class ServerStatusOutputV1(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'admin_contact_email': 'str',
        'admin_contact_name': 'str',
        'installation_id': 'str',
        'server_specs': 'list[ServerSpecOutputV1]',
        'status': 'str',
        'telemetry_enabled': 'bool',
        'version': 'str'
    }

    attribute_map = {
        'admin_contact_email': 'adminContactEmail',
        'admin_contact_name': 'adminContactName',
        'installation_id': 'installationId',
        'server_specs': 'serverSpecs',
        'status': 'status',
        'telemetry_enabled': 'telemetryEnabled',
        'version': 'version'
    }

    def __init__(self, admin_contact_email=None, admin_contact_name=None, installation_id=None, server_specs=None, status=None, telemetry_enabled=False, version=None):
        """
        ServerStatusOutputV1 - a model defined in Swagger
        """

        self._admin_contact_email = None
        self._admin_contact_name = None
        self._installation_id = None
        self._server_specs = None
        self._status = None
        self._telemetry_enabled = None
        self._version = None

        if admin_contact_email is not None:
          self.admin_contact_email = admin_contact_email
        if admin_contact_name is not None:
          self.admin_contact_name = admin_contact_name
        if installation_id is not None:
          self.installation_id = installation_id
        if server_specs is not None:
          self.server_specs = server_specs
        if status is not None:
          self.status = status
        if telemetry_enabled is not None:
          self.telemetry_enabled = telemetry_enabled
        if version is not None:
          self.version = version

    @property
    def admin_contact_email(self):
        """
        Gets the admin_contact_email of this ServerStatusOutputV1.
        The admin contact's email, which is controlled on the server

        :return: The admin_contact_email of this ServerStatusOutputV1.
        :rtype: str
        """
        return self._admin_contact_email

    @admin_contact_email.setter
    def admin_contact_email(self, admin_contact_email):
        """
        Sets the admin_contact_email of this ServerStatusOutputV1.
        The admin contact's email, which is controlled on the server

        :param admin_contact_email: The admin_contact_email of this ServerStatusOutputV1.
        :type: str
        """

        self._admin_contact_email = admin_contact_email

    @property
    def admin_contact_name(self):
        """
        Gets the admin_contact_name of this ServerStatusOutputV1.
        The admin contact's name, which is controlled on the server

        :return: The admin_contact_name of this ServerStatusOutputV1.
        :rtype: str
        """
        return self._admin_contact_name

    @admin_contact_name.setter
    def admin_contact_name(self, admin_contact_name):
        """
        Sets the admin_contact_name of this ServerStatusOutputV1.
        The admin contact's name, which is controlled on the server

        :param admin_contact_name: The admin_contact_name of this ServerStatusOutputV1.
        :type: str
        """

        self._admin_contact_name = admin_contact_name

    @property
    def installation_id(self):
        """
        Gets the installation_id of this ServerStatusOutputV1.
        The installation identifier for this machine, which is controlled on the server

        :return: The installation_id of this ServerStatusOutputV1.
        :rtype: str
        """
        return self._installation_id

    @installation_id.setter
    def installation_id(self, installation_id):
        """
        Sets the installation_id of this ServerStatusOutputV1.
        The installation identifier for this machine, which is controlled on the server

        :param installation_id: The installation_id of this ServerStatusOutputV1.
        :type: str
        """

        self._installation_id = installation_id

    @property
    def server_specs(self):
        """
        Gets the server_specs of this ServerStatusOutputV1.
        Information about the specs of the server

        :return: The server_specs of this ServerStatusOutputV1.
        :rtype: list[ServerSpecOutputV1]
        """
        return self._server_specs

    @server_specs.setter
    def server_specs(self, server_specs):
        """
        Sets the server_specs of this ServerStatusOutputV1.
        Information about the specs of the server

        :param server_specs: The server_specs of this ServerStatusOutputV1.
        :type: list[ServerSpecOutputV1]
        """

        self._server_specs = server_specs

    @property
    def status(self):
        """
        Gets the status of this ServerStatusOutputV1.
        The server readiness status

        :return: The status of this ServerStatusOutputV1.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """
        Sets the status of this ServerStatusOutputV1.
        The server readiness status

        :param status: The status of this ServerStatusOutputV1.
        :type: str
        """

        self._status = status

    @property
    def telemetry_enabled(self):
        """
        Gets the telemetry_enabled of this ServerStatusOutputV1.
        True if sending telemetry back to Seeq is enabled

        :return: The telemetry_enabled of this ServerStatusOutputV1.
        :rtype: bool
        """
        return self._telemetry_enabled

    @telemetry_enabled.setter
    def telemetry_enabled(self, telemetry_enabled):
        """
        Sets the telemetry_enabled of this ServerStatusOutputV1.
        True if sending telemetry back to Seeq is enabled

        :param telemetry_enabled: The telemetry_enabled of this ServerStatusOutputV1.
        :type: bool
        """

        self._telemetry_enabled = telemetry_enabled

    @property
    def version(self):
        """
        Gets the version of this ServerStatusOutputV1.
        The version of Seeq running on the server

        :return: The version of this ServerStatusOutputV1.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """
        Sets the version of this ServerStatusOutputV1.
        The version of Seeq running on the server

        :param version: The version of this ServerStatusOutputV1.
        :type: str
        """

        self._version = version

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, ServerStatusOutputV1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
