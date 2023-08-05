# coding: utf-8
# -----------------------------------------------------------------------------------
# <copyright company="Aspose" file="SaveResult.py">
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


class SaveResult(object):
    """Result of saving.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'source_document': 'FileLink',
        'dest_document': 'FileLink',
        'additional_items': 'list[FileLink]'
    }

    attribute_map = {
        'source_document': 'SourceDocument',
        'dest_document': 'DestDocument',
        'additional_items': 'AdditionalItems'
    }

    def __init__(self, source_document=None, dest_document=None, additional_items=None):  # noqa: E501
        """SaveResult - a model defined in Swagger"""  # noqa: E501

        self._source_document = None
        self._dest_document = None
        self._additional_items = None
        self.discriminator = None

        if source_document is not None:
            self.source_document = source_document
        if dest_document is not None:
            self.dest_document = dest_document
        if additional_items is not None:
            self.additional_items = additional_items

    @property
    def source_document(self):
        """Gets the source_document of this SaveResult.  # noqa: E501

        Gets or sets link to source document.  # noqa: E501

        :return: The source_document of this SaveResult.  # noqa: E501
        :rtype: FileLink
        """
        return self._source_document

    @source_document.setter
    def source_document(self, source_document):
        """Sets the source_document of this SaveResult.

        Gets or sets link to source document.  # noqa: E501

        :param source_document: The source_document of this SaveResult.  # noqa: E501
        :type: FileLink
        """
        self._source_document = source_document
    @property
    def dest_document(self):
        """Gets the dest_document of this SaveResult.  # noqa: E501

        Gets or sets link to destination document.  # noqa: E501

        :return: The dest_document of this SaveResult.  # noqa: E501
        :rtype: FileLink
        """
        return self._dest_document

    @dest_document.setter
    def dest_document(self, dest_document):
        """Sets the dest_document of this SaveResult.

        Gets or sets link to destination document.  # noqa: E501

        :param dest_document: The dest_document of this SaveResult.  # noqa: E501
        :type: FileLink
        """
        self._dest_document = dest_document
    @property
    def additional_items(self):
        """Gets the additional_items of this SaveResult.  # noqa: E501

        Gets or sets links to additional items (css, images etc).  # noqa: E501

        :return: The additional_items of this SaveResult.  # noqa: E501
        :rtype: list[FileLink]
        """
        return self._additional_items

    @additional_items.setter
    def additional_items(self, additional_items):
        """Sets the additional_items of this SaveResult.

        Gets or sets links to additional items (css, images etc).  # noqa: E501

        :param additional_items: The additional_items of this SaveResult.  # noqa: E501
        :type: list[FileLink]
        """
        self._additional_items = additional_items
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
        if not isinstance(other, SaveResult):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
