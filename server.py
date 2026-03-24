from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain
from wallet import Wallet

app = Flask(__name__)

# Identifikasi unik untuk Node ini
node_identifier = str(uuid4()).replace('-', '')

# Inisialisasi Blockchain
blockchain = Blockchain()

# Buatan Wallet untuk node ini agar bisa menerima reward mining
node_wallet = Wallet()
print(f"==================================================")
print(f"Node Wallet Public Key: {node_wallet.get_public_key_hex()}")
print(f"Node Wallet Private Key: {node_wallet.get_private_key_hex()}")
print(f"==================================================")

@app.route('/mine', methods=['GET'])
def mine():
    # Mine block baru dan berikan reward ke node ini
    block = blockchain.mine_pending_transactions(node_wallet.get_public_key_hex())
    
    response = {
        'message': "New Block Forged",
        'index': block.index,
        'transactions': [t.to_dict() for t in block.transactions],
        'nonce': block.nonce,
        'previous_hash': block.previous_hash,
        'hash': block.hash
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Cek parameter wajib
    required = ['sender', 'receiver', 'amount', 'signature']
    if not all(k in values for k in required):
        return 'Missing values', 400

    try:
        # Tambah transaksi baru
        index = blockchain.add_transaction(
            values['sender'], 
            values['receiver'], 
            values['amount'], 
            values['signature']
        )
        response = {'message': f'Transaction will be added to Block {index}'}
        return jsonify(response), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': [{
            "index": b.index,
            "timestamp": b.timestamp,
            "transactions": [t.to_dict() for t in b.transactions],
            "nonce": b.nonce,
            "previous_hash": b.previous_hash,
            "hash": b.hash
        } for b in blockchain.chain],
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': [{
                "index": b.index,
                "timestamp": b.timestamp,
                "transactions": [t.to_dict() for t in b.transactions],
                "nonce": b.nonce,
                "previous_hash": b.previous_hash,
                "hash": b.hash
            } for b in blockchain.chain]
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': [{
                "index": b.index,
                "timestamp": b.timestamp,
                "transactions": [t.to_dict() for t in b.transactions],
                "nonce": b.nonce,
                "previous_hash": b.previous_hash,
                "hash": b.hash
            } for b in blockchain.chain]
        }
    return jsonify(response), 200

@app.route('/wallet/new', methods=['GET'])
def new_wallet():
    """Endpoint utilitas untuk user membuat wallet baru via API"""
    w = Wallet()
    response = {
        'private_key': w.get_private_key_hex(),
        'public_key': w.get_public_key_hex()
    }
    return jsonify(response), 200

@app.route('/wallet/sign', methods=['POST'])
def sign_transaction():
    """Endpoint utilitas untuk menandatangani transaksi menggunakan private key"""
    values = request.get_json()
    required = ['private_key', 'sender', 'receiver', 'amount']
    if not all(k in values for k in required):
        return jsonify({'error': 'Missing values. Required: private_key, sender, receiver, amount'}), 400

    try:
        import json as json_module
        tx_data = json_module.dumps({
            'sender': values['sender'],
            'receiver': values['receiver'],
            'amount': values['amount']
        }, sort_keys=True)
        signature = Wallet.sign_transaction(values['private_key'], tx_data)
        response = {
            'sender': values['sender'],
            'receiver': values['receiver'],
            'amount': values['amount'],
            'signature': signature,
            'message': 'Transaction signed successfully'
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': f'Signing failed: {str(e)}'}), 400

@app.route('/pending', methods=['GET'])
def pending_transactions():
    """Tampilkan transaksi yang sedang menunggu untuk di-mine"""
    response = {
        'pending_transactions': [t.to_dict() for t in blockchain.pending_transactions],
        'count': len(blockchain.pending_transactions)
    }
    return jsonify(response), 200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()

    app.run(host='127.0.0.1', port=args.port, threaded=True)
