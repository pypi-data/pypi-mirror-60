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


class FormulaCompileOutputV1(object):
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
        'metadata': 'dict(str, str)',
        'return_type': 'str',
        'status_message': 'str',
        'warning_count': 'int',
        'warning_logs': 'list[FormulaLogV1]'
    }

    attribute_map = {
        'metadata': 'metadata',
        'return_type': 'returnType',
        'status_message': 'statusMessage',
        'warning_count': 'warningCount',
        'warning_logs': 'warningLogs'
    }

    def __init__(self, metadata=None, return_type=None, status_message=None, warning_count=None, warning_logs=None):
        """
        FormulaCompileOutputV1 - a model defined in Swagger
        """

        self._metadata = None
        self._return_type = None
        self._status_message = None
        self._warning_count = None
        self._warning_logs = None

        if metadata is not None:
          self.metadata = metadata
        if return_type is not None:
          self.return_type = return_type
        if status_message is not None:
          self.status_message = status_message
        if warning_count is not None:
          self.warning_count = warning_count
        if warning_logs is not None:
          self.warning_logs = warning_logs

    @property
    def metadata(self):
        """
        Gets the metadata of this FormulaCompileOutputV1.
        Metadata describing the compiled formula's result

        :return: The metadata of this FormulaCompileOutputV1.
        :rtype: dict(str, str)
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """
        Sets the metadata of this FormulaCompileOutputV1.
        Metadata describing the compiled formula's result

        :param metadata: The metadata of this FormulaCompileOutputV1.
        :type: dict(str, str)
        """

        self._metadata = metadata

    @property
    def return_type(self):
        """
        Gets the return_type of this FormulaCompileOutputV1.
        The data type of the compiled formula's result

        :return: The return_type of this FormulaCompileOutputV1.
        :rtype: str
        """
        return self._return_type

    @return_type.setter
    def return_type(self, return_type):
        """
        Sets the return_type of this FormulaCompileOutputV1.
        The data type of the compiled formula's result

        :param return_type: The return_type of this FormulaCompileOutputV1.
        :type: str
        """

        self._return_type = return_type

    @property
    def status_message(self):
        """
        Gets the status_message of this FormulaCompileOutputV1.
        A plain language status message with information about any issues that may have been encountered during an operation. Null if the status message has not been set.

        :return: The status_message of this FormulaCompileOutputV1.
        :rtype: str
        """
        return self._status_message

    @status_message.setter
    def status_message(self, status_message):
        """
        Sets the status_message of this FormulaCompileOutputV1.
        A plain language status message with information about any issues that may have been encountered during an operation. Null if the status message has not been set.

        :param status_message: The status_message of this FormulaCompileOutputV1.
        :type: str
        """

        self._status_message = status_message

    @property
    def warning_count(self):
        """
        Gets the warning_count of this FormulaCompileOutputV1.
        The total number of warnings that have occurred

        :return: The warning_count of this FormulaCompileOutputV1.
        :rtype: int
        """
        return self._warning_count

    @warning_count.setter
    def warning_count(self, warning_count):
        """
        Sets the warning_count of this FormulaCompileOutputV1.
        The total number of warnings that have occurred

        :param warning_count: The warning_count of this FormulaCompileOutputV1.
        :type: int
        """

        self._warning_count = warning_count

    @property
    def warning_logs(self):
        """
        Gets the warning_logs of this FormulaCompileOutputV1.
        The Formula warning logs, which includes the text, line number, and column number where the warning occurred in addition to the warning details

        :return: The warning_logs of this FormulaCompileOutputV1.
        :rtype: list[FormulaLogV1]
        """
        return self._warning_logs

    @warning_logs.setter
    def warning_logs(self, warning_logs):
        """
        Sets the warning_logs of this FormulaCompileOutputV1.
        The Formula warning logs, which includes the text, line number, and column number where the warning occurred in addition to the warning details

        :param warning_logs: The warning_logs of this FormulaCompileOutputV1.
        :type: list[FormulaLogV1]
        """

        self._warning_logs = warning_logs

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
        if not isinstance(other, FormulaCompileOutputV1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
