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

""" A main module for running the entire simulation """
import concurrent.futures
import random
import time
from collections import namedtuple
from queue import Queue

from privacy_ccp.communication_system.message import Message
from privacy_ccp.communication_system.message_board import MessagingServer
from privacy_ccp.simulation_environment.user_agent import UserAgent
from privacy_ccp.crypto.rsa_encryption import RSAEncryption, encrypt_data


def setup_user_agents(n, user_encrption_algo):
    agents_obj_list = []
    pub_key_list = []
    agents_list= []
    unique_key_list = set()

    for index in range(n):
        agent_obj = UserAgent(agent_id=index, user_data=random.randint(0, n * 100), enc_algo=user_encrption_algo)
        priv_key, pub_key = user_encrption_algo.generate_keys()
        pub_key_list.append(pub_key)
        agent_obj.set_enc_keys(pub_key=pub_key, priv_key=priv_key)
        # print(f'agent{index} has value {agent_obj.get_data()}')
        agents_obj_list.append(agent_obj)

    for idx in range(n):
        agent = namedtuple('agent', ['data', 'message'])
        dest_id = random.choice([x for x in range(0, n-1) if x != idx])
        msg = str(agents_obj_list[idx].get_data())
        # encrypted_dest_id = agent_obj.get_encrypted_data(str(dest_id))
        # print(f'agent{idx} sending msg to agent{dest_id} using the public key of agent{dest_id}')

        encrypted_msg = encrypt_data(pub_key=pub_key_list[dest_id], data=msg)
        agent_msg = Message(dest_id=str(dest_id).encode(), msg=encrypted_msg)
        agents_list.append(agent(agents_obj_list[idx], agent_msg))

    return agents_list


def setup_msg_board():
    return MessagingServer(messageRequestQueue=Queue(maxsize=0), messageList=[])


def setup_crypto_system():
    pass


def run_simulation(user_agents, msg_board):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for agent in user_agents:
            executor.submit(msg_board.add_msg_to_message_queue, agent.message)
            agent.data.update_sent_msg_count()

    # print("Length of msg queue is now: ", msg_board.msg_request_count())
    print("#Items in Message Board: ", msg_board.msg_count())
    # input()

    # for (message, hashcode, signature) in msg_board.messageList:
    #     print(f'\n==============================================='
    #           f'\nMsg: {message.get_msg_content_in_bytes()}\n'
    #           f'\nHash: {hashcode.hexdigest()}\n'
    #           f'\nSignature: {signature.hexdigest()}\n'
    #           f'\n===============================================\n')
    # print(msg_board.messageList)
    # input()

    total_num_received_msg = 0
    total_num_sent_msg = 0
    for agent in user_agents:
        total_num_sent_msg += agent.data.get_sent_msg_count()
        print(f'agent:{agent.data.get_agent_id()} has sent {agent.data.get_sent_msg_count()} messages.')
        for idx in range(msg_board.msg_count()):
            agent.data.read_msg_request(msg_board, agent.data.get_priv_key(), k=idx)

        total_num_received_msg += agent.data.get_received_msg_count()

        print(f'agent:{agent.data.get_agent_id()} has received {agent.data.get_received_msg_count()} messages.')
        print(f'agent:{agent.data.get_agent_id()} has the average as: {agent.data.get_updated_computation_value()} ')
    print(f'#Sent: {total_num_sent_msg}, #Received: {total_num_received_msg}')


def setup_crypto_system(name, bit_length):
    return RSAEncryption(bit_size=bit_length)


def main():
    """
    Run the simulation.

    :return: None
    """
    start = time.perf_counter()
    enc_algo = setup_crypto_system(name="rsa", bit_length=2048)
    user_agents = setup_user_agents(10, enc_algo)
    msg_board = setup_msg_board()
    run_simulation(user_agents, msg_board)
    finish = time.perf_counter()
    print(f'The time required to process {len(user_agents)} threads is {round(finish - start, 2)}')


if __name__ == '__main__':
    main()
