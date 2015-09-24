"""
Encryption utilities for rest_framework_encrypted_lookup
"""
import base64
import codecs
import hashlib

from Crypto.Cipher import AES

from .settings import encrypted_lookup_settings


class IDCipher(object):
    """
    Class which encryption/decryption between integer ids and string representations.
    """

    BLOCK_SIZE = 16
    PADDING_STRING = '{'
    PADDING_BYTES = bytes(PADDING_STRING.encode('utf-8'))

    def __init__(self, secret=encrypted_lookup_settings['secret_key']):
        secret_hash = hashlib.md5(bytearray(secret, 'utf-8')).hexdigest()
        self.secret = codecs.decode(secret_hash, 'hex_codec')
        self.cipher = AES.new(self.secret)

    def _pad(self, string, padding_char):
        """
        Utility method to pad a string with characters.

        This is a required step in string-encryption, which requires that the
        byte-length of the string be evenly divisible by the encryption block
        size.

        :param string: the string to pad
        :param padding_char:
        :return: the padded string
        """
        return string + (self.BLOCK_SIZE - len(string) % self.BLOCK_SIZE) * padding_char

    def encode(self, this_id):
        """
        Encode an integer id into cipher text.

        :param this_id:
        :return: cipher text
        """

        result = self.cipher.encrypt(self._pad(str(this_id), self.PADDING_STRING))
        result = str(base64.b32encode(result).decode('utf-8')).lower().rstrip('=')

        return result

    def decode(self, encoded):
        """
        Decode an integer id from cipher text.

        :param encoded: cipher text
        :return: integer id
        """

        result = self.cipher.decrypt(base64.b32decode(self._pad(encoded.upper(), "=")))
        result = int(result.rstrip(self.PADDING_BYTES))

        return result

# TODO: Refactor name to ID_CIPHER on next major version upgrade
id_cipher = IDCipher()  # pylint: disable=invalid-name
