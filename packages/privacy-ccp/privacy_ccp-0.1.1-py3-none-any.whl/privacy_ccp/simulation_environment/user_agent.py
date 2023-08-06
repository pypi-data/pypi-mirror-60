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

*****************************************************
[The implementation of this class is still in WIP]
*****************************************************


    A class to represent an agent which participates in a collaborative computation task.

        Class_Attributes
        ==============

        agent_id: id of the agent.

        neighbour_number: max number of neighbouring agents to collaborate to.

        num_read_msg: number of messages already read from the message board.

        data: agents own data that will be shared in encrypted/un-encrypted format for collaboration.

        read_msg_index: index of the last message read from the message board.


        Methods
        ==============

        get_data():
            returns the encrypted/un-encrypted data of the agent.

        get_num_neighbours():
            returns max number of neighbouring agents to collaborate to.

        set_num_neighbours(count):
            updates the max number of neighbours for collaboration in the CCP task.

        get_read_msg_index():
            returns the index of the last message that was read by this agent from message board.

        set_read_msg_index(idx):
            updates the attribute read_msg_index with value idx, which is the index of the last message read by the
            agent.

        get_encrypted_user_data():
            get the encryted version of the agent data that will be used to create a new message which will be
            posted to the message board.
"""


class UserAgent:

    def __init__(self, agent_id: int, user_data, enc_algo=None):
        """
        Constructor of the agent which sets up the object.

        :param agnt_id: id of the agent

        :param user_data: actual data of the user which will be shred during the CCT.
        """
        self.__agent_id = agent_id
        self.__num_read_msg = 0
        self.__data = user_data
        self.__read_msg_indexes = []
        self.__no_of_sent_msg = 0
        self.__no_of_received_msg = 0
        self.__encryption = enc_algo
        self.__pub_key = None
        self.__priv_key = None
        self.__computation_value = self.__data

    def set_enc_keys(self, pub_key, priv_key):
        self.__priv_key = priv_key
        self.__pub_key = pub_key

    def get_pub_key(self):
        return self.__pub_key

    def get_priv_key(self):
        return self.__priv_key

    def get_encryption_algo(self):
        return self.__encryption

    def get_data(self):
        return self.__data

    def get_agent_id(self):
        return self.__agent_id

    def get_sent_msg_count(self):
        return self.__no_of_sent_msg

    def get_received_msg_count(self):
        return self.__no_of_received_msg

    def update_sent_msg_count(self):
        self.__no_of_sent_msg += 1

    def get_read_msg_index(self):
        return self.__read_msg_indexes

    def set_read_msg_index(self, idx):
        self.__read_msg_indexes.append(idx)

    def get_updated_computation_value(self):
        self.__update_computation_value()
        return round(self.__computation_value, 3)

    def read_msg_request(self, msg_board, priv_key, k=None):
        # print(f"Reached here with index {k} and agent id is {self.get_agent_id()}")
        retreived_msg = msg_board.get_msg(self.__agent_id, k)
        if retreived_msg:
            self.__no_of_received_msg += 1
            self.set_read_msg_index(k)
            # print(retreived_msg.get_msg_content())
            # input()
            assert (self.__priv_key == priv_key)
            decrypted_data = self.get_encryption_algo().decrypt_data(priv_key=priv_key,
                                                                     encrypted_data=retreived_msg.get_msg_content())
            self.__computation_value += int(decrypted_data.decode())

    def __update_computation_value(self):
        self.__computation_value /= self.get_received_msg_count() + 1
