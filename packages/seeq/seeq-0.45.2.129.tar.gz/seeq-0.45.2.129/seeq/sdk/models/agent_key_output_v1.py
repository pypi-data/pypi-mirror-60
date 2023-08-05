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


class AgentKeyOutputV1(object):
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
        'agent_key': 'str'
    }

    attribute_map = {
        'agent_key': 'agentKey'
    }

    def __init__(self, agent_key=None):
        """
        AgentKeyOutputV1 - a model defined in Swagger
        """

        self._agent_key = None

        if agent_key is not None:
          self.agent_key = agent_key

    @property
    def agent_key(self):
        """
        Gets the agent_key of this AgentKeyOutputV1.
        Seeq's agent.key value

        :return: The agent_key of this AgentKeyOutputV1.
        :rtype: str
        """
        return self._agent_key

    @agent_key.setter
    def agent_key(self, agent_key):
        """
        Sets the agent_key of this AgentKeyOutputV1.
        Seeq's agent.key value

        :param agent_key: The agent_key of this AgentKeyOutputV1.
        :type: str
        """

        self._agent_key = agent_key

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
        if not isinstance(other, AgentKeyOutputV1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
