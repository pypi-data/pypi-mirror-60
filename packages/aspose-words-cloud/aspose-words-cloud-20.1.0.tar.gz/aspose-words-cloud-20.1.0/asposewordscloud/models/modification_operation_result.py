# coding: utf-8
# -----------------------------------------------------------------------------------
# <copyright company="Aspose" file="ModificationOperationResult.py">
#   Copyright (c) 2019 Aspose.Words for Cloud
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------
import pprint
import re  # noqa: F401

import six


class ModificationOperationResult(object):
    """result of the operation which modifies the original document and saves the result.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'source': 'FileLink',
        'dest': 'FileLink'
    }

    attribute_map = {
        'source': 'Source',
        'dest': 'Dest'
    }

    def __init__(self, source=None, dest=None):  # noqa: E501
        """ModificationOperationResult - a model defined in Swagger"""  # noqa: E501

        self._source = None
        self._dest = None
        self.discriminator = None

        if source is not None:
            self.source = source
        if dest is not None:
            self.dest = dest

    @property
    def source(self):
        """Gets the source of this ModificationOperationResult.  # noqa: E501

        Gets or sets link to the source document (source for the modification operation).  # noqa: E501

        :return: The source of this ModificationOperationResult.  # noqa: E501
        :rtype: FileLink
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this ModificationOperationResult.

        Gets or sets link to the source document (source for the modification operation).  # noqa: E501

        :param source: The source of this ModificationOperationResult.  # noqa: E501
        :type: FileLink
        """
        self._source = source
    @property
    def dest(self):
        """Gets the dest of this ModificationOperationResult.  # noqa: E501

        Gets or sets link to the dest document (result of the modification operation).  # noqa: E501

        :return: The dest of this ModificationOperationResult.  # noqa: E501
        :rtype: FileLink
        """
        return self._dest

    @dest.setter
    def dest(self, dest):
        """Sets the dest of this ModificationOperationResult.

        Gets or sets link to the dest document (result of the modification operation).  # noqa: E501

        :param dest: The dest of this ModificationOperationResult.  # noqa: E501
        :type: FileLink
        """
        self._dest = dest
    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
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
        if not isinstance(other, ModificationOperationResult):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
