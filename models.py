from hashlib import sha256
import json
import time
import logging


logging.basicConfig(level=logging.DEBUG)


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        logging.debug(f'Block initialize with index({index}), '
                      f'transactions({transactions}), '
                      f'timestamp({timestamp}) and '
                      f'previous hash({previous_hash})')

    def compute_hash(self):
        """
       Creates a hash for the block content.
       """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        res = sha256(block_string.encode()).hexdigest()
        return res

    def __str__(self):
        return f'index({self.index}) - timestamp({self.timestamp})'

    def __repr__(self):
        return self.__str__()


class Blockchain:
    # Dificulty for the Proof of Work algorithm
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []  # information to insert into the blockchain
        self.chain = []
        self.create_genesis_block()
        logging.debug(f'New blockchain created: '
                      f'unconfirmed_transactions({self.unconfirmed_transactions}) and '
                      f'chain({self.chain})')

    def create_genesis_block(self):
        """
        Generate the genesis block and add it to the chain.
        The block has index 0, previous_hash 0 and a valid hash.
        """
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
        logging.debug('Genesis block created')

    @staticmethod
    def proof_of_work(block):
        """
        Tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        logging.debug(f'Calculating PoW: number of calculations required: {block.nonce}')
        logging.debug(f'Calculating PoW: final hash --> {computed_hash}')
        return computed_hash

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        """
        Aggregates the block to the chain after verification
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        logging.debug(f'Add block to chain: block --> {block}')
        self.chain.append(block)
        logging.debug(f'Add block to chain: chain --> {self.chain}')
        return True

    @staticmethod
    def is_valid_proof(block, block_hash):
        """
        Check if the block hash is valid and satisfy thr dificulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    def add_new_transaction(self, transaction):
        logging.debug(f'Add new transaction: {transaction}')
        self.unconfirmed_transactions.append(transaction)
        logging.debug(f'Current unconfirmed transactions: {len(self.unconfirmed_transactions)}')

    def mine(self):
        """
        Interface to add pending transactions to the blockchain, adding them to the
        block and calculating the proof of work.
        """
        if not self.unconfirmed_transactions:
            logging.debug('Mining: not unconfirmed transactions')
            return False

        new_block = Block(index=self.last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=self.last_block.hash)

        logging.debug(f'Mining: New block: {new_block}')
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.index
