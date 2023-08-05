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


class ScreenshotJobInputV1(object):
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
        'condition_id': 'str',
        'content_selector': 'str',
        'document_id': 'str',
        'height': 'int',
        'period': 'str',
        'range_formula': 'str',
        'timezone': 'str',
        'width': 'int',
        'worksheet_id': 'str',
        'workstep_id': 'str'
    }

    attribute_map = {
        'condition_id': 'conditionId',
        'content_selector': 'contentSelector',
        'document_id': 'documentId',
        'height': 'height',
        'period': 'period',
        'range_formula': 'rangeFormula',
        'timezone': 'timezone',
        'width': 'width',
        'worksheet_id': 'worksheetId',
        'workstep_id': 'workstepId'
    }

    def __init__(self, condition_id=None, content_selector=None, document_id=None, height=None, period=None, range_formula=None, timezone=None, width=None, worksheet_id=None, workstep_id=None):
        """
        ScreenshotJobInputV1 - a model defined in Swagger
        """

        self._condition_id = None
        self._content_selector = None
        self._document_id = None
        self._height = None
        self._period = None
        self._range_formula = None
        self._timezone = None
        self._width = None
        self._worksheet_id = None
        self._workstep_id = None

        if condition_id is not None:
          self.condition_id = condition_id
        if content_selector is not None:
          self.content_selector = content_selector
        if document_id is not None:
          self.document_id = document_id
        if height is not None:
          self.height = height
        if period is not None:
          self.period = period
        if range_formula is not None:
          self.range_formula = range_formula
        if timezone is not None:
          self.timezone = timezone
        if width is not None:
          self.width = width
        if worksheet_id is not None:
          self.worksheet_id = worksheet_id
        if workstep_id is not None:
          self.workstep_id = workstep_id

    @property
    def condition_id(self):
        """
        Gets the condition_id of this ScreenshotJobInputV1.
        The ID of a condition that can be used to provide a $condition variable to the rangeFormula if it is condition-based.

        :return: The condition_id of this ScreenshotJobInputV1.
        :rtype: str
        """
        return self._condition_id

    @condition_id.setter
    def condition_id(self, condition_id):
        """
        Sets the condition_id of this ScreenshotJobInputV1.
        The ID of a condition that can be used to provide a $condition variable to the rangeFormula if it is condition-based.

        :param condition_id: The condition_id of this ScreenshotJobInputV1.
        :type: str
        """

        self._condition_id = condition_id

    @property
    def content_selector(self):
        """
        Gets the content_selector of this ScreenshotJobInputV1.
        A CSS selector that can be used to capture only a certain page element

        :return: The content_selector of this ScreenshotJobInputV1.
        :rtype: str
        """
        return self._content_selector

    @content_selector.setter
    def content_selector(self, content_selector):
        """
        Sets the content_selector of this ScreenshotJobInputV1.
        A CSS selector that can be used to capture only a certain page element

        :param content_selector: The content_selector of this ScreenshotJobInputV1.
        :type: str
        """

        self._content_selector = content_selector

    @property
    def document_id(self):
        """
        Gets the document_id of this ScreenshotJobInputV1.
        The ID of the document, if present, which spawned this job

        :return: The document_id of this ScreenshotJobInputV1.
        :rtype: str
        """
        return self._document_id

    @document_id.setter
    def document_id(self, document_id):
        """
        Sets the document_id of this ScreenshotJobInputV1.
        The ID of the document, if present, which spawned this job

        :param document_id: The document_id of this ScreenshotJobInputV1.
        :type: str
        """

        self._document_id = document_id

    @property
    def height(self):
        """
        Gets the height of this ScreenshotJobInputV1.
        The height of the screenshot

        :return: The height of this ScreenshotJobInputV1.
        :rtype: int
        """
        return self._height

    @height.setter
    def height(self, height):
        """
        Sets the height of this ScreenshotJobInputV1.
        The height of the screenshot

        :param height: The height of this ScreenshotJobInputV1.
        :type: int
        """
        if height is None:
            raise ValueError("Invalid value for `height`, must not be `None`")

        self._height = height

    @property
    def period(self):
        """
        Gets the period of this ScreenshotJobInputV1.
        The duration between each screenshot. Example: 5min

        :return: The period of this ScreenshotJobInputV1.
        :rtype: str
        """
        return self._period

    @period.setter
    def period(self, period):
        """
        Sets the period of this ScreenshotJobInputV1.
        The duration between each screenshot. Example: 5min

        :param period: The period of this ScreenshotJobInputV1.
        :type: str
        """
        if period is None:
            raise ValueError("Invalid value for `period`, must not be `None`")

        self._period = period

    @property
    def range_formula(self):
        """
        Gets the range_formula of this ScreenshotJobInputV1.
        A Seeq formula that is used to determine the date range used for the screenshot. It must produce a capsule and will be passed $now, set to the current time, as an argument. Example: capsule($now - 24h, $now)

        :return: The range_formula of this ScreenshotJobInputV1.
        :rtype: str
        """
        return self._range_formula

    @range_formula.setter
    def range_formula(self, range_formula):
        """
        Sets the range_formula of this ScreenshotJobInputV1.
        A Seeq formula that is used to determine the date range used for the screenshot. It must produce a capsule and will be passed $now, set to the current time, as an argument. Example: capsule($now - 24h, $now)

        :param range_formula: The range_formula of this ScreenshotJobInputV1.
        :type: str
        """
        if range_formula is None:
            raise ValueError("Invalid value for `range_formula`, must not be `None`")

        self._range_formula = range_formula

    @property
    def timezone(self):
        """
        Gets the timezone of this ScreenshotJobInputV1.
        The timezone to use for the screenshot. If not provided the timezone of the server will be used

        :return: The timezone of this ScreenshotJobInputV1.
        :rtype: str
        """
        return self._timezone

    @timezone.setter
    def timezone(self, timezone):
        """
        Sets the timezone of this ScreenshotJobInputV1.
        The timezone to use for the screenshot. If not provided the timezone of the server will be used

        :param timezone: The timezone of this ScreenshotJobInputV1.
        :type: str
        """

        self._timezone = timezone

    @property
    def width(self):
        """
        Gets the width of this ScreenshotJobInputV1.
        The width of the screenshot

        :return: The width of this ScreenshotJobInputV1.
        :rtype: int
        """
        return self._width

    @width.setter
    def width(self, width):
        """
        Sets the width of this ScreenshotJobInputV1.
        The width of the screenshot

        :param width: The width of this ScreenshotJobInputV1.
        :type: int
        """
        if width is None:
            raise ValueError("Invalid value for `width`, must not be `None`")

        self._width = width

    @property
    def worksheet_id(self):
        """
        Gets the worksheet_id of this ScreenshotJobInputV1.
        The worksheet id to capture

        :return: The worksheet_id of this ScreenshotJobInputV1.
        :rtype: str
        """
        return self._worksheet_id

    @worksheet_id.setter
    def worksheet_id(self, worksheet_id):
        """
        Sets the worksheet_id of this ScreenshotJobInputV1.
        The worksheet id to capture

        :param worksheet_id: The worksheet_id of this ScreenshotJobInputV1.
        :type: str
        """
        if worksheet_id is None:
            raise ValueError("Invalid value for `worksheet_id`, must not be `None`")

        self._worksheet_id = worksheet_id

    @property
    def workstep_id(self):
        """
        Gets the workstep_id of this ScreenshotJobInputV1.
        The workstep id to capture. If not provided the latest for the worksheet will be used

        :return: The workstep_id of this ScreenshotJobInputV1.
        :rtype: str
        """
        return self._workstep_id

    @workstep_id.setter
    def workstep_id(self, workstep_id):
        """
        Sets the workstep_id of this ScreenshotJobInputV1.
        The workstep id to capture. If not provided the latest for the worksheet will be used

        :param workstep_id: The workstep_id of this ScreenshotJobInputV1.
        :type: str
        """

        self._workstep_id = workstep_id

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
        if not isinstance(other, ScreenshotJobInputV1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
