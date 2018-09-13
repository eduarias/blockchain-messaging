import time
import json

import requests
from flask import Flask, redirect, render_template, request

from models import Blockchain, Block

app = Flask(__name__)

blockchain = Blockchain()   # copy of blockchain node
peers = set()               # network address of other nodes
CONNECTED_NODE_ADDRESS = 'http://127.0.0.1:8000'
posts = []


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    input_data = request.get_json()
    required_fields = ['author', 'content']

    if not input_data:
        return 'Invalid transaction data', 400
    for field in required_fields:
        if not input_data.get(field):
            return 'Invalid transaction data', 400

    input_data['timestamp'] = time.time()

    blockchain.add_new_transaction(input_data)

    return 'Success', 201


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({'length': len(chain_data),
                       'chain': chain_data})


@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return 'No transactions to mine'
    else:
        return 'Block #{} is mined.'.format(result)


@app.route('/pending_tx')
def get_pending_tx():
    """Get unconfirmed transactions"""
    return json.dumps(blockchain.unconfirmed_transactions)


@app.route('/add_nodes', methods=['POST'])
def register_new_peers():
    """Endpoint for new members in the network"""
    nodes = request.get_json()
    if not nodes:
        return 'Invalid data', 400
    for node in nodes:
        peers.add(node)
    return 'Nodes added successfully', 201


def consensus():
    """
    Consensus algorithm. If there is a chain longer than the one found, ours is replace for it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain)

    for node in peers:
        response = requests.get(f'http://{node}/chain')
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True
    else:
        return False


@app.route('/add_block', methods=['POST'])
def validate_and_add_block():
    """Endpoint to add a block mine by someone else to the node chain"""
    block_data = request.get_json()
    block = Block(block_data["index"], block_data["transactions"],
                  block_data["timestamp", block_data["previous_hash"]])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


def announce_new_block(block):
    for peer in peers:
        url = "http://{}/add_block".format(peer)
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))


def fetch_posts():
    get_chain_address = f'{CONNECTED_NODE_ADDRESS}/chain'
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain['chain']:
            for tx in block['transactions']:
                tx['index'] = block['index']
                tx['hash'] = block['previous_hash']
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction using our application.
    """
    post_content = request.form['content']
    author = request.form['author']

    post_object = {
        'author': author,
        'content': post_content,
    }

    # Submit a transaction
    new_tx_address = f'{CONNECTED_NODE_ADDRESS}/new_transaction'

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
