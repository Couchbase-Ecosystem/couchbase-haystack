---
id: authentication
title: Authentication
---

## Classes

### `CouchbaseAuthenticator`

This is an abstract base class that should be inherited by specific Couchbase authenticator implementations.

#### Methods

- `get_cb_auth() -> Union[PasswordAuthenticator, CertificateAuthenticator]`
  - **Description**: This method is intended to be implemented by subclasses to return the appropriate Couchbase authenticator.
  - **Raises**: `NotImplementedError` if called directly on `CouchbaseAuthenticator`.

### `CouchbasePasswordAuthenticator`

This class handles password-based authentication for Couchbase.

#### `__init__`

```python
def __init__(
    self,
    username: Secret = Secret.from_env_var("CB_USERNAME"),
    password: Secret = Secret.from_env_var("CB_PASSWORD"),
    cert_path: Optional[str] = None,
    **kwargs: Dict[str, Any],
)
```

**Input Parameters:**
- `username` (Secret): The username used for authentication, typically fetched from an environment variable.
- `password` (Secret): The password used for authentication, also typically fetched from an environment variable.
- `cert_path` (Optional[str]): The path to the certificate trust store (if applicable).
- `kwargs` (Dict[str, Any]): Additional parameters that can be passed during initialization.

**Example Usage:**

```python
auth = CouchbasePasswordAuthenticator(
    username=Secret.from_env_var("my_username"),
    password=Secret.from_env_var("my_password"),
    cert_path="/path/to/cert"
)
```

#### `get_cb_auth`

```python
def get_cb_auth() -> PasswordAuthenticator
```

**Response:**
- Returns an instance of `PasswordAuthenticator` initialized with the provided username, password, and optional certificate path.

**Example Usage:**

```python
couchbase_auth = auth.get_cb_auth()
```

#### `to_dict`

```python
def to_dict() -> Dict[str, Any]
```

**Response:**
- Returns a dictionary containing the serialized state of the `CouchbasePasswordAuthenticator`.

**Example Usage:**

```python
serialized_auth = auth.to_dict()
```

#### `from_dict`

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "CouchbasePasswordAuthenticator"
```

**Input Parameters:**
- `data` (Dict[str, Any]): A dictionary containing the serialized state of a `CouchbasePasswordAuthenticator`.

**Response:**
- Returns a `CouchbasePasswordAuthenticator` instance reconstructed from the provided dictionary.

**Example Usage:**

```python
auth_instance = CouchbasePasswordAuthenticator.from_dict(serialized_auth)
```

### `CouchbaseCertificateAuthenticator`

This class handles certificate-based authentication for Couchbase.

#### `__init__`

```python
def __init__(
    self,
    cert_path: Optional[str] = None,
    key_path: Optional[str] = None,
    trust_store_path: Optional[str] = None,
)
```

**Input Parameters:**
- `cert_path` (Optional[str]): The path to the client certificate.
- `key_path` (Optional[str]): The path to the client key.
- `trust_store_path` (Optional[str]): The path to the trust store containing trusted CA certificates.

**Example Usage:**

```python
auth = CouchbaseCertificateAuthenticator(
    cert_path="/path/to/cert.pem",
    key_path="/path/to/key.pem",
    trust_store_path="/path/to/truststore.pem"
)
```

#### `get_cb_auth`

```python
def get_cb_auth() -> CertificateAuthenticator
```

**Response:**
- Returns an instance of `CertificateAuthenticator` initialized with the provided certificate path, key path, and trust store path.

**Example Usage:**

```python
couchbase_auth = auth.get_cb_auth()
```

#### `to_dict`

```python
def to_dict() -> Dict[str, Any]
```

**Response:**
- Returns a dictionary containing the serialized state of the `CouchbaseCertificateAuthenticator`.

**Example Usage:**

```python
serialized_auth = auth.to_dict()
```

#### `from_dict`

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseCertificateAuthenticator"
```

**Input Parameters:**
- `data` (Dict[str, Any]): A dictionary containing the serialized state of a `CouchbaseCertificateAuthenticator`.

**Response:**
- Returns a `CouchbaseCertificateAuthenticator` instance reconstructed from the provided dictionary.

**Example Usage:**

```python
auth_instance = CouchbaseCertificateAuthenticator.from_dict(serialized_auth)
```

## Serialization and Deserialization

Both `CouchbasePasswordAuthenticator` and `CouchbaseCertificateAuthenticator` support serialization to a dictionary and deserialization from a dictionary. This is useful for saving the state of an authenticator and restoring it later.

