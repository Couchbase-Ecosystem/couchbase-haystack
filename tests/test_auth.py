from haystack_integrations.document_stores.couchbase.auth import CouchbaseAuthenticator, CouchbasePasswordAuthenticator, CouchbaseCertificateAuthenticator
from haystack.utils.auth import Secret

class TestCouchbaseAuth:
    def test_password_auth(self):
        auth = CouchbasePasswordAuthenticator(
            username=Secret.from_env_var("username"),
            password=Secret.from_env_var("password"),
            cert_path= "cert_path",
            test = "test"
        )
        auth_dict = auth.to_dict()
        recon_auth = CouchbasePasswordAuthenticator.from_dict(auth_dict)
        assert auth["username"] == recon_auth["username"]
        assert auth["password"] == recon_auth["password"]
        assert auth["cert_path"] == recon_auth["cert_path"]
        assert auth["kwargs"] == recon_auth["kwargs"]

    def test_certificate_auth(self):
        auth = CouchbaseCertificateAuthenticator(
            cert_path="cert_path",
            key_path="key_path",
            trust_store_path="trust_store_path"
        )
        auth_dict = auth.to_dict()
        recon_auth = CouchbaseCertificateAuthenticator.from_dict(auth_dict)
        assert auth["cert_path"] == recon_auth["cert_path"]
        assert auth["key_path"] == recon_auth["key_path"]
        assert auth["trust_store_path"] == recon_auth["trust_store_path"]