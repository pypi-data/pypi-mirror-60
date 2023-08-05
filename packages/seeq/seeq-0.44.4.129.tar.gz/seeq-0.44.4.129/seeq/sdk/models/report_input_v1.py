# coding: utf-8

"""
    Seeq REST API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: 0.44.04
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class ReportInputV1(object):
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
        'format': 'str',
        'items': 'list[ReportInputItemV1]',
        'title': 'str'
    }

    attribute_map = {
        'format': 'format',
        'items': 'items',
        'title': 'title'
    }

    def __init__(self, format=None, items=None, title=None):
        """
        ReportInputV1 - a model defined in Swagger
        """

        self._format = None
        self._items = None
        self._title = None

        if format is not None:
          self.format = format
        if items is not None:
          self.items = items
        if title is not None:
          self.title = title

    @property
    def format(self):
        """
        Gets the format of this ReportInputV1.
        Report format to generate. Currently only 'pptx' is supported.

        :return: The format of this ReportInputV1.
        :rtype: str
        """
        return self._format

    @format.setter
    def format(self, format):
        """
        Sets the format of this ReportInputV1.
        Report format to generate. Currently only 'pptx' is supported.

        :param format: The format of this ReportInputV1.
        :type: str
        """
        if format is None:
            raise ValueError("Invalid value for `format`, must not be `None`")

        self._format = format

    @property
    def items(self):
        """
        Gets the items of this ReportInputV1.
        A list of Worksheets to include in the report

        :return: The items of this ReportInputV1.
        :rtype: list[ReportInputItemV1]
        """
        return self._items

    @items.setter
    def items(self, items):
        """
        Sets the items of this ReportInputV1.
        A list of Worksheets to include in the report

        :param items: The items of this ReportInputV1.
        :type: list[ReportInputItemV1]
        """
        if items is None:
            raise ValueError("Invalid value for `items`, must not be `None`")

        self._items = items

    @property
    def title(self):
        """
        Gets the title of this ReportInputV1.
        Title for the report. If false or unspecified, the report has no title

        :return: The title of this ReportInputV1.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """
        Sets the title of this ReportInputV1.
        Title for the report. If false or unspecified, the report has no title

        :param title: The title of this ReportInputV1.
        :type: str
        """

        self._title = title

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
        if not isinstance(other, ReportInputV1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
