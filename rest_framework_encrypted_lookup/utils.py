import base64

from Crypto.Cipher import AES

from django.conf import settings


class IDCipher(object):
    """
    Class which encryption/decryption between integer ids and string representations.
    """

    BLOCK_SIZE = 16
    PADDING_STRING = '{'
    PADDING_BYTES = bytes(PADDING_STRING.encode('utf-8'))

    def __init__(self):
        self.secret = settings.ID_ENCRYPT_SECRET
        self.cipher = AES.new(self.secret)

    def pad(self, s, padding_char):
        return s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * padding_char

    def encode(self, this_id):
        return str(base64.b32encode(self.cipher.encrypt(self.pad(str(this_id), self.PADDING_STRING))).decode('utf-8')).lower().rstrip('=')

    def decode(self, encoded):
        return int(self.cipher.decrypt(base64.b32decode(self.pad(encoded.upper(), "="))).rstrip(self.PADDING_BYTES))

id_cipher = IDCipher()
