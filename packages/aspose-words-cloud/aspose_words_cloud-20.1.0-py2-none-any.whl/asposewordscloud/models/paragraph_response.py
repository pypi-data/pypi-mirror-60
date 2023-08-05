# coding: utf-8
# -----------------------------------------------------------------------------------
# <copyright company="Aspose" file="ParagraphResponse.py">
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


class ParagraphResponse(object):
    """This response should be returned by the service when handling: GET http://api.aspose.com/v4.0/words/Test.doc/paragraphs/{0}.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'request_id': 'str',
        'paragraph': 'Paragraph'
    }

    attribute_map = {
        'request_id': 'RequestId',
        'paragraph': 'Paragraph'
    }

    def __init__(self, request_id=None, paragraph=None):  # noqa: E501
        """ParagraphResponse - a model defined in Swagger"""  # noqa: E501

        self._request_id = None
        self._paragraph = None
        self.discriminator = None

        if request_id is not None:
            self.request_id = request_id
        if paragraph is not None:
            self.paragraph = paragraph

    @property
    def request_id(self):
        """Gets the request_id of this ParagraphResponse.  # noqa: E501

        Gets or sets request Id.  # noqa: E501

        :return: The request_id of this ParagraphResponse.  # noqa: E501
        :rtype: str
        """
        return self._request_id

    @request_id.setter
    def request_id(self, request_id):
        """Sets the request_id of this ParagraphResponse.

        Gets or sets request Id.  # noqa: E501

        :param request_id: The request_id of this ParagraphResponse.  # noqa: E501
        :type: str
        """
        self._request_id = request_id
    @property
    def paragraph(self):
        """Gets the paragraph of this ParagraphResponse.  # noqa: E501

        Gets or sets paragraph.  # noqa: E501

        :return: The paragraph of this ParagraphResponse.  # noqa: E501
        :rtype: Paragraph
        """
        return self._paragraph

    @paragraph.setter
    def paragraph(self, paragraph):
        """Sets the paragraph of this ParagraphResponse.

        Gets or sets paragraph.  # noqa: E501

        :param paragraph: The paragraph of this ParagraphResponse.  # noqa: E501
        :type: Paragraph
        """
        self._paragraph = paragraph
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
        if not isinstance(other, ParagraphResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
