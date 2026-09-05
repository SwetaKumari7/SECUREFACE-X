import os
import json
import hashlib
from datetime import datetime, timezone


BLOCKCHAIN_FILE = os.path.join(
    "models",
    "biometric_blockchain.json"
)


class Block:

    def __init__(
        self,
        index,
        timestamp,
        template_file,
        template_hash,
        previous_hash
    ):

        self.index = index
        self.timestamp = timestamp
        self.template_file = template_file
        self.template_hash = template_hash
        self.previous_hash = previous_hash

        self.hash = self.calculate_hash()

    def calculate_hash(self):

        block_data = (
            str(self.index)
            + self.timestamp
            + self.template_file
            + self.template_hash
            + self.previous_hash
        )

        return hashlib.sha256(
            block_data.encode("utf-8")
        ).hexdigest()

    def to_dict(self):

        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "template_file": self.template_file,
            "template_hash": self.template_hash,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }


class BiometricBlockchain:

    def __init__(self):

        self.chain = []

        if os.path.exists(BLOCKCHAIN_FILE):
            self.load_chain()
        else:
            self.create_genesis_block()

    def create_genesis_block(self):

        genesis = Block(
            index=0,
            timestamp=datetime.now(
                timezone.utc
            ).isoformat(),
            template_file="GENESIS",
            template_hash=hashlib.sha256(
                b"GENESIS"
            ).hexdigest(),
            previous_hash="0"
        )

        self.chain.append(genesis)
        self.save_chain()

    def add_template_block(
        self,
        template_file,
        template_hash
    ):

        previous_block = self.chain[-1]

        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now(
                timezone.utc
            ).isoformat(),
            template_file=template_file,
            template_hash=template_hash,
            previous_hash=previous_block.hash
        )

        self.chain.append(new_block)
        self.save_chain()

        return new_block

    def save_chain(self):

        os.makedirs(
            os.path.dirname(BLOCKCHAIN_FILE),
            exist_ok=True
        )

        data = [
            block.to_dict()
            for block in self.chain
        ]

        with open(
            BLOCKCHAIN_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    def load_chain(self):

        with open(
            BLOCKCHAIN_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        self.chain = []

        for item in data:

            block = Block(
                index=item["index"],
                timestamp=item["timestamp"],
                template_file=item["template_file"],
                template_hash=item["template_hash"],
                previous_hash=item["previous_hash"]
            )

            block.hash = item["hash"]

            self.chain.append(block)

    def verify_chain(self):

        if not self.chain:
            return False

        for i in range(1, len(self.chain)):

            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False

            if current.previous_hash != previous.hash:
                return False

        genesis = self.chain[0]

        if genesis.hash != genesis.calculate_hash():
            return False

        return True

    def find_template_hash(self, template_file):

        for block in self.chain:

            if block.template_file == template_file:
                return block.template_hash

        return None

    def verify_template_integrity(self, template_file):

        if not self.verify_chain():
            return False, "Blockchain integrity verification failed."

        if not os.path.exists(template_file):
            return False, "AES biometric template was not found."

        current_hash = calculate_file_hash(template_file)

        stored_hash = self.find_template_hash(
            template_file
        )

        if stored_hash is None:
            return False, "Template is not registered in blockchain."

        if current_hash != stored_hash:
            return False, (
                "SECURITY ALERT: Biometric template "
                "does not match blockchain record."
            )

        return True, "Template integrity verified."


def calculate_file_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            data = file.read(8192)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


def register_template_in_blockchain():

    template_file = r"models\face_templates_aes.enc"

    if not os.path.exists(template_file):

        raise FileNotFoundError(
            "AES encrypted template was not found."
        )

    template_hash = calculate_file_hash(
        template_file
    )

    blockchain = BiometricBlockchain()

    existing_hash = blockchain.find_template_hash(
        template_file
    )

    if existing_hash is not None:

        if existing_hash == template_hash:

            print(
                "Template already registered in blockchain."
            )

            return blockchain

        raise ValueError(
            "SECURITY ALERT: Template hash does not "
            "match the existing blockchain record."
        )

    block = blockchain.add_template_block(
        template_file,
        template_hash
    )

    print("Biometric template registered.")
    print("Block index:", block.index)
    print("Template:", block.template_file)
    print("SHA-256:", block.template_hash)
    print("Block hash:", block.hash)

    return blockchain


if __name__ == "__main__":

    print("======================================")
    print("BIOMETRIC BLOCKCHAIN SECURITY")
    print("======================================")

    blockchain = register_template_in_blockchain()

    print()

    chain_status = blockchain.verify_chain()

    print(
        "Blockchain integrity:",
        "PASSED" if chain_status else "FAILED"
    )

    template_status, message = (
        blockchain.verify_template_integrity(
            r"models\face_templates_aes.enc"
        )
    )

    print(
        "Template integrity:",
        "PASSED" if template_status else "FAILED"
    )

    print(message)

    print(
        "Total blocks:",
        len(blockchain.chain)
    )

    print()
    print("Blockchain file:")
    print(BLOCKCHAIN_FILE)

    print("======================================")
    print("BLOCKCHAIN TEST COMPLETED")
    print("======================================")