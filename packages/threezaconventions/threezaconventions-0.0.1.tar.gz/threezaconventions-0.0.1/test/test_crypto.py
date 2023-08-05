from threezaconventions.crypto import hash5,to_public, random_key, to_code
import uuid

def test_random():
    key = random_key()
    assert len(key)==len(str(uuid.uuid4()))
