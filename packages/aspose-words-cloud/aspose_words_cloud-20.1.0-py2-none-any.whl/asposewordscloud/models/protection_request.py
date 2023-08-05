# coding: utf-8
# -----------------------------------------------------------------------------------
# <copyright company="Aspose" file="ProtectionRequest.py">
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


class ProtectionRequest(object):
    """Request on changing of protection.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'password': 'str',
        'new_password': 'str',
        'protection_type': 'str'
    }

    attribute_map = {
        'password': 'Password',
        'new_password': 'NewPassword',
        'protection_type': 'ProtectionType'
    }

    def __init__(self, password=None, new_password=None, protection_type=None):  # noqa: E501
        """ProtectionRequest - a model defined in Swagger"""  # noqa: E501

        self._password = None
        self._new_password = None
        self._protection_type = None
        self.discriminator = None

        if password is not None:
            self.password = password
        if new_password is not None:
            self.new_password = new_password
        if protection_type is not None:
            self.protection_type = protection_type

    @property
    def password(self):
        """Gets the password of this ProtectionRequest.  # noqa: E501

        Gets or sets current password.  # noqa: E501

        :return: The password of this ProtectionRequest.  # noqa: E501
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """Sets the password of this ProtectionRequest.

        Gets or sets current password.  # noqa: E501

        :param password: The password of this ProtectionRequest.  # noqa: E501
        :type: str
        """
        self._password = password
    @property
    def new_password(self):
        """Gets the new_password of this ProtectionRequest.  # noqa: E501

        Gets or sets new password.  # noqa: E501

        :return: The new_password of this ProtectionRequest.  # noqa: E501
        :rtype: str
        """
        return self._new_password

    @new_password.setter
    def new_password(self, new_password):
        """Sets the new_password of this ProtectionRequest.

        Gets or sets new password.  # noqa: E501

        :param new_password: The new_password of this ProtectionRequest.  # noqa: E501
        :type: str
        """
        self._new_password = new_password
    @property
    def protection_type(self):
        """Gets the protection_type of this ProtectionRequest.  # noqa: E501

        Gets or sets new type of protection.  # noqa: E501

        :return: The protection_type of this ProtectionRequest.  # noqa: E501
        :rtype: str
        """
        return self._protection_type

    @protection_type.setter
    def protection_type(self, protection_type):
        """Sets the protection_type of this ProtectionRequest.

        Gets or sets new type of protection.  # noqa: E501

        :param protection_type: The protection_type of this ProtectionRequest.  # noqa: E501
        :type: str
        """
        self._protection_type = protection_type
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
        if not isinstance(other, ProtectionRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
