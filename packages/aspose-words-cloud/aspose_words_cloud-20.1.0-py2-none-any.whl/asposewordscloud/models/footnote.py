# coding: utf-8
# -----------------------------------------------------------------------------------
# <copyright company="Aspose" file="Footnote.py">
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


class Footnote(object):
    """Footnote.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'link': 'WordsApiLink',
        'node_id': 'str',
        'content': 'StoryChildNodes',
        'footnote_type': 'str',
        'position': 'DocumentPosition',
        'reference_mark': 'str',
        'text': 'str'
    }

    attribute_map = {
        'link': 'link',
        'node_id': 'NodeId',
        'content': 'Content',
        'footnote_type': 'FootnoteType',
        'position': 'Position',
        'reference_mark': 'ReferenceMark',
        'text': 'Text'
    }

    def __init__(self, link=None, node_id=None, content=None, footnote_type=None, position=None, reference_mark=None, text=None):  # noqa: E501
        """Footnote - a model defined in Swagger"""  # noqa: E501

        self._link = None
        self._node_id = None
        self._content = None
        self._footnote_type = None
        self._position = None
        self._reference_mark = None
        self._text = None
        self.discriminator = None

        if link is not None:
            self.link = link
        if node_id is not None:
            self.node_id = node_id
        if content is not None:
            self.content = content
        if footnote_type is not None:
            self.footnote_type = footnote_type
        if position is not None:
            self.position = position
        if reference_mark is not None:
            self.reference_mark = reference_mark
        if text is not None:
            self.text = text

    @property
    def link(self):
        """Gets the link of this Footnote.  # noqa: E501

        Gets or sets link to the document.  # noqa: E501

        :return: The link of this Footnote.  # noqa: E501
        :rtype: WordsApiLink
        """
        return self._link

    @link.setter
    def link(self, link):
        """Sets the link of this Footnote.

        Gets or sets link to the document.  # noqa: E501

        :param link: The link of this Footnote.  # noqa: E501
        :type: WordsApiLink
        """
        self._link = link
    @property
    def node_id(self):
        """Gets the node_id of this Footnote.  # noqa: E501

        Gets or sets node id.  # noqa: E501

        :return: The node_id of this Footnote.  # noqa: E501
        :rtype: str
        """
        return self._node_id

    @node_id.setter
    def node_id(self, node_id):
        """Sets the node_id of this Footnote.

        Gets or sets node id.  # noqa: E501

        :param node_id: The node_id of this Footnote.  # noqa: E501
        :type: str
        """
        self._node_id = node_id
    @property
    def content(self):
        """Gets the content of this Footnote.  # noqa: E501

        Gets or sets content of footnote.  # noqa: E501

        :return: The content of this Footnote.  # noqa: E501
        :rtype: StoryChildNodes
        """
        return self._content

    @content.setter
    def content(self, content):
        """Sets the content of this Footnote.

        Gets or sets content of footnote.  # noqa: E501

        :param content: The content of this Footnote.  # noqa: E501
        :type: StoryChildNodes
        """
        self._content = content
    @property
    def footnote_type(self):
        """Gets the footnote_type of this Footnote.  # noqa: E501

        Gets or sets returns a value that specifies whether this is a footnote or endnote.  # noqa: E501

        :return: The footnote_type of this Footnote.  # noqa: E501
        :rtype: str
        """
        return self._footnote_type

    @footnote_type.setter
    def footnote_type(self, footnote_type):
        """Sets the footnote_type of this Footnote.

        Gets or sets returns a value that specifies whether this is a footnote or endnote.  # noqa: E501

        :param footnote_type: The footnote_type of this Footnote.  # noqa: E501
        :type: str
        """
        allowed_values = ["Footnote", "Endnote"]  # noqa: E501
        if not footnote_type.isdigit():	
            if footnote_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `footnote_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(footnote_type, allowed_values))
            self._footnote_type = footnote_type
        else:
            self._footnote_type = allowed_values[int(footnote_type) if six.PY3 else long(footnote_type)]
    @property
    def position(self):
        """Gets the position of this Footnote.  # noqa: E501

        Gets or sets link to comment range start node.  # noqa: E501

        :return: The position of this Footnote.  # noqa: E501
        :rtype: DocumentPosition
        """
        return self._position

    @position.setter
    def position(self, position):
        """Sets the position of this Footnote.

        Gets or sets link to comment range start node.  # noqa: E501

        :param position: The position of this Footnote.  # noqa: E501
        :type: DocumentPosition
        """
        self._position = position
    @property
    def reference_mark(self):
        """Gets the reference_mark of this Footnote.  # noqa: E501

        Gets or sets /sets custom reference mark to be used for this footnote. Default value is , meaning auto-numbered footnotes are used.  # noqa: E501

        :return: The reference_mark of this Footnote.  # noqa: E501
        :rtype: str
        """
        return self._reference_mark

    @reference_mark.setter
    def reference_mark(self, reference_mark):
        """Sets the reference_mark of this Footnote.

        Gets or sets /sets custom reference mark to be used for this footnote. Default value is , meaning auto-numbered footnotes are used.  # noqa: E501

        :param reference_mark: The reference_mark of this Footnote.  # noqa: E501
        :type: str
        """
        self._reference_mark = reference_mark
    @property
    def text(self):
        """Gets the text of this Footnote.  # noqa: E501

        Gets or sets this is a convenience property that allows to easily get or set text of the footnote.  # noqa: E501

        :return: The text of this Footnote.  # noqa: E501
        :rtype: str
        """
        return self._text

    @text.setter
    def text(self, text):
        """Sets the text of this Footnote.

        Gets or sets this is a convenience property that allows to easily get or set text of the footnote.  # noqa: E501

        :param text: The text of this Footnote.  # noqa: E501
        :type: str
        """
        self._text = text
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
        if not isinstance(other, Footnote):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
