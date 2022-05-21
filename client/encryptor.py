from Crypto.Cipher import AES
from Crypto import Random

ENCODING = 'utf-8'


class Encryptor:
    def __init__(self) -> None:
        key_file = open('key.txt', 'r')
        self.key = key_file.readline().encode(ENCODING)

    def pad(self, msg) -> str:
        bs = AES.block_size
        return msg + (bs - len(msg) % bs) * chr(bs - len(msg) % bs)

    def unpad(self, msg) -> str:
        return msg[:-ord(msg[len(msg)-1:])]

    def encrypt(self, message) -> bytes:
        message = self.pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(message.encode(ENCODING))

    def decrypt(self, message) -> str:
        iv = message[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        dec_msg = cipher.decrypt(message[AES.block_size:]).decode(ENCODING)
        return self.unpad(dec_msg)
