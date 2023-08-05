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


class AceInputV1(object):
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
        'identity_id': 'str',
        'permissions': 'PermissionsV1'
    }

    attribute_map = {
        'identity_id': 'identityId',
        'permissions': 'permissions'
    }

    def __init__(self, identity_id=None, permissions=None):
        """
        AceInputV1 - a model defined in Swagger
        """

        self._identity_id = None
        self._permissions = None

        if identity_id is not None:
          self.identity_id = identity_id
        if permissions is not None:
          self.permissions = permissions

    @property
    def identity_id(self):
        """
        Gets the identity_id of this AceInputV1.
        ID of the identity. Can be null or empty.

        :return: The identity_id of this AceInputV1.
        :rtype: str
        """
        return self._identity_id

    @identity_id.setter
    def identity_id(self, identity_id):
        """
        Sets the identity_id of this AceInputV1.
        ID of the identity. Can be null or empty.

        :param identity_id: The identity_id of this AceInputV1.
        :type: str
        """
        if identity_id is None:
            raise ValueError("Invalid value for `identity_id`, must not be `None`")

        self._identity_id = identity_id

    @property
    def permissions(self):
        """
        Gets the permissions of this AceInputV1.
        Permissions for this Access Control Entry.

        :return: The permissions of this AceInputV1.
        :rtype: PermissionsV1
        """
        return self._permissions

    @permissions.setter
    def permissions(self, permissions):
        """
        Sets the permissions of this AceInputV1.
        Permissions for this Access Control Entry.

        :param permissions: The permissions of this AceInputV1.
        :type: PermissionsV1
        """
        if permissions is None:
            raise ValueError("Invalid value for `permissions`, must not be `None`")

        self._permissions = permissions

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
        if not isinstance(other, AceInputV1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
