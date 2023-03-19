import hashlib
import json
import logging
import os

import pem as pem
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
import jwt

HOST = "https://playadust.social/"

config = {
    "shake": "",
    "public_key": "",
    "camp_name": "",
    "camp_location": "",
    "camp_email": "",
}

pk = {
    "public_key": "",
    "camp_name": "",
    "camp_location": "",
    "camp_email": "",
}


def prompt_for(display: str, default: str):
    prompt = f"Enter value for [{display}] - default is [{default}]: "
    got = input(prompt)
    if got == "":
        got = default
    return got

if not os.path.isfile("private.pem"):
    print("Generating new keys...")
    private_key_binary = ec.generate_private_key(ec.SECP256K1())
    public_key = private_key_binary.public_key().public_bytes(encoding=serialization.Encoding.PEM,
                                                              format=serialization.PublicFormat.SubjectPublicKeyInfo)

    private_key = private_key_binary.private_bytes(encoding=serialization.Encoding.PEM,
                                                   format=serialization.PrivateFormat.TraditionalOpenSSL,
                                                   encryption_algorithm=serialization.NoEncryption())
    with open("private.pem", "wt") as f:
        f.write(str(private_key.decode('utf-8')))
    with open("public.pem", "wt") as f:
        f.write(str(public_key.decode('utf-8')))

else:
    with open("private.pem", "rt") as f:
        private_key = f.read()
    with open("public.pem", "rt") as f:
        public_key = f.read()

if os.path.isfile("config.json"):
    with open("config.json", "rt") as f:
        config = json.load(f)

summy = hashlib.shake_256()
parsed_pk = pem.parse(public_key.encode('utf-8'))
summy.update(parsed_pk[0].as_bytes())
shake256 = summy.hexdigest(4)

print("Prepping registration packet")
pk['public_key'] = public_key
config["camp_name"] = pk["camp_name"] = prompt_for("camp name", config["camp_name"])
config["camp_email"] = pk["camp_email"] = prompt_for("camp email", config["camp_email"])
# camp_location is optional
config["camp_location"] = pk["camp_location"] = prompt_for("camp_location", config["camp_location"])
encoded = jwt.encode(pk, private_key, algorithm="ES256K")
print(f"send ->  {HOST}register")
result = requests.post(f"{HOST}register", data=encoded)
if result.status_code != 200:
    logging.exception("unable to access the registration server")
    exit(1)
parsed_return = result.json()
print(parsed_return)

if not parsed_return['ok']:
    print("Operation failed:")
    logging.exception(parsed_return)
    exit(1)

with open("config.json", "wt") as f:
    json.dump(config, f)
print("SAVE YOUR KEYS - SAVE YOUR KEYS - SAVE YOUR KEYS")
print("Copy your *.pem files to a backup device!  They cannot be recovered.")
print("operation ok.")
print("SAVE YOUR KEYS - SAVE YOUR KEYS - SAVE YOUR KEYS")

