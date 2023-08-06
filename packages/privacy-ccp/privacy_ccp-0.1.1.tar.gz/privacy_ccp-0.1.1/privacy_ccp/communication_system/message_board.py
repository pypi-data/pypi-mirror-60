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
    A simple message board server through which the collaborative communication is maintained between various agents.

        Class_Attributes
        ==============

            messageRequestQueue : Queue
                A queue which contains the requested messages still to be published in the message board.

            messageList : list
                A list of messages currently present in the message board.


        Methods
        ==============

            msg_count()
                Returns the count of total number of messages present in the message board.

            msg_request_count()
                Count of messages in the message queue which are still to be added to mesage board.

            add_msg_to_message_queue(msg)
                Adds a message to be added in message board in the queue.

                :param msg: Message to be added to mesage queue.

            add_msg_to_board(msg=None)
                Pop out one message from message queue or take the attribute msg and add it to the message board.

                :param msg: Message to be added to mesage board (default None).

            process_msg_queue()
                Process message queue and add messages to message board in FIFO manner until there is no more messages to
                added in the message queue.
"""

from typing import NamedTuple
from queue import Queue
from privacy_ccp.crypto.generate_hash import get_hash
from privacy_ccp.crypto.generate_signature import get_signature

isProcessingMsgQueue = False


class MessagingServer(NamedTuple):
    messageRequestQueue: Queue
    messageList: list

    def msg_count(self):
        """
        Returns the count of total messages in the message board.

        :return: size of message board
        """
        return len(self.messageList)

    def get_msg(self, requester_id, msg_index):
        requested_message, _, _ = self.messageList[msg_index]
        if requested_message.get_dest_id() == str(requester_id).encode():
            return requested_message
        else:
            return None

    def msg_request_count(self):
        """
        Count of messages in the message queue which are still to be added to mesage board.

        :return: size of message queue.
        """
        return self.messageRequestQueue.qsize()

    def add_msg_to_message_queue(self, msg):
        """
        Adds a message to be added in message board in the queue.

        :param msg: Message to be added to mesage queue.

        :return: None
        """
        global isProcessingMsgQueue

        self.messageRequestQueue.put(msg)
        if not isProcessingMsgQueue:
            # print("Starting to process msg queue")
            self.process_msg_queue()
            # print("Finished processing msg queue for now")

    def __add_msg_to_board(self, msg):
        """
        Pop out one message from message queue and add it to the message board.

        :param msg: Message to be added to mesage board (default None).

        :return: None
        """
        if len(self.messageList) > 0:
            previous_hash = self.messageList[-1][1]
        else:
            previous_hash = get_hash(b'Starting from a empty message board')

        new_hash_tuple = (previous_hash.hexdigest(), msg.get_msg_content())
        encoded_object = "".join(map(str, new_hash_tuple)).encode()
        new_hash = get_hash(encoded_object)
        generated_signature = get_signature(str(new_hash.hexdigest()))
        self.messageList.append((msg, new_hash, generated_signature))

    def process_msg_queue(self):
        """
        Process message queue and add messages to message board in FIFO manner until there is no more messages to
        added in the message queue.

        :return: None
        """
        global isProcessingMsgQueue

        isProcessingMsgQueue = True
        while self.msg_request_count() > 0:
            message = self.messageRequestQueue.get()
            self.__add_msg_to_board(msg=message)
        isProcessingMsgQueue = False
