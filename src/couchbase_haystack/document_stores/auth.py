from typing import Any, Dict, Optional, Union

from couchbase.auth import CertificateAuthenticator, PasswordAuthenticator
from haystack import default_from_dict, default_to_dict
from haystack.utils.auth import Secret, deserialize_secrets_inplace


class CouchbaseAuthenticator(dict):
    def get_cb_auth(self) -> Union[PasswordAuthenticator, CertificateAuthenticator]:
        """This method should be implemented in a subclass."""
        raise NotImplementedError("This method should be implemented in a subclass.")


class CouchbasePasswordAuthenticator(CouchbaseAuthenticator):
    """
    Args:
        username (str): Username to use for authentication.
        password (str): Password to use for authentication.
        cert_path (str): Path of the certificate trust store. Defaults to None.
    """

    def __init__(
        self,
        username: Secret = Secret.from_env_var("CB_USERNAME"),
        password: Secret = Secret.from_env_var("CB_PASSWORD"),
        cert_path: Optional[str] = None,
        **kwargs,  # type: Dict[str, Any]
    ):
        self.username = username
        self.password = password
        self.cert_path = cert_path
        self.kwargs = kwargs
        parent_kwargs = {"username": self.username, "password": self.password, "cert_path": self.cert_path, "kwargs": kwargs}
        parent_kwargs.update(self.kwargs)
        super().__init__(**parent_kwargs)

    def get_cb_auth(self) -> PasswordAuthenticator:
        return PasswordAuthenticator(self.username.resolve_value(), self.password.resolve_value(), self.cert_path, **self.kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the component to a dictionary.

        :returns:
            Dictionary with serialized data.
        """
        return default_to_dict(
            self,
            username=self.username.to_dict(),
            password=self.password.to_dict(),
            cert_path=self.cert_path,
            **self.kwargs,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CouchbasePasswordAuthenticator":
        """
        Deserializes the component from a dictionary.

        :param data:
            Dictionary to deserialize from.
        :returns:
              Deserialized component.
        """
        deserialize_secrets_inplace(data["init_parameters"], keys=["username", "password"])
        return default_from_dict(cls, data)


class CouchbaseCertificateAuthenticator(dict):
    """
    Args:
        username (str): Username to use for authentication.
        password (str): Password to use for authentication.
        cert_path (str): Path of the certificate trust store. Defaults to None.
    """

    def __init__(self, cert_path: Optional[str] = None, key_path: Optional[str] = None, trust_store_path: Optional[str] = None):
        self.cert_path = cert_path
        self.key_path = key_path
        self.trust_store_path = trust_store_path
        parent_kwargs = {
            "cert_path": cert_path,
            "key_path": key_path,
            "trust_store_path": trust_store_path,
        }
        super().__init__(**parent_kwargs)

    def get_cb_auth(self) -> CertificateAuthenticator:
        return CertificateAuthenticator(cert_path=self.cert_path, key_path=self.key_path, trust_store_path=self.trust_store_path)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the component to a dictionary.

        :returns:
            Dictionary with serialized data.
        """
        return default_to_dict(self, cert_path=self.cert_path, key_path=self.key_path, trust_store_path=self.trust_store_path)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CouchbasePasswordAuthenticator":
        """
        Deserializes the component from a dictionary.

        :param data:
            Dictionary to deserialize from.
        :returns:
              Deserialized component.
        """
        return default_from_dict(cls, data)
