# Copyright (c) 2019, Pradipta Deb
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following
# disclaimer. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and
# the following disclaimer in the documentation and/or other materials provided with the distribution. THIS SOFTWARE
# IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ==============================================================================

"""
    A class to represent a message used for communication bybthe user agents.

        Class_Attributes
        ==============

            dest_ids : tuple
               A tuple of values defining for the message destinations. Each value in the tuple corressponds to
               encrypted/un-encrypted agent ids.

            msg : str
               Actual message content. Ideally, should always be encrypted.

        Methods
        ==============

            get_dest_ids()
               returns the destination ids in encrypted/unencrypted format.

            def update_dest_ids(id_values: list):
                Update method for dest_ids tuple of a message. Can only append new values to the existing list of
                destination ids.

                :param id_values: list of values to be added for dest_ids list.

            def get_msg_content_in_bytes(self):
                retuns the content of the message in byte-like object format in order to be encoded in future.
"""

from typing import NamedTuple


class Message(NamedTuple):

    dest_id: bytes
    msg: bytes

    def get_dest_id(self):
        """
        Getter method for dest_id attribute.

        :return: returns the value of the dest_id attribute
        """
        return self.dest_id

    # def update_dest_ids(self, id_values: list):
    #     """
    #     Update method for dest_ids tuple of a message. Can only append new values to the existing list of
    #     destination ids.
    #
    #     :param id_values: list of values to be added for dest_ids list.
    #
    #     :return: modified object
    #     """
    #     updated_dest_ids = list(self.get_dest_ids()) + id_values
    #     return self._replace(dest_ids=tuple(updated_dest_ids))

    def get_msg_content(self):
        """
        retuns the content of the message in byte-like object format in order to be encoded in future.

        :return: entire msg content in a bytes-like object(e.g String).
        """
        return self.msg
