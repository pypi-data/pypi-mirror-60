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


class FolderOutputListV1(object):
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
        'content': 'list[FolderContentOutputV1]',
        'has_items_before_offset_present': 'bool',
        'limit': 'int',
        'next': 'str',
        'offset': 'int',
        'prev': 'str',
        'status_message': 'str'
    }

    attribute_map = {
        'content': 'content',
        'has_items_before_offset_present': 'hasItemsBeforeOffsetPresent',
        'limit': 'limit',
        'next': 'next',
        'offset': 'offset',
        'prev': 'prev',
        'status_message': 'statusMessage'
    }

    def __init__(self, content=None, has_items_before_offset_present=False, limit=None, next=None, offset=None, prev=None, status_message=None):
        """
        FolderOutputListV1 - a model defined in Swagger
        """

        self._content = None
        self._has_items_before_offset_present = None
        self._limit = None
        self._next = None
        self._offset = None
        self._prev = None
        self._status_message = None

        if content is not None:
          self.content = content
        if has_items_before_offset_present is not None:
          self.has_items_before_offset_present = has_items_before_offset_present
        if limit is not None:
          self.limit = limit
        if next is not None:
          self.next = next
        if offset is not None:
          self.offset = offset
        if prev is not None:
          self.prev = prev
        if status_message is not None:
          self.status_message = status_message

    @property
    def content(self):
        """
        Gets the content of this FolderOutputListV1.
        The content of the folder

        :return: The content of this FolderOutputListV1.
        :rtype: list[FolderContentOutputV1]
        """
        return self._content

    @content.setter
    def content(self, content):
        """
        Sets the content of this FolderOutputListV1.
        The content of the folder

        :param content: The content of this FolderOutputListV1.
        :type: list[FolderContentOutputV1]
        """

        self._content = content

    @property
    def has_items_before_offset_present(self):
        """
        Gets the has_items_before_offset_present of this FolderOutputListV1.

        :return: The has_items_before_offset_present of this FolderOutputListV1.
        :rtype: bool
        """
        return self._has_items_before_offset_present

    @has_items_before_offset_present.setter
    def has_items_before_offset_present(self, has_items_before_offset_present):
        """
        Sets the has_items_before_offset_present of this FolderOutputListV1.

        :param has_items_before_offset_present: The has_items_before_offset_present of this FolderOutputListV1.
        :type: bool
        """

        self._has_items_before_offset_present = has_items_before_offset_present

    @property
    def limit(self):
        """
        Gets the limit of this FolderOutputListV1.
        The pagination limit, the total number of collection items that will be returned in this page of results

        :return: The limit of this FolderOutputListV1.
        :rtype: int
        """
        return self._limit

    @limit.setter
    def limit(self, limit):
        """
        Sets the limit of this FolderOutputListV1.
        The pagination limit, the total number of collection items that will be returned in this page of results

        :param limit: The limit of this FolderOutputListV1.
        :type: int
        """

        self._limit = limit

    @property
    def next(self):
        """
        Gets the next of this FolderOutputListV1.
        The href of the next set of paginated results

        :return: The next of this FolderOutputListV1.
        :rtype: str
        """
        return self._next

    @next.setter
    def next(self, next):
        """
        Sets the next of this FolderOutputListV1.
        The href of the next set of paginated results

        :param next: The next of this FolderOutputListV1.
        :type: str
        """

        self._next = next

    @property
    def offset(self):
        """
        Gets the offset of this FolderOutputListV1.
        The pagination offset, the index of the first collection item that will be returned in this page of results

        :return: The offset of this FolderOutputListV1.
        :rtype: int
        """
        return self._offset

    @offset.setter
    def offset(self, offset):
        """
        Sets the offset of this FolderOutputListV1.
        The pagination offset, the index of the first collection item that will be returned in this page of results

        :param offset: The offset of this FolderOutputListV1.
        :type: int
        """

        self._offset = offset

    @property
    def prev(self):
        """
        Gets the prev of this FolderOutputListV1.
        The href of the previous set of paginated results

        :return: The prev of this FolderOutputListV1.
        :rtype: str
        """
        return self._prev

    @prev.setter
    def prev(self, prev):
        """
        Sets the prev of this FolderOutputListV1.
        The href of the previous set of paginated results

        :param prev: The prev of this FolderOutputListV1.
        :type: str
        """

        self._prev = prev

    @property
    def status_message(self):
        """
        Gets the status_message of this FolderOutputListV1.
        A plain language status message with information about any issues that may have been encountered during an operation. Null if the status message has not been set.

        :return: The status_message of this FolderOutputListV1.
        :rtype: str
        """
        return self._status_message

    @status_message.setter
    def status_message(self, status_message):
        """
        Sets the status_message of this FolderOutputListV1.
        A plain language status message with information about any issues that may have been encountered during an operation. Null if the status message has not been set.

        :param status_message: The status_message of this FolderOutputListV1.
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
        if not isinstance(other, FolderOutputListV1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
