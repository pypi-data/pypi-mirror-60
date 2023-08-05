import uuid

# Conventions used at www.3za.org
# Argue at https://algorithmia.com/algorithms/threezakeys/Hash/discussion

def hash5(key):
	return str(uuid.uuid5(uuid.NAMESPACE_DNS, key))

def to_public(private_key):
	return hash5(hash5(private_key))

def random_key():
	return str(uuid.uuid4())

def to_code(key):
	return hash5(private_key)

def random_name():
	return random_key()+'.json'
