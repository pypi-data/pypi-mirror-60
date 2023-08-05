# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""Default module wrapping the public and private key cryptography and ledger api."""

import logging
from typing import BinaryIO, Optional

import base58

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    load_pem_private_key,
)

from aea.crypto.base import Crypto
from aea.mail.base import Address

logger = logging.getLogger(__name__)

CHOSEN_ALGORITHM_ID = b"MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAE"
CHOSEN_PBK_LENGTH = 160

DEFAULT = "default"


def _load_pem_private_key_from_path(path):
    return load_pem_private_key(open(path, "rb").read(), None, default_backend())


class DefaultCrypto(Crypto):
    """Class wrapping the public and private key cryptography."""

    identifier = DEFAULT
    _chosen_ec = ec.SECP384R1()
    _chosen_hash = hashes.SHA256()

    def __init__(self, private_key_pem_path: Optional[str] = None):
        """Instantiate a crypto object."""
        self._private_key = (
            self._generate_pk()
            if private_key_pem_path is None
            else self._load_pem_private_key_from_path(private_key_pem_path)
        )
        self._public_key_obj = self._compute_pbk()
        self._public_key_pem = self._pbk_obj_to_pem(self._public_key_obj)
        self._public_key_b64 = self._pbk_pem_to_b64(self._public_key_pem)
        self._public_key_b58 = self._pbk_b64_to_b58(self._public_key_b64)
        self._fingerprint_hex = self._pbk_b64_to_hex(self._public_key_b64)
        assert self._pbk_obj_to_b58(self._public_key_obj) == self._pbk_obj_to_b58(
            self._pbk_b58_to_obj(self._public_key_b58)
        )

    @property
    def entity(self) -> None:
        """Get the entity."""
        raise NotImplementedError  # pragma: no cover

    @property
    def public_key(self) -> str:
        """
        Return a 219 character public key in base58 format.

        :return: a public key string in base58 format
        """
        return self._public_key_b58

    @property
    def public_key_pem(self) -> bytes:
        """
        Return a PEM encoded public key in base64 format. It consists of an algorithm identifier and the public key as a bit string.

        :return: a public key bytes string
        """
        return self._public_key_pem

    @property
    def private_key_pem(self) -> bytes:
        """
        Return a PEM encoded private key in base64 format. It consists of an algorithm identifier and the private key as a bit string.

        :return: a private key bytes string
        """
        return self._private_key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption())  # type: ignore

    @property
    def address(self) -> str:
        """
        Return a 219 character public key in base58 format.

        :return: a public key string in base58 format
        """
        return self._public_key_b58

    @property
    def fingerprint(self) -> str:
        """
        Return a 64 character fingerprint of the public key in hexadecimal format (32 bytes).

        :return: the fingerprint
        """
        return self._fingerprint_hex

    @classmethod
    def load(cls, fp: BinaryIO) -> "DefaultCrypto":
        """
        Deserialize binary file `fp` (a `.read()`-supporting file-like object containing a private key).

        :param fp: the input file pointer. Must be set in binary mode (mode='rb')
        :return: None
        """
        # todo: this requires changing the constructor. So we can feed directly the private key
        #       instead of the path to it.
        raise NotImplementedError  # pragma: no cover

    def dump(self, fp: BinaryIO) -> None:
        """
        Serialize crypto object as binary stream to `fp` (a `.write()`-supporting file-like object).

        :param fp: the output file pointer. Must be set in binary mode (mode='wb')
        :return: None
        """
        pem = self._private_key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption())  # type: ignore
        fp.write(pem)
        fp.close()

    def _generate_pk(self) -> object:
        """
        Generate a private key object.

        :return: private key object
        """
        private_key = ec.generate_private_key(self._chosen_ec, default_backend())
        return private_key

    def _load_pem_private_key_from_path(self, path) -> object:
        """
        Load a private key in PEM format from a file.

        :param path: the path to the PEM file.

        :return: the private key.
        """
        private_key = load_pem_private_key(
            open(path, "rb").read(), None, default_backend()
        )
        try:
            assert private_key.curve.name == self._chosen_ec.name
        except ValueError as e:  # pragma: no cover
            raise e  # pragma: no cover
        except AssertionError:  # pragma: no cover
            raise ValueError(
                "Expected elliptic curve: {} actual: {}".format(
                    private_key.curve.name, self._chosen_ec.name
                )
            )  # pragma: no cover
        return private_key

    def _compute_pbk(self) -> object:
        """
        Derive the public key from the private key.

        :return: public key object
        """
        public_key = self._private_key.public_key()  # type: ignore
        return public_key

    def _pbk_obj_to_pem(self, pbk: object) -> bytes:
        """
        Serialize the public key from object to bytes.

        :param pbk: the public key as an object

        :return: the public key as a bytes string in pem format (base64)
        """
        result = pbk.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)  # type: ignore
        return result

    def _pbk_pem_to_b64(self, pbk: bytes) -> bytes:
        """
        Convert the public key from pem bytes string format to standard bytes string format.

        :param pbk: the public key as a bytes string (PEM base64)

        :return: the public key as a bytes string (base64)
        """
        result = b"".join(pbk.splitlines()[1:-1])
        return result

    def _pbk_b64_to_b58(self, pbk: bytes) -> str:
        """
        Convert the public key from base64 to base58 string.

        :param pbk: the public key as a bytes string (base64)

        :return: the public key as a string (base58)
        """
        result = base58.b58encode(pbk).decode("utf-8")
        return result

    def _pbk_obj_to_b58(self, pbk: object) -> str:
        """
        Convert the public key from object to string.

        :param pbk: the public key as an object

        :return: the public key as a string (base58)
        """
        pbk = self._pbk_obj_to_pem(pbk)
        pbk = self._pbk_pem_to_b64(pbk)
        pbk = self._pbk_b64_to_b58(pbk)
        return pbk

    def _pbk_b58_to_b64(self, pbk: str) -> bytes:
        """
        Convert the public key from base58 string to base64 bytes string.

        :param pbk: the public key in base58

        :return: the public key in base64
        """
        pbk_b64 = base58.b58decode(str.encode(pbk))
        return pbk_b64

    def _pbk_b64_to_pem(self, pbk: bytes) -> bytes:
        """
        Convert the public key from standard bytes string format to pem bytes string format.

        :param pbk: the public key as a bytes string (base64)

        :return: the public key as a bytes string (PEM base64)
        """
        assert len(pbk) == CHOSEN_PBK_LENGTH, "Public key is not of expected length."
        assert (
            pbk[0:32] == CHOSEN_ALGORITHM_ID
        ), "Public key has not expected algorithm id."
        pbk = pbk[0:64] + b"\n" + pbk[64:128] + b"\n" + pbk[128:] + b"\n"
        pbk_pem = b"-----BEGIN PUBLIC KEY-----\n" + pbk + b"-----END PUBLIC KEY-----\n"
        return pbk_pem

    def _pbk_b58_to_obj(self, pbk: str) -> object:
        """
        Convert the public key from string (base58) to object.

        :param pbk: the public key as a string (base58)

        :return: the public key object
        """
        pbk_b64 = self._pbk_b58_to_b64(pbk)
        pbk_pem = self._pbk_b64_to_pem(pbk_b64)
        pbk_obj = serialization.load_pem_public_key(pbk_pem, backend=default_backend())
        return pbk_obj

    def sign_data(self, data: bytes) -> bytes:
        """
        Sign data with your own private key.

        :param data: the data to sign
        :return: the signature
        """
        digest = self._hash_data(data)
        signature = self._private_key.sign(digest, ec.ECDSA(utils.Prehashed(self._chosen_hash)))  # type: ignore
        return signature

    def is_confirmed_integrity(
        self, data: bytes, signature: bytes, signer_pbk: str
    ) -> bool:
        """
        Confirrm the integrity of the data with respect to its signature.

        :param data: the data to be confirmed
        :param signature: the signature associated with the data
        :param signer_pbk:  the public key of the signer

        :return: bool indicating whether the integrity is confirmed or not
        """
        signer_pbk_obj = self._pbk_b58_to_obj(signer_pbk)
        digest = self._hash_data(data)
        try:
            signer_pbk_obj.verify(signature, digest, ec.ECDSA(utils.Prehashed(self._chosen_hash)))  # type: ignore
            return True
        except InvalidSignature as e:
            logger.exception(str(e))
            return False

    def _hash_data(self, data: bytes) -> bytes:
        """
        Hash data.

        :param data: the data to be hashed
        :return: digest of the data
        """
        hasher = hashes.Hash(self._chosen_hash, default_backend())
        hasher.update(data)
        digest = hasher.finalize()
        return digest

    def _pbk_b64_to_hex(self, pbk: bytes) -> str:
        """
        Hash the public key to obtain a fingerprint.

        :return: the fingerprint in hex format
        """
        pbk_hash = self._hash_data(pbk)
        pbk_hex = pbk_hash.hex()
        return pbk_hex

    def _pvk_obj_to_pem(self, pvk: object) -> bytes:
        """
        Convert the private key to pem format.

        :return: bytes (pem format)
        """
        return pvk.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption())  # type: ignore

    @classmethod
    def get_address_from_public_key(cls, public_key: str) -> str:
        """
        Get the address from the public key.

        :param public_key: the public key
        :return: str
        """
        raise NotImplementedError  # pragma: no cover

    def sign_message(self, message: bytes) -> bytes:
        """
        Sign a message in bytes string form.

        :param message: the message we want to send
        :return: Signed message in bytes
        """
        raise NotImplementedError  # pragma: no cover

    def recover_message(self, message: bytes, signature: bytes) -> Address:
        """
        Recover the address from the hash.

        :param message: the message we expect
        :param signature: the transaction signature
        :return: the recovered address
        """
        raise NotImplementedError  # praggma: no cover
