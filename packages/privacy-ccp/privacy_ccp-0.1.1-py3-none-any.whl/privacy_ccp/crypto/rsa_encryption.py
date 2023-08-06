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
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from privacy_ccp.crypto.encryption import Encryption


class RSAEncryption(Encryption):

    def __init__(self, bit_size=256):
        super().__init__()
        self.__bit_size = bit_size
        self.__scheme = PKCS1_OAEP

    def get_bit_size(self):
        return self.__bit_size

    def set_bit_size(self, bit_length):
        self.__bit_size = bit_length

    def generate_keys(self):
        key = RSA.generate(self.__bit_size)
        self.set_private_key(key)
        self.set_public_key(key.publickey())
        return key, key.publickey()

    def encrypt_data(self, pub_key, data: str):
        cipher = self.__scheme.new(key=pub_key)
        encrypted_data = cipher.encrypt(data.encode())
        return encrypted_data

    def decrypt_data(self, priv_key, encrypted_data):
        cipher = self.__scheme.new(key=priv_key)
        decrypted_data = cipher.decrypt(encrypted_data)
        return decrypted_data
