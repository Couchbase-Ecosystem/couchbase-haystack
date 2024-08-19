---
id: authentication
title: Authentication
---

## Classes

### `CouchbaseAuthenticator`

A base class for Couchbase authentication.

```python
from typing import overload

class CouchbaseAuthenticator(dict):
    @overload
    def get_cb_auth(self):
        "Get Couchbase auth"
```


### `CouchbasePasswordAuthenticator`

This class handles password-based authentication for Couchbase.

#### Args:

- `username` (Secret): Username to use for authentication. Defaults to `Secret.from_env_var("CB_USERNAME")`.
- `password` (Secret): Password to use for authentication. Defaults to `Secret.from_env_var("CB_PASSWORD")`.
- `cert_path` (Optional[str]): Path of the certificate trust store. Defaults to `None`.

#### Methods:

- `get_cb_auth() -> PasswordAuthenticator`: Returns a `PasswordAuthenticator` object for Couchbase.
- `to_dict() -> Dict[str, Any]`: Serializes the component to a dictionary.
- `from_dict(data: Dict[str, Any]) -> "CouchbasePasswordAuthenticator"`: Deserializes the component from a dictionary.

```python
class CouchbasePasswordAuthenticator(CouchbaseAuthenticator):
    def __init__(self,
                 username: Secret = Secret.from_env_var("CB_USERNAME"),
                 password: Secret = Secret.from_env_var("CB_PASSWORD"),
                 cert_path: Optional[str] = None,
                 **kwargs: Dict[str, Any]):
        # Constructor body...

    def get_cb_auth(self) -> PasswordAuthenticator:
        # Method body...

    def to_dict(self) -> Dict[str, Any]:
        # Method body...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CouchbasePasswordAuthenticator":
        # Method body...
```

### `CouchbaseCertificateAuthenticator`

This class handles certificate-based authentication for Couchbase.

#### Args:

- `cert_path` (str): Path to the client certificate.
- `key_path` (str): Path to the client private key.
- `trust_store_path` (Optional[str]): Path of the certificate trust store. Defaults to `None`.

#### Methods:

- `get_cb_auth() -> CertificateAuthenticator`: Returns a `CertificateAuthenticator` object for Couchbase.
- `to_dict() -> Dict[str, Any]`: Serializes the component to a dictionary.
- `from_dict(data: Dict[str, Any]) -> "CouchbaseCertificateAuthenticator"`: Deserializes the component from a dictionary.

```python
class CouchbaseCertificateAuthenticator(dict):
    def __init__(self,
                 cert_path: str = None,
                 key_path: str = None,
                 trust_store_path: Optional[str] = None):
        # Constructor body...

    def get_cb_auth(self) -> CertificateAuthenticator:
        # Method body...

    def to_dict(self) -> Dict[str, Any]:
        # Method body...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseCertificateAuthenticator":
        # Method body...
```
