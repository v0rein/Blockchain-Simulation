import binascii
from ecdsa import SigningKey, VerifyingKey, SECP256k1

class Wallet:
    def __init__(self):
        # Membuat pasang kunci (private dan public)
        self.private_key = SigningKey.generate(curve=SECP256k1)
        verifying_key = self.private_key.get_verifying_key()
        assert verifying_key is not None
        self.public_key = verifying_key
    
    def get_private_key_hex(self):
        return self.private_key.to_string().hex()
    
    def get_public_key_hex(self):
        return self.public_key.to_string().hex()

    @staticmethod
    def sign_transaction(private_key_hex, transaction_string):
        """Menandatangani pesan transaksi menggunakan private key"""
        private_key = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)
        signature = private_key.sign(transaction_string.encode('utf-8'))
        return signature.hex()

    @staticmethod
    def verify_signature(public_key_hex, signature_hex, transaction_string):
        """Memverifikasi keabsahan signature menggunakan public key"""
        try:
            public_key = VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=SECP256k1)
            return public_key.verify(bytes.fromhex(signature_hex), transaction_string.encode('utf-8'))
        except Exception:
            return False

if __name__ == '__main__':
    # Test Wallet
    w = Wallet()
    print("Private key:", w.get_private_key_hex())
    print("Public key:", w.get_public_key_hex())
