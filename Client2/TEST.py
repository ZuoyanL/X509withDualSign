import rsa
import binascii
import OpenSSL
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from cryptography.hazmat.primitives.asymmetric import padding

data = b"HHHH"

cert_path = open('client2.crt').read()
cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_path)

pub_key = OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, cert.get_pubkey()).decode("utf-8")
# print(pub_key)
pri_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, open('client2.pem').read())
pri_key = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, pri_key).decode("utf-8")
# print(pri_key)

private_key = serialization.load_pem_private_key(
        pri_key.encode(),
        password=None,
        backend=default_backend()
    )

public_key = serialization.load_pem_public_key(
    pub_key.encode(),
    backend=default_backend()
)

out_data = public_key.encrypt(
        data,
        padding.PKCS1v15()
    )

out_data = private_key.decrypt(
        out_data,
        padding.PKCS1v15()
    )
print(out_data.decode())