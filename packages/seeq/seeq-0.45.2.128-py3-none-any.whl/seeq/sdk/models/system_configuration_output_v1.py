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


class SystemConfigurationOutputV1(object):
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
        'default_auth_auto_login': 'bool',
        'default_auth_provider_id': 'str',
        'default_max_capsule_duration': 'ScalarValueOutputV1',
        'default_max_interpolation': 'ScalarValueOutputV1',
        'maximum_threads': 'int',
        'number_format': 'str',
        'parallelization_threshold': 'ScalarValueOutputV1',
        'priorities': 'list[PriorityV1]',
        'registration_enabled': 'bool',
        'restrict_logs': 'bool',
        'status_message': 'str'
    }

    attribute_map = {
        'default_auth_auto_login': 'defaultAuthAutoLogin',
        'default_auth_provider_id': 'defaultAuthProviderId',
        'default_max_capsule_duration': 'defaultMaxCapsuleDuration',
        'default_max_interpolation': 'defaultMaxInterpolation',
        'maximum_threads': 'maximumThreads',
        'number_format': 'numberFormat',
        'parallelization_threshold': 'parallelizationThreshold',
        'priorities': 'priorities',
        'registration_enabled': 'registrationEnabled',
        'restrict_logs': 'restrictLogs',
        'status_message': 'statusMessage'
    }

    def __init__(self, default_auth_auto_login=False, default_auth_provider_id=None, default_max_capsule_duration=None, default_max_interpolation=None, maximum_threads=None, number_format=None, parallelization_threshold=None, priorities=None, registration_enabled=False, restrict_logs=False, status_message=None):
        """
        SystemConfigurationOutputV1 - a model defined in Swagger
        """

        self._default_auth_auto_login = None
        self._default_auth_provider_id = None
        self._default_max_capsule_duration = None
        self._default_max_interpolation = None
        self._maximum_threads = None
        self._number_format = None
        self._parallelization_threshold = None
        self._priorities = None
        self._registration_enabled = None
        self._restrict_logs = None
        self._status_message = None

        if default_auth_auto_login is not None:
          self.default_auth_auto_login = default_auth_auto_login
        if default_auth_provider_id is not None:
          self.default_auth_provider_id = default_auth_provider_id
        if default_max_capsule_duration is not None:
          self.default_max_capsule_duration = default_max_capsule_duration
        if default_max_interpolation is not None:
          self.default_max_interpolation = default_max_interpolation
        if maximum_threads is not None:
          self.maximum_threads = maximum_threads
        if number_format is not None:
          self.number_format = number_format
        if parallelization_threshold is not None:
          self.parallelization_threshold = parallelization_threshold
        if priorities is not None:
          self.priorities = priorities
        if registration_enabled is not None:
          self.registration_enabled = registration_enabled
        if restrict_logs is not None:
          self.restrict_logs = restrict_logs
        if status_message is not None:
          self.status_message = status_message

    @property
    def default_auth_auto_login(self):
        """
        Gets the default_auth_auto_login of this SystemConfigurationOutputV1.
        True if the system should automatically attempt to login without user action. Only applies when the default auth provider datasource class is \"Windows Auth\"

        :return: The default_auth_auto_login of this SystemConfigurationOutputV1.
        :rtype: bool
        """
        return self._default_auth_auto_login

    @default_auth_auto_login.setter
    def default_auth_auto_login(self, default_auth_auto_login):
        """
        Sets the default_auth_auto_login of this SystemConfigurationOutputV1.
        True if the system should automatically attempt to login without user action. Only applies when the default auth provider datasource class is \"Windows Auth\"

        :param default_auth_auto_login: The default_auth_auto_login of this SystemConfigurationOutputV1.
        :type: bool
        """

        self._default_auth_auto_login = default_auth_auto_login

    @property
    def default_auth_provider_id(self):
        """
        Gets the default_auth_provider_id of this SystemConfigurationOutputV1.
        The datasource ID of the authentication provider that should be automatically selected when the Seeq user interface is displayed

        :return: The default_auth_provider_id of this SystemConfigurationOutputV1.
        :rtype: str
        """
        return self._default_auth_provider_id

    @default_auth_provider_id.setter
    def default_auth_provider_id(self, default_auth_provider_id):
        """
        Sets the default_auth_provider_id of this SystemConfigurationOutputV1.
        The datasource ID of the authentication provider that should be automatically selected when the Seeq user interface is displayed

        :param default_auth_provider_id: The default_auth_provider_id of this SystemConfigurationOutputV1.
        :type: str
        """

        self._default_auth_provider_id = default_auth_provider_id

    @property
    def default_max_capsule_duration(self):
        """
        Gets the default_max_capsule_duration of this SystemConfigurationOutputV1.
        The scalar value of the default capsule duration

        :return: The default_max_capsule_duration of this SystemConfigurationOutputV1.
        :rtype: ScalarValueOutputV1
        """
        return self._default_max_capsule_duration

    @default_max_capsule_duration.setter
    def default_max_capsule_duration(self, default_max_capsule_duration):
        """
        Sets the default_max_capsule_duration of this SystemConfigurationOutputV1.
        The scalar value of the default capsule duration

        :param default_max_capsule_duration: The default_max_capsule_duration of this SystemConfigurationOutputV1.
        :type: ScalarValueOutputV1
        """

        self._default_max_capsule_duration = default_max_capsule_duration

    @property
    def default_max_interpolation(self):
        """
        Gets the default_max_interpolation of this SystemConfigurationOutputV1.
        The scalar value of the default maximum interpolation

        :return: The default_max_interpolation of this SystemConfigurationOutputV1.
        :rtype: ScalarValueOutputV1
        """
        return self._default_max_interpolation

    @default_max_interpolation.setter
    def default_max_interpolation(self, default_max_interpolation):
        """
        Sets the default_max_interpolation of this SystemConfigurationOutputV1.
        The scalar value of the default maximum interpolation

        :param default_max_interpolation: The default_max_interpolation of this SystemConfigurationOutputV1.
        :type: ScalarValueOutputV1
        """

        self._default_max_interpolation = default_max_interpolation

    @property
    def maximum_threads(self):
        """
        Gets the maximum_threads of this SystemConfigurationOutputV1.
        The maximum number of threads to use when parallelizing a single request

        :return: The maximum_threads of this SystemConfigurationOutputV1.
        :rtype: int
        """
        return self._maximum_threads

    @maximum_threads.setter
    def maximum_threads(self, maximum_threads):
        """
        Sets the maximum_threads of this SystemConfigurationOutputV1.
        The maximum number of threads to use when parallelizing a single request

        :param maximum_threads: The maximum_threads of this SystemConfigurationOutputV1.
        :type: int
        """

        self._maximum_threads = maximum_threads

    @property
    def number_format(self):
        """
        Gets the number_format of this SystemConfigurationOutputV1.
        The default number format to be used for items without a number format property.

        :return: The number_format of this SystemConfigurationOutputV1.
        :rtype: str
        """
        return self._number_format

    @number_format.setter
    def number_format(self, number_format):
        """
        Sets the number_format of this SystemConfigurationOutputV1.
        The default number format to be used for items without a number format property.

        :param number_format: The number_format of this SystemConfigurationOutputV1.
        :type: str
        """

        self._number_format = number_format

    @property
    def parallelization_threshold(self):
        """
        Gets the parallelization_threshold of this SystemConfigurationOutputV1.
        The duration, in nanoseconds, above which requests may be parallelized

        :return: The parallelization_threshold of this SystemConfigurationOutputV1.
        :rtype: ScalarValueOutputV1
        """
        return self._parallelization_threshold

    @parallelization_threshold.setter
    def parallelization_threshold(self, parallelization_threshold):
        """
        Sets the parallelization_threshold of this SystemConfigurationOutputV1.
        The duration, in nanoseconds, above which requests may be parallelized

        :param parallelization_threshold: The parallelization_threshold of this SystemConfigurationOutputV1.
        :type: ScalarValueOutputV1
        """

        self._parallelization_threshold = parallelization_threshold

    @property
    def priorities(self):
        """
        Gets the priorities of this SystemConfigurationOutputV1.
        The priorities for metrics, sorted descending by level

        :return: The priorities of this SystemConfigurationOutputV1.
        :rtype: list[PriorityV1]
        """
        return self._priorities

    @priorities.setter
    def priorities(self, priorities):
        """
        Sets the priorities of this SystemConfigurationOutputV1.
        The priorities for metrics, sorted descending by level

        :param priorities: The priorities of this SystemConfigurationOutputV1.
        :type: list[PriorityV1]
        """

        self._priorities = priorities

    @property
    def registration_enabled(self):
        """
        Gets the registration_enabled of this SystemConfigurationOutputV1.
        True if new user registration is available from the Seeq login screen

        :return: The registration_enabled of this SystemConfigurationOutputV1.
        :rtype: bool
        """
        return self._registration_enabled

    @registration_enabled.setter
    def registration_enabled(self, registration_enabled):
        """
        Sets the registration_enabled of this SystemConfigurationOutputV1.
        True if new user registration is available from the Seeq login screen

        :param registration_enabled: The registration_enabled of this SystemConfigurationOutputV1.
        :type: bool
        """

        self._registration_enabled = registration_enabled

    @property
    def restrict_logs(self):
        """
        Gets the restrict_logs of this SystemConfigurationOutputV1.
        True if log access is restricted to admins.

        :return: The restrict_logs of this SystemConfigurationOutputV1.
        :rtype: bool
        """
        return self._restrict_logs

    @restrict_logs.setter
    def restrict_logs(self, restrict_logs):
        """
        Sets the restrict_logs of this SystemConfigurationOutputV1.
        True if log access is restricted to admins.

        :param restrict_logs: The restrict_logs of this SystemConfigurationOutputV1.
        :type: bool
        """

        self._restrict_logs = restrict_logs

    @property
    def status_message(self):
        """
        Gets the status_message of this SystemConfigurationOutputV1.

        :return: The status_message of this SystemConfigurationOutputV1.
        :rtype: str
        """
        return self._status_message

    @status_message.setter
    def status_message(self, status_message):
        """
        Sets the status_message of this SystemConfigurationOutputV1.

        :param status_message: The status_message of this SystemConfigurationOutputV1.
        :type: str
        """

        self._status_message = status_message

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
        if not isinstance(other, SystemConfigurationOutputV1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
