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


class Ifc(object):
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
        'creator': 'User',
        'status': 'str',
        'source': 'str',
        'created_at': 'datetime',
        'updated_at': 'datetime',
        'document_id': 'str',
        'document': 'Document',
        'structure_file': 'str',
        'systems_file': 'str',
        'map_file': 'str',
        'gltf_file': 'str',
        'bvh_tree_file': 'str',
        'viewer_360_file': 'str',
        'xkt_file': 'str',
        'project_id': 'str',
        'world_position': 'list[float]',
        'errors': 'list[str]',
        'warnings': 'list[str]'
    }

    attribute_map = {
        'id': 'id',
        'name': 'name',
        'creator': 'creator',
        'status': 'status',
        'source': 'source',
        'created_at': 'created_at',
        'updated_at': 'updated_at',
        'document_id': 'document_id',
        'document': 'document',
        'structure_file': 'structure_file',
        'systems_file': 'systems_file',
        'map_file': 'map_file',
        'gltf_file': 'gltf_file',
        'bvh_tree_file': 'bvh_tree_file',
        'viewer_360_file': 'viewer_360_file',
        'xkt_file': 'xkt_file',
        'project_id': 'project_id',
        'world_position': 'world_position',
        'errors': 'errors',
        'warnings': 'warnings'
    }

    def __init__(self, id=None, name=None, creator=None, status=None, source=None, created_at=None, updated_at=None, document_id=None, document=None, structure_file=None, systems_file=None, map_file=None, gltf_file=None, bvh_tree_file=None, viewer_360_file=None, xkt_file=None, project_id=None, world_position=None, errors=None, warnings=None, local_vars_configuration=None):  # noqa: E501
        """Ifc - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._name = None
        self._creator = None
        self._status = None
        self._source = None
        self._created_at = None
        self._updated_at = None
        self._document_id = None
        self._document = None
        self._structure_file = None
        self._systems_file = None
        self._map_file = None
        self._gltf_file = None
        self._bvh_tree_file = None
        self._viewer_360_file = None
        self._xkt_file = None
        self._project_id = None
        self._world_position = None
        self._errors = None
        self._warnings = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if name is not None:
            self.name = name
        if creator is not None:
            self.creator = creator
        if status is not None:
            self.status = status
        if source is not None:
            self.source = source
        if created_at is not None:
            self.created_at = created_at
        if updated_at is not None:
            self.updated_at = updated_at
        if document_id is not None:
            self.document_id = document_id
        if document is not None:
            self.document = document
        if structure_file is not None:
            self.structure_file = structure_file
        if systems_file is not None:
            self.systems_file = systems_file
        if map_file is not None:
            self.map_file = map_file
        if gltf_file is not None:
            self.gltf_file = gltf_file
        if bvh_tree_file is not None:
            self.bvh_tree_file = bvh_tree_file
        if viewer_360_file is not None:
            self.viewer_360_file = viewer_360_file
        if xkt_file is not None:
            self.xkt_file = xkt_file
        if project_id is not None:
            self.project_id = project_id
        self.world_position = world_position
        if errors is not None:
            self.errors = errors
        if warnings is not None:
            self.warnings = warnings

    @property
    def id(self):
        """Gets the id of this Ifc.  # noqa: E501


        :return: The id of this Ifc.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Ifc.


        :param id: The id of this Ifc.  # noqa: E501
        :type: int
        """

        self._id = id

    @property
    def name(self):
        """Gets the name of this Ifc.  # noqa: E501


        :return: The name of this Ifc.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Ifc.


        :param name: The name of this Ifc.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def creator(self):
        """Gets the creator of this Ifc.  # noqa: E501


        :return: The creator of this Ifc.  # noqa: E501
        :rtype: User
        """
        return self._creator

    @creator.setter
    def creator(self, creator):
        """Sets the creator of this Ifc.


        :param creator: The creator of this Ifc.  # noqa: E501
        :type: User
        """

        self._creator = creator

    @property
    def status(self):
        """Gets the status of this Ifc.  # noqa: E501


        :return: The status of this Ifc.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this Ifc.


        :param status: The status of this Ifc.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def source(self):
        """Gets the source of this Ifc.  # noqa: E501


        :return: The source of this Ifc.  # noqa: E501
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this Ifc.


        :param source: The source of this Ifc.  # noqa: E501
        :type: str
        """
        allowed_values = ["UPLOAD", "SPLIT", "MERGE", "EXPORT"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and source not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `source` ({0}), must be one of {1}"  # noqa: E501
                .format(source, allowed_values)
            )

        self._source = source

    @property
    def created_at(self):
        """Gets the created_at of this Ifc.  # noqa: E501


        :return: The created_at of this Ifc.  # noqa: E501
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this Ifc.


        :param created_at: The created_at of this Ifc.  # noqa: E501
        :type: datetime
        """

        self._created_at = created_at

    @property
    def updated_at(self):
        """Gets the updated_at of this Ifc.  # noqa: E501


        :return: The updated_at of this Ifc.  # noqa: E501
        :rtype: datetime
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, updated_at):
        """Sets the updated_at of this Ifc.


        :param updated_at: The updated_at of this Ifc.  # noqa: E501
        :type: datetime
        """

        self._updated_at = updated_at

    @property
    def document_id(self):
        """Gets the document_id of this Ifc.  # noqa: E501


        :return: The document_id of this Ifc.  # noqa: E501
        :rtype: str
        """
        return self._document_id

    @document_id.setter
    def document_id(self, document_id):
        """Sets the document_id of this Ifc.


        :param document_id: The document_id of this Ifc.  # noqa: E501
        :type: str
        """

        self._document_id = document_id

    @property
    def document(self):
        """Gets the document of this Ifc.  # noqa: E501


        :return: The document of this Ifc.  # noqa: E501
        :rtype: Document
        """
        return self._document

    @document.setter
    def document(self, document):
        """Sets the document of this Ifc.


        :param document: The document of this Ifc.  # noqa: E501
        :type: Document
        """

        self._document = document

    @property
    def structure_file(self):
        """Gets the structure_file of this Ifc.  # noqa: E501


        :return: The structure_file of this Ifc.  # noqa: E501
        :rtype: str
        """
        return self._structure_file

    @structure_file.setter
    def structure_file(self, structure_file):
        """Sets the structure_file of this Ifc.


        :param structure_file: The structure_file of this Ifc.  # noqa: E501
        :type: str
        """

        self._structure_file = structure_file

    @property
    def systems_file(self):
        """Gets the systems_file of this Ifc.  # noqa: E501


        :return: The systems_file of this Ifc.  # noqa: E501
        :rtype: str
        """
        return self._systems_file

    @systems_file.setter
    def systems_file(self, systems_file):
        """Sets the systems_file of this Ifc.


        :param systems_file: The systems_file of this Ifc.  # noqa: E501
        :type: str
        """

        self._systems_file = systems_file

    @property
    def map_file(self):
        """Gets the map_file of this Ifc.  # noqa: E501


        :return: The map_file of this Ifc.  # noqa: E501
        :rtype: str
        """
        return self._map_file

    @map_file.setter
    def map_file(self, map_file):
        """Sets the map_file of this Ifc.


        :param map_file: The map_file of this Ifc.  # noqa: E501
        :type: str
        """

        self._map_file = map_file

    @property
    def gltf_file(self):
        """Gets the gltf_file of this Ifc.  # noqa: E501


        :return: The gltf_file of this Ifc.  # noqa: E501
        :rtype: str
        """
        return self._gltf_file

    @gltf_file.setter
    def gltf_file(self, gltf_file):
        """Sets the gltf_file of this Ifc.


        :param gltf_file: The gltf_file of this Ifc.  # noqa: E501
        :type: str
        """

        self._gltf_file = gltf_file

    @property
    def bvh_tree_file(self):
        """Gets the bvh_tree_file of this Ifc.  # noqa: E501


        :return: The bvh_tree_file of this Ifc.  # noqa: E501
        :rtype: str
        """
        return self._bvh_tree_file

    @bvh_tree_file.setter
    def bvh_tree_file(self, bvh_tree_file):
        """Sets the bvh_tree_file of this Ifc.


        :param bvh_tree_file: The bvh_tree_file of this Ifc.  # noqa: E501
        :type: str
        """

        self._bvh_tree_file = bvh_tree_file

    @property
    def viewer_360_file(self):
        """Gets the viewer_360_file of this Ifc.  # noqa: E501


        :return: The viewer_360_file of this Ifc.  # noqa: E501
        :rtype: str
        """
        return self._viewer_360_file

    @viewer_360_file.setter
    def viewer_360_file(self, viewer_360_file):
        """Sets the viewer_360_file of this Ifc.


        :param viewer_360_file: The viewer_360_file of this Ifc.  # noqa: E501
        :type: str
        """

        self._viewer_360_file = viewer_360_file

    @property
    def xkt_file(self):
        """Gets the xkt_file of this Ifc.  # noqa: E501


        :return: The xkt_file of this Ifc.  # noqa: E501
        :rtype: str
        """
        return self._xkt_file

    @xkt_file.setter
    def xkt_file(self, xkt_file):
        """Sets the xkt_file of this Ifc.


        :param xkt_file: The xkt_file of this Ifc.  # noqa: E501
        :type: str
        """

        self._xkt_file = xkt_file

    @property
    def project_id(self):
        """Gets the project_id of this Ifc.  # noqa: E501


        :return: The project_id of this Ifc.  # noqa: E501
        :rtype: str
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Sets the project_id of this Ifc.


        :param project_id: The project_id of this Ifc.  # noqa: E501
        :type: str
        """

        self._project_id = project_id

    @property
    def world_position(self):
        """Gets the world_position of this Ifc.  # noqa: E501

        [x,y,z] array of the position of the local_placement in world coordinates  # noqa: E501

        :return: The world_position of this Ifc.  # noqa: E501
        :rtype: list[float]
        """
        return self._world_position

    @world_position.setter
    def world_position(self, world_position):
        """Sets the world_position of this Ifc.

        [x,y,z] array of the position of the local_placement in world coordinates  # noqa: E501

        :param world_position: The world_position of this Ifc.  # noqa: E501
        :type: list[float]
        """

        self._world_position = world_position

    @property
    def errors(self):
        """Gets the errors of this Ifc.  # noqa: E501

        List of errors that happened during IFC processing  # noqa: E501

        :return: The errors of this Ifc.  # noqa: E501
        :rtype: list[str]
        """
        return self._errors

    @errors.setter
    def errors(self, errors):
        """Sets the errors of this Ifc.

        List of errors that happened during IFC processing  # noqa: E501

        :param errors: The errors of this Ifc.  # noqa: E501
        :type: list[str]
        """

        self._errors = errors

    @property
    def warnings(self):
        """Gets the warnings of this Ifc.  # noqa: E501

        List of warnings that happened during IFC processing  # noqa: E501

        :return: The warnings of this Ifc.  # noqa: E501
        :rtype: list[str]
        """
        return self._warnings

    @warnings.setter
    def warnings(self, warnings):
        """Sets the warnings of this Ifc.

        List of warnings that happened during IFC processing  # noqa: E501

        :param warnings: The warnings of this Ifc.  # noqa: E501
        :type: list[str]
        """

        self._warnings = warnings

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
        if not isinstance(other, Ifc):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Ifc):
            return True

        return self.to_dict() != other.to_dict()
