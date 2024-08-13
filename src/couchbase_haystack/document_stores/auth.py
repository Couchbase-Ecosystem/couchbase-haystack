from typing import Any, Dict, Union,Optional, overload
from haystack import default_from_dict, default_to_dict
from haystack.utils.auth import Secret, deserialize_secrets_inplace
from couchbase.auth import PasswordAuthenticator, CertificateAuthenticator

class CouchbaseAuthenticator(dict):
    @overload
    def get_cb_auth(self):
        "Get couchbase auth"   

class CouchbasePasswordAuthenticator (CouchbaseAuthenticator):
    """
    Args:
        username (str): Username to use for authentication.
        password (str): Password to use for authentication.
        cert_path (str): Path of the certificate trust store. Defaults to None.
    """

    def __init__(self,
                 username: Secret = Secret.from_env_var("CB_USERNAME"),
                 password: Secret = Secret.from_env_var("CB_PASSWORD"),          # type: str
                 cert_path=None,    # type: Optional[str]
                 **kwargs           # type: Dict[str, Any]
                 ):
        self.username = username
        self.password = password
        self.cert_path = cert_path
        self.kwargs = kwargs
        parent_kwargs = {
            'username': self.username,
            'password': self.password,
            'cert_path': self.cert_path,
            'kwargs': kwargs
        }
        parent_kwargs.update(self.kwargs)
        super().__init__(**parent_kwargs)

    def get_cb_auth(self):
        return PasswordAuthenticator(self.username.resolve_value(), self.password.resolve_value(), self.cert_path, **self.kwargs)
    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the component to a dictionary.

        :returns:
            Dictionary with serialized data.
        """
        return default_to_dict(
            self,
            username= self.username.to_dict(),
            password= self.password.to_dict(),
            cert_path= self.cert_path,
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
    def __init__(self,
                 cert_path=None,            # type: str
                 key_path=None,             # type: str
                 trust_store_path=None     # type: Optional[str]
                 ):
        self.cert_path=cert_path
        self.key_path=key_path
        self.trust_store_path=trust_store_path
        parent_kwargs = {
            'cert_path': cert_path,
            'key_path': key_path,
            'trust_store_path': trust_store_path,
        }
        super().__init__(**parent_kwargs)
    def get_cb_auth(self):
        return CertificateAuthenticator(
            cert_path=self.cert_path,
            key_path=self.key_path,
            trust_store_path=self.trust_store_path
        )
    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the component to a dictionary.

        :returns:
            Dictionary with serialized data.
        """
        return default_to_dict(
            self,
            cert_path=self.cert_path,
            key_path=self.key_path,
            trust_store_path=self.trust_store_path
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
        return default_from_dict(cls, data)