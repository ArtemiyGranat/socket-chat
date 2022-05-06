from Crypto.Cipher import AES
# from Crypto.Random import get_random_bytes


class Encryptor:
    def __init__(self) -> None:
        self.key = b'\xd2P\x05\x0b\xd5\x8e\xa2&#!\xe9\x80k\x17\xc7V'
        self.iv = b'!\xc5\x1b\xca\xe7)\x89\xc0\xf8\x9e;\x0c\xf3H\xb3)'
        self.cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        self.d_cipher = AES.new(self.key, AES.MODE_CBC, self.iv)

    def pad(self, message) -> str:
        return message + ((16 - len(message) % 16) * "{")

    def encrypt(self, message) -> str:
        return self.cipher.encrypt(self.pad(message).encode("utf-8"))

    def decrypt(self, message) -> str:
        decrypted_msg = self.d_cipher.decrypt(message).decode("utf-8")
        cnt = decrypted_msg.count('{')
        return decrypted_msg[:len(decrypted_msg) - cnt]
