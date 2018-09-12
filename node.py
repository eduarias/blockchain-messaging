import time
import json
from flask import Flask, request
import requests

from .models import Blockchain

app = Flask(__name__)

# copy of blockchain node
blockchain = Blockchain()


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    input_data = request.get_json()
    required_fields = ['author', 'content']

    for field in required_fields:
        if not input_data.get(field):
            return 'Invalid transaction data', 404

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
