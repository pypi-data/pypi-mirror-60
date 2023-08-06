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
import click
from collections import namedtuple
from queue import Queue

from privacy_ccp.communication_system.message import Message
from privacy_ccp.communication_system.message_board import MessagingServer
from privacy_ccp.crypto.rsa_encryption import RSAEncryption
from privacy_ccp.simulation_environment.user_agent import UserAgent
from tqdm import tqdm


def setup_crypto_system():
    enc_name = input("Please choose which encryption to be used in the simulation:\n\n"
                     "1: Pallier\n"
                     "2: DSA\n"
                     "3: RSA (Deafult scheme)\n\n"
                     "Input: ")
    while True:
        try:
            bit_length = int(input("Please enter an encryption bit length (>=1024): "))
        except ValueError:
            print("Wrong Input.")
            bit_length = 0
            continue
        if bit_length < 1024:
            print("Wrong Input.")
        else:
            break

    if enc_name == '1':
        print(f"Using Pallier Encryption protocol with {bit_length} bytes key.")
        return PallierEncryption(bit_size=bit_length)
    elif enc_name == '2':
        print(f"Using DSA Encryption protocol with {bit_length} bytes key.")
        return DSAEncryption(bit_size=bit_length)
    else:
        print(f"Using RSA Encryption protocol with {bit_length} bytes key.")
        return RSAEncryption(bit_size=bit_length)


def setup_user_agents(user_encrption_algo):
    while True:
        try:
            n = int(input("\n\nPlease enter the number of users of the simulation (>3): "))
        except ValueError:
            print("Wrong Input.")
            n = 0
            continue
        if n <= 3:
            print("Wrong Input.")
        else:
            break

    agents_obj_list = []
    pub_key_list = []
    agents_list = []

    print(f"\n========================\n"
          f"Generating pub-priv key paris of length: {user_encrption_algo.get_bit_size()} for {n} agents"
          f"\n========================\n")
    for index in tqdm(range(n)):
        agent_obj = UserAgent(agent_id=index, user_data=random.randint(0, n * 10), enc_algo=user_encrption_algo)
        priv_key, pub_key = user_encrption_algo.generate_keys()
        pub_key_list.append(pub_key)
        agent_obj.set_enc_keys(pub_key=pub_key, priv_key=priv_key)
        # print(f'agent{index} has value {agent_obj.get_data()}')
        agents_obj_list.append(agent_obj)

    for index in range(n):
        agent = namedtuple('agent', ['data', 'message'])
        dest_id = random.choice([x for x in range(0, n - 1) if x != index])
        msg = str(agents_obj_list[index].get_data())
        # encrypted_dest_id = agent_obj.get_encrypted_data(str(dest_id))
        # print(f'agent{index} sending msg to agent{dest_id} using the public key of agent{dest_id}')

        encrypted_msg = user_encrption_algo.encrypt_data(pub_key=pub_key_list[dest_id], data=msg)
        agent_msg = Message(dest_id=str(dest_id).encode(), msg=encrypted_msg)
        agents_list.append(agent(agents_obj_list[index], agent_msg))

    return agents_list


def setup_msg_board():
    return MessagingServer(messageRequestQueue=Queue(maxsize=0), messageList=[])


def run_simulation(user_agents, msg_board):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for agent in user_agents:
            executor.submit(msg_board.add_msg_to_message_queue, agent.message)
            agent.data.update_sent_msg_count()

    print(f"\n\n#Items in Message Board: {msg_board.msg_count()}\n\n")

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
        print(f'\nagent:{agent.data.get_agent_id() + 1} has sent {agent.data.get_sent_msg_count()} messages.')
        for idx in range(msg_board.msg_count()):
            agent.data.read_msg_request(msg_board, agent.data.get_priv_key(), k=idx)

        total_num_received_msg += agent.data.get_received_msg_count()

        print(f'agent:{agent.data.get_agent_id() + 1} has received {agent.data.get_received_msg_count()} messages.')
        print(
            f'agent:{agent.data.get_agent_id() + 1} has the average as: {agent.data.get_updated_computation_value()} ')

    print(f'\n\n========================\n'
          f'#Sent: {total_num_sent_msg}, #Received: {total_num_received_msg}'
          f'\n========================\n')


def perform_ccp_simulation():
    """
    Run the simulation.

    :return: None
    """
    click.clear()
    enc_algo = setup_crypto_system()
    user_agents = setup_user_agents(user_encrption_algo=enc_algo)
    click.clear()
    msg_board = setup_msg_board()
    click.clear()
    print("\n========================\nStarting silumation now...\n========================\n")
    for _ in tqdm(range(5)):
        time.sleep(0.25)
    start = time.perf_counter()
    run_simulation(user_agents, msg_board)
    finish = time.perf_counter()
    print(f'The time required to process {len(user_agents)} threads is {round(finish - start, 2)}')
