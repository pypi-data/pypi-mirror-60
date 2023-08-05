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


class FolderInputV1(object):
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
        'description': 'str',
        'name': 'str',
        'owner_id': 'str',
        'parent_folder_id': 'str'
    }

    attribute_map = {
        'description': 'description',
        'name': 'name',
        'owner_id': 'ownerId',
        'parent_folder_id': 'parentFolderId'
    }

    def __init__(self, description=None, name=None, owner_id=None, parent_folder_id=None):
        """
        FolderInputV1 - a model defined in Swagger
        """

        self._description = None
        self._name = None
        self._owner_id = None
        self._parent_folder_id = None

        if description is not None:
          self.description = description
        if name is not None:
          self.name = name
        if owner_id is not None:
          self.owner_id = owner_id
        if parent_folder_id is not None:
          self.parent_folder_id = parent_folder_id

    @property
    def description(self):
        """
        Gets the description of this FolderInputV1.
        Clarifying information or other plain language description of this asset. An input of just whitespace is equivalent to a null input.

        :return: The description of this FolderInputV1.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this FolderInputV1.
        Clarifying information or other plain language description of this asset. An input of just whitespace is equivalent to a null input.

        :param description: The description of this FolderInputV1.
        :type: str
        """

        self._description = description

    @property
    def name(self):
        """
        Gets the name of this FolderInputV1.
        Human readable name. Null or whitespace names are not permitted.

        :return: The name of this FolderInputV1.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this FolderInputV1.
        Human readable name. Null or whitespace names are not permitted.

        :param name: The name of this FolderInputV1.
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")

        self._name = name

    @property
    def owner_id(self):
        """
        Gets the owner_id of this FolderInputV1.
        The ID of the User that owns this folder. If omitted when creating a new Folder, the authenticated user is used by default. Only administrators can set this value.

        :return: The owner_id of this FolderInputV1.
        :rtype: str
        """
        return self._owner_id

    @owner_id.setter
    def owner_id(self, owner_id):
        """
        Sets the owner_id of this FolderInputV1.
        The ID of the User that owns this folder. If omitted when creating a new Folder, the authenticated user is used by default. Only administrators can set this value.

        :param owner_id: The owner_id of this FolderInputV1.
        :type: str
        """

        self._owner_id = owner_id

    @property
    def parent_folder_id(self):
        """
        Gets the parent_folder_id of this FolderInputV1.
        The ID of the parent folder for this folder. If omitted when creating a new Folder, a root folder will be created.

        :return: The parent_folder_id of this FolderInputV1.
        :rtype: str
        """
        return self._parent_folder_id

    @parent_folder_id.setter
    def parent_folder_id(self, parent_folder_id):
        """
        Sets the parent_folder_id of this FolderInputV1.
        The ID of the parent folder for this folder. If omitted when creating a new Folder, a root folder will be created.

        :param parent_folder_id: The parent_folder_id of this FolderInputV1.
        :type: str
        """

        self._parent_folder_id = parent_folder_id

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
        if not isinstance(other, FolderInputV1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
