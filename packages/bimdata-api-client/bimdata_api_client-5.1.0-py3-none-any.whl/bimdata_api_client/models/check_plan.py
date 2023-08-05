# coding: utf-8

"""
    BIMData API

    BIMData API is a tool to interact with your models stored on BIMData’s servers.     Through the API, you can manage your projects, the clouds, upload your IFC files and manage them through endpoints.  # noqa: E501

    The version of the OpenAPI document: v1
    Contact: contact@bimdata.io
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from bimdata_api_client.configuration import Configuration


class CheckPlan(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'id': 'int',
        'name': 'str',
        'description': 'str',
        'created_at': 'datetime',
        'updated_at': 'datetime',
        'rulesets': 'list[Ruleset]',
        'is_default': 'bool'
    }

    attribute_map = {
        'id': 'id',
        'name': 'name',
        'description': 'description',
        'created_at': 'created_at',
        'updated_at': 'updated_at',
        'rulesets': 'rulesets',
        'is_default': 'is_default'
    }

    def __init__(self, id=None, name=None, description=None, created_at=None, updated_at=None, rulesets=None, is_default=None, local_vars_configuration=None):  # noqa: E501
        """CheckPlan - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._name = None
        self._description = None
        self._created_at = None
        self._updated_at = None
        self._rulesets = None
        self._is_default = None
        self.discriminator = None

        if id is not None:
            self.id = id
        self.name = name
        self.description = description
        if created_at is not None:
            self.created_at = created_at
        if updated_at is not None:
            self.updated_at = updated_at
        if rulesets is not None:
            self.rulesets = rulesets
        if is_default is not None:
            self.is_default = is_default

    @property
    def id(self):
        """Gets the id of this CheckPlan.  # noqa: E501


        :return: The id of this CheckPlan.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this CheckPlan.


        :param id: The id of this CheckPlan.  # noqa: E501
        :type: int
        """

        self._id = id

    @property
    def name(self):
        """Gets the name of this CheckPlan.  # noqa: E501


        :return: The name of this CheckPlan.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this CheckPlan.


        :param name: The name of this CheckPlan.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) < 1):
            raise ValueError("Invalid value for `name`, length must be greater than or equal to `1`")  # noqa: E501

        self._name = name

    @property
    def description(self):
        """Gets the description of this CheckPlan.  # noqa: E501


        :return: The description of this CheckPlan.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this CheckPlan.


        :param description: The description of this CheckPlan.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def created_at(self):
        """Gets the created_at of this CheckPlan.  # noqa: E501


        :return: The created_at of this CheckPlan.  # noqa: E501
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this CheckPlan.


        :param created_at: The created_at of this CheckPlan.  # noqa: E501
        :type: datetime
        """

        self._created_at = created_at

    @property
    def updated_at(self):
        """Gets the updated_at of this CheckPlan.  # noqa: E501


        :return: The updated_at of this CheckPlan.  # noqa: E501
        :rtype: datetime
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, updated_at):
        """Sets the updated_at of this CheckPlan.


        :param updated_at: The updated_at of this CheckPlan.  # noqa: E501
        :type: datetime
        """

        self._updated_at = updated_at

    @property
    def rulesets(self):
        """Gets the rulesets of this CheckPlan.  # noqa: E501


        :return: The rulesets of this CheckPlan.  # noqa: E501
        :rtype: list[Ruleset]
        """
        return self._rulesets

    @rulesets.setter
    def rulesets(self, rulesets):
        """Sets the rulesets of this CheckPlan.


        :param rulesets: The rulesets of this CheckPlan.  # noqa: E501
        :type: list[Ruleset]
        """

        self._rulesets = rulesets

    @property
    def is_default(self):
        """Gets the is_default of this CheckPlan.  # noqa: E501


        :return: The is_default of this CheckPlan.  # noqa: E501
        :rtype: bool
        """
        return self._is_default

    @is_default.setter
    def is_default(self, is_default):
        """Sets the is_default of this CheckPlan.


        :param is_default: The is_default of this CheckPlan.  # noqa: E501
        :type: bool
        """

        self._is_default = is_default

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
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
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, CheckPlan):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CheckPlan):
            return True

        return self.to_dict() != other.to_dict()
