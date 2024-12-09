from dataclasses import dataclass
import hashlib
import uuid
from lottery.config import config


@dataclass
class WompiCredentials:
    public_key: str
    private_key: str
    events_key: str
    integrity_key: str


class Wompi:
    def __init__(self):
        self.load_wompi_credentials()
        self.initialized = True

    def generate_purchase_reference(self):
        """
        Generates a unique payment reference using a truncated MD5 hash of a UUID.

        The function performs the following steps:
        1. Generates a UUID (Universally Unique Identifier).
        2. Computes the MD5 hash of the UUID.
        3. Returns the first 16 characters of the hexadecimal representation of the MD5 hash.

        Returns:
            str: A unique payment reference consisting of 16 hexadecimal characters.
        """
        # Generate a UUID
        unique_id = str(uuid.uuid4())
        # Compute the MD5 hash of the UUID
        hash_object = hashlib.md5(unique_id.encode())
        # Get the hexadecimal representation of the hash
        hex_dig = hash_object.hexdigest()
        # Return the first 16 characters of the hash
        return hex_dig[:16]

    def generate_hash_integrity_signature(self, payment_reference, amountToPayInCents):
        integrity_signature = f"{payment_reference}{amountToPayInCents}COP{self.credentials.integrity_key}"
        hash_object = hashlib.sha256();
        hash_object.update(integrity_signature.encode('utf-8'))
        hash_signature = hash_object.hexdigest()
        return hash_signature

    def load_wompi_credentials(self):
        environment = config.environment
        self.base_url = config.get(environment, "WOMPI_BASE_API_URL")
        self.base_redirect_url = config.get(environment, "WOMPI_BASE_REDIRECT_URL")
        self.credentials = WompiCredentials(
            public_key=config.get(environment, "WOMPI_PUBLIC_KEY"),
            private_key=config.get(environment, "WOMPI_PRIVATE_KEY"),
            events_key=config.get(environment, "WOMPI_EVENTS_KEY"),
            integrity_key=config.get(environment, "WOMPI_INTEGRITY_KEY"),
        )


wompi = Wompi()
