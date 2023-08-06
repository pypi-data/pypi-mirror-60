# ==============================================================================
# Copyright (c) 2020, Pradipta Deb
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
    A base class to representing the various encryption schemes.

        Class_Attributes
        ==============

            public_key : bytes
               A tuple of values defining for the message destinations. Each value in the tuple corressponds to
               encrypted/un-encrypted agent ids.

            private_key : bytes
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


class Encryption:

    def __init__(self):
        self.__public_key = None
        self.__private_key = None

    def get_public_key(self):
        return self.__public_key

    def get_private_key(self):
        return self.__private_key

    def set_public_key(self, pub_key):
        self.__public_key = pub_key

    def set_private_key(self, priv_key):
        self.__private_key = priv_key
