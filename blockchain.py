import hashlib
import json
import requests
from time import time
from urllib.parse import urlparse
from wallet import Wallet

class Transaction:
    def __init__(self, sender, receiver, amount, signature=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = signature

    def to_dict(self):
        base = {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount
        }
        if self.signature:
            base["signature"] = self.signature
        return base

    def to_string(self):
        # Format dictionary untuk di-hash atau ditandatangani
        data = {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount
        }
        return json.dumps(data, sort_keys=True)
    
    def is_valid(self):
        # Transaksi reward dari sistem dianggap sah tanpa signature
        if self.sender == "MINING_REWARD":
            return True
        
        if not self.signature or len(self.signature) == 0:
            return False
            
        return Wallet.verify_signature(
            self.sender, 
            self.signature, 
            self.to_string()
        )

class Block:
    def __init__(self, index, transactions, previous_hash, nonce=0, timestamp=None):
        self.index = index
        self.timestamp = timestamp or time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [t.to_dict() for t in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.difficulty = 2 # Tingkat kesulitan mining (2 untuk demo, 4 untuk produksi)
        self.mining_reward = 50 # Reward untuk penambang (miner)
        self.nodes = set()
        
        # Buat Genesis block
        self.create_block(previous_hash='1', proof=100)

    def register_node(self, address):
        """Mendaftarkan Node Baru dalam Jaringan"""
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)

    def create_block(self, previous_hash=None, proof=None):
        """Membuat Block Baru dan Memasukkannya ke Chain"""
        block = Block(
            index=len(self.chain) + 1,
            transactions=self.pending_transactions,
            previous_hash=previous_hash or self.chain[-1].hash,
        )
        # Jika nilai proof dipass secara manual (contoh Genesis)
        if proof is not None:
            block.nonce = proof
            block.hash = block.calculate_hash()
        else:
            block.mine_block(self.difficulty)
            
        self.pending_transactions = []
        self.chain.append(block)
        return block

    def mine_pending_transactions(self, miner_reward_address):
        """Memproses semua transaksi yang menunggu dengan menambang blok baru"""
        # 1. Buat transaksi reward untuk si miner
        reward_tx = Transaction(
            sender="MINING_REWARD",
            receiver=miner_reward_address,
            amount=self.mining_reward
        )
        self.pending_transactions.append(reward_tx)
        
        # 2. Mine blok dengan transaksi-transaksi tersebut
        previous_hash = self.chain[-1].hash
        block = self.create_block(previous_hash)
        return block

    def add_transaction(self, sender, receiver, amount, signature):
        """Menambahkan transaksi baru ke dalam array pending setelah dicek keabsahannya"""
        tx = Transaction(sender, receiver, amount, signature)
        if not tx.is_valid():
            raise Exception("Invalid Transaction Signature!")
        
        self.pending_transactions.append(tx)
        return self.chain[-1].index + 1

    def is_chain_valid(self, chain):
        """Validasi integritas dari rantai blok terhubung"""
        previous_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            
            # Cek apkah previous hash sesuai
            if block['previous_hash'] != self.hash_block_dict(previous_block):
                return False
                
            # Cek apkah hash membuktikan difficulty PoW 
            if not block['hash'].startswith("0" * self.difficulty):
                return False

            previous_block = block
            current_index += 1

        return True

    def hash_block_dict(self, block_dict):
        """Buat hash sha256 dari object block berformat dictionary"""
        block_string = json.dumps({
            "index": block_dict['index'],
            "timestamp": block_dict['timestamp'],
            "transactions": block_dict['transactions'],
            "previous_hash": block_dict['previous_hash'],
            "nonce": block_dict['nonce']
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def resolve_conflicts(self):
        """Algoritma Konsensus yang mengganti rantai terpanjang yang valid di dalam network/jaringan"""
        neighbors = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbors:
            try:
                response = requests.get(f'http://{node}/chain')
                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']

                    # Periksa jika chain node tetangga lebih panjang dan valid.
                    if length > max_length and self.is_chain_valid(chain):
                        max_length = length
                        new_chain = chain
            except:
                continue

        # Jika kita temukan dan konfirmasi ada chain yg lebih bagus, replace chain server ini!
        if new_chain:
            # Bangun ulang class objek Block & Transaction yang hancur karena JSON Format
            reconstructed_chain = []
            for b_dict in new_chain:
                transactions = [Transaction(t['sender'], t['receiver'], t['amount'], t.get('signature')) for t in b_dict['transactions']]
                b = Block(b_dict['index'], transactions, b_dict['previous_hash'], b_dict['nonce'], b_dict['timestamp'])
                b.hash = b_dict['hash']
                reconstructed_chain.append(b)
                
            self.chain = reconstructed_chain
            return True

        return False
