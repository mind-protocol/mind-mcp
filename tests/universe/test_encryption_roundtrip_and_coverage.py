"""
Tests for Phase U3: Encrypted Brains (AES-256-GCM)

Covers:
- AES-256-GCM encrypt/decrypt roundtrip for string fields
- AES-256-GCM encrypt/decrypt roundtrip for embedding vectors
- RSA-2048 key pair generation, PEM load/save
- RSA-OAEP wrap/unwrap of AES keys
- Space key distribution (grant, decrypt)
- Hierarchical key chain resolution
- Key rotation
- Encrypted field codec (node dict encrypt/decrypt)
- INV-3: Plaintext detection heuristics
- Error cases: wrong key, corrupt data, bad key size

DOCS: docs/universe/IMPLEMENTATION_Universe_Graph.md (Phase U3)
"""

import os
import tempfile
import pytest

from runtime.crypto.aes256_content_encryptor import ContentEncryptor, CryptoError
from runtime.crypto.rsa_key_manager import KeyManager
from runtime.crypto.space_key_distribution_and_rotation import SpaceKeyManager
from runtime.crypto.encrypted_field_codec import (
    encode_b64,
    decode_b64,
    is_plaintext,
    is_plaintext_vector,
    encrypt_node_fields,
    decrypt_node_fields,
)


# =============================================================================
# AES-256-GCM Content Encryption
# =============================================================================

class TestContentEncryptor:
    """Tests for AES-256-GCM content encryption."""

    def test_encrypt_decrypt_roundtrip_string(self):
        """Encrypt and decrypt a string field -- roundtrip must be lossless."""
        key = os.urandom(32)
        plaintext = "Hello, encrypted universe!"
        ciphertext = ContentEncryptor.encrypt(plaintext, key)
        decrypted = ContentEncryptor.decrypt(ciphertext, key)
        assert decrypted == plaintext

    def test_encrypt_decrypt_roundtrip_unicode(self):
        """Roundtrip with unicode content."""
        key = os.urandom(32)
        plaintext = "Contre-Terre: cites de lumiere -- monde interieur"
        ciphertext = ContentEncryptor.encrypt(plaintext, key)
        assert ContentEncryptor.decrypt(ciphertext, key) == plaintext

    def test_encrypt_decrypt_roundtrip_empty_string(self):
        """Empty strings should roundtrip correctly."""
        key = os.urandom(32)
        ciphertext = ContentEncryptor.encrypt("", key)
        assert ContentEncryptor.decrypt(ciphertext, key) == ""

    def test_encrypt_decrypt_roundtrip_long_text(self):
        """Long text (simulating full node content)."""
        key = os.urandom(32)
        plaintext = "X" * 100_000
        ciphertext = ContentEncryptor.encrypt(plaintext, key)
        assert ContentEncryptor.decrypt(ciphertext, key) == plaintext

    def test_ciphertext_differs_from_plaintext(self):
        """Ciphertext must not contain plaintext bytes."""
        key = os.urandom(32)
        plaintext = "secret content"
        ciphertext = ContentEncryptor.encrypt(plaintext, key)
        assert plaintext.encode() not in ciphertext

    def test_different_ivs_produce_different_ciphertexts(self):
        """Same key + same plaintext should produce different ciphertexts (random IV)."""
        key = os.urandom(32)
        plaintext = "same input every time"
        ct1 = ContentEncryptor.encrypt(plaintext, key)
        ct2 = ContentEncryptor.encrypt(plaintext, key)
        assert ct1 != ct2  # Different random IVs

    def test_wrong_key_fails_decryption(self):
        """Decryption with wrong key must raise CryptoError, not return garbage."""
        key1 = os.urandom(32)
        key2 = os.urandom(32)
        ciphertext = ContentEncryptor.encrypt("secret", key1)
        with pytest.raises(CryptoError):
            ContentEncryptor.decrypt(ciphertext, key2)

    def test_corrupt_ciphertext_fails(self):
        """Corrupted ciphertext must raise CryptoError."""
        key = os.urandom(32)
        ciphertext = ContentEncryptor.encrypt("data", key)
        corrupted = ciphertext[:10] + b"\xff" + ciphertext[11:]
        with pytest.raises(CryptoError):
            ContentEncryptor.decrypt(corrupted, key)

    def test_truncated_ciphertext_fails(self):
        """Too-short ciphertext must raise CryptoError."""
        key = os.urandom(32)
        with pytest.raises(CryptoError):
            ContentEncryptor.decrypt(b"short", key)

    def test_bad_key_size_raises(self):
        """Key must be exactly 32 bytes."""
        with pytest.raises(CryptoError):
            ContentEncryptor.encrypt("data", b"too_short")
        with pytest.raises(CryptoError):
            ContentEncryptor.encrypt("data", os.urandom(16))

    def test_encrypt_decrypt_embedding_roundtrip(self):
        """Encrypt and decrypt a float vector -- roundtrip must be lossless."""
        key = os.urandom(32)
        embedding = [0.1, 0.2, 0.3, -0.5, 1.0, 0.0]
        ciphertext = ContentEncryptor.encrypt_embedding(embedding, key)
        decrypted = ContentEncryptor.decrypt_embedding(ciphertext, key)
        assert len(decrypted) == len(embedding)
        for a, b in zip(embedding, decrypted):
            assert abs(a - b) < 1e-15

    def test_encrypt_decrypt_large_embedding(self):
        """Roundtrip a 768-dimension embedding (typical size)."""
        key = os.urandom(32)
        embedding = [float(i) / 768 for i in range(768)]
        ciphertext = ContentEncryptor.encrypt_embedding(embedding, key)
        decrypted = ContentEncryptor.decrypt_embedding(ciphertext, key)
        assert len(decrypted) == 768
        for a, b in zip(embedding, decrypted):
            assert abs(a - b) < 1e-15

    def test_wrong_key_fails_embedding_decryption(self):
        """Embedding decryption with wrong key must raise CryptoError."""
        key1 = os.urandom(32)
        key2 = os.urandom(32)
        ciphertext = ContentEncryptor.encrypt_embedding([1.0, 2.0], key1)
        with pytest.raises(CryptoError):
            ContentEncryptor.decrypt_embedding(ciphertext, key2)

    def test_empty_embedding_roundtrip(self):
        """Empty embedding list should roundtrip."""
        key = os.urandom(32)
        ciphertext = ContentEncryptor.encrypt_embedding([], key)
        decrypted = ContentEncryptor.decrypt_embedding(ciphertext, key)
        assert decrypted == []


# =============================================================================
# RSA Key Manager
# =============================================================================

class TestKeyManager:
    """Tests for RSA-2048 key management."""

    def test_generate_keypair(self):
        """Generate a keypair and verify both parts are PEM-encoded."""
        private_pem, public_pem = KeyManager.generate_keypair()
        assert b"BEGIN PRIVATE KEY" in private_pem
        assert b"BEGIN PUBLIC KEY" in public_pem

    def test_load_private_key(self):
        """Load a private key from PEM bytes."""
        private_pem, _ = KeyManager.generate_keypair()
        key = KeyManager.load_private_key(private_pem)
        assert key.key_size == 2048

    def test_load_public_key(self):
        """Load a public key from PEM bytes."""
        _, public_pem = KeyManager.generate_keypair()
        key = KeyManager.load_public_key(public_pem)
        assert key.key_size == 2048

    def test_rsa_encrypt_decrypt_roundtrip(self):
        """RSA-OAEP encrypt/decrypt roundtrip for an AES key."""
        private_pem, public_pem = KeyManager.generate_keypair()
        aes_key = os.urandom(32)
        encrypted = KeyManager.rsa_encrypt(aes_key, public_pem)
        private_key = KeyManager.load_private_key(private_pem)
        decrypted = KeyManager.rsa_decrypt(encrypted, private_key)
        assert decrypted == aes_key

    def test_wrong_private_key_fails_decryption(self):
        """Decryption with wrong private key must raise CryptoError."""
        priv1, pub1 = KeyManager.generate_keypair()
        priv2, _ = KeyManager.generate_keypair()
        encrypted = KeyManager.rsa_encrypt(b"secret_key_material", pub1)
        wrong_key = KeyManager.load_private_key(priv2)
        with pytest.raises(CryptoError):
            KeyManager.rsa_decrypt(encrypted, wrong_key)

    def test_save_load_private_key_file(self):
        """Save and load private key from file."""
        private_pem, _ = KeyManager.generate_keypair()
        with tempfile.NamedTemporaryFile(suffix=".pem", delete=False) as f:
            path = f.name
        try:
            KeyManager.save_private_key(private_pem, path)
            loaded = KeyManager.load_private_key_from_file(path)
            assert loaded.key_size == 2048
        finally:
            os.unlink(path)

    def test_save_load_public_key_file(self):
        """Save and load public key from file."""
        _, public_pem = KeyManager.generate_keypair()
        with tempfile.NamedTemporaryFile(suffix=".pem", delete=False) as f:
            path = f.name
        try:
            KeyManager.save_public_key(public_pem, path)
            data = open(path, "rb").read()
            loaded = KeyManager.load_public_key(data)
            assert loaded.key_size == 2048
        finally:
            os.unlink(path)

    def test_load_nonexistent_file_raises(self):
        """Loading from nonexistent path must raise CryptoError."""
        with pytest.raises(CryptoError):
            KeyManager.load_private_key_from_file("/tmp/nonexistent_key.pem")

    def test_load_invalid_pem_raises(self):
        """Loading garbage PEM data must raise CryptoError."""
        with pytest.raises(CryptoError):
            KeyManager.load_private_key(b"this is not a PEM file")


# =============================================================================
# Space Key Distribution
# =============================================================================

class TestSpaceKeyManager:
    """Tests for per-Space key distribution and rotation."""

    def test_create_space_key(self):
        """Generated space key must be 32 bytes."""
        key = SpaceKeyManager.create_space_key()
        assert isinstance(key, bytes)
        assert len(key) == 32

    def test_grant_and_decrypt_key(self):
        """Grant a space key, then decrypt it -- roundtrip."""
        private_pem, public_pem = KeyManager.generate_keypair()
        space_key = SpaceKeyManager.create_space_key()
        skm = SpaceKeyManager()

        encrypted_b64 = skm.grant_key(space_key, public_pem)
        assert isinstance(encrypted_b64, str)  # Base64 string

        private_key = KeyManager.load_private_key(private_pem)
        decrypted = skm.decrypt_granted_key(encrypted_b64, private_key)
        assert decrypted == space_key

    def test_grant_key_different_actors_produce_different_ciphertexts(self):
        """Same space key granted to two actors -> different ciphertexts."""
        _, pub1 = KeyManager.generate_keypair()
        _, pub2 = KeyManager.generate_keypair()
        space_key = SpaceKeyManager.create_space_key()
        skm = SpaceKeyManager()

        enc1 = skm.grant_key(space_key, pub1)
        enc2 = skm.grant_key(space_key, pub2)
        assert enc1 != enc2

    def test_child_key_encrypt_decrypt_with_parent(self):
        """Encrypt child key with parent key and decrypt -- roundtrip."""
        parent_key = SpaceKeyManager.create_space_key()
        child_key = SpaceKeyManager.create_space_key()

        encrypted_b64 = SpaceKeyManager.encrypt_child_key_with_parent(child_key, parent_key)
        decrypted = SpaceKeyManager.decrypt_child_key_with_parent(encrypted_b64, parent_key)
        assert decrypted == child_key

    def test_wrong_parent_key_fails(self):
        """Decrypting child key with wrong parent key must fail."""
        parent_key = SpaceKeyManager.create_space_key()
        wrong_key = SpaceKeyManager.create_space_key()
        child_key = SpaceKeyManager.create_space_key()

        encrypted_b64 = SpaceKeyManager.encrypt_child_key_with_parent(child_key, parent_key)
        with pytest.raises(CryptoError):
            SpaceKeyManager.decrypt_child_key_with_parent(encrypted_b64, wrong_key)

    def test_rotate_key(self):
        """Key rotation generates new key and re-encrypts for all actors."""
        priv1, pub1 = KeyManager.generate_keypair()
        priv2, pub2 = KeyManager.generate_keypair()
        old_key = SpaceKeyManager.create_space_key()
        skm = SpaceKeyManager()

        new_key, encrypted_keys = skm.rotate_key(
            old_key,
            {"actor_1": pub1, "actor_2": pub2},
        )

        assert new_key != old_key
        assert len(new_key) == 32
        assert "actor_1" in encrypted_keys
        assert "actor_2" in encrypted_keys

        # Both actors can decrypt the new key
        pk1 = KeyManager.load_private_key(priv1)
        pk2 = KeyManager.load_private_key(priv2)
        assert skm.decrypt_granted_key(encrypted_keys["actor_1"], pk1) == new_key
        assert skm.decrypt_granted_key(encrypted_keys["actor_2"], pk2) == new_key

    def test_resolve_key_chain_single_level(self):
        """Resolve a key chain with a single parent-child hop."""
        priv, pub = KeyManager.generate_keypair()
        skm = SpaceKeyManager()

        parent_key = SpaceKeyManager.create_space_key()
        child_key = SpaceKeyManager.create_space_key()

        # Actor has access to parent
        encrypted_parent_b64 = skm.grant_key(parent_key, pub)
        # Child key encrypted with parent key
        encrypted_child_b64 = SpaceKeyManager.encrypt_child_key_with_parent(child_key, parent_key)

        pk = KeyManager.load_private_key(priv)
        resolved = skm.resolve_key_chain(
            encrypted_parent_b64,
            pk,
            [encrypted_child_b64],
        )
        assert resolved == child_key

    def test_resolve_key_chain_three_levels(self):
        """Resolve a key chain with root -> mid -> leaf."""
        priv, pub = KeyManager.generate_keypair()
        skm = SpaceKeyManager()

        root_key = SpaceKeyManager.create_space_key()
        mid_key = SpaceKeyManager.create_space_key()
        leaf_key = SpaceKeyManager.create_space_key()

        encrypted_root_b64 = skm.grant_key(root_key, pub)
        encrypted_mid_b64 = SpaceKeyManager.encrypt_child_key_with_parent(mid_key, root_key)
        encrypted_leaf_b64 = SpaceKeyManager.encrypt_child_key_with_parent(leaf_key, mid_key)

        pk = KeyManager.load_private_key(priv)
        resolved = skm.resolve_key_chain(
            encrypted_root_b64,
            pk,
            [encrypted_mid_b64, encrypted_leaf_b64],
        )
        assert resolved == leaf_key

    def test_resolve_key_chain_no_children(self):
        """Resolve with no children returns the ancestor key."""
        priv, pub = KeyManager.generate_keypair()
        skm = SpaceKeyManager()

        space_key = SpaceKeyManager.create_space_key()
        encrypted_b64 = skm.grant_key(space_key, pub)

        pk = KeyManager.load_private_key(priv)
        resolved = skm.resolve_key_chain(encrypted_b64, pk, [])
        assert resolved == space_key


# =============================================================================
# Encrypted Field Codec
# =============================================================================

class TestEncryptedFieldCodec:
    """Tests for the encrypted field codec."""

    def test_base64_encode_decode_roundtrip(self):
        """Base64 encode/decode roundtrip."""
        data = os.urandom(100)
        encoded = encode_b64(data)
        assert isinstance(encoded, str)
        decoded = decode_b64(encoded)
        assert decoded == data

    def test_invalid_base64_raises(self):
        """Invalid base64 string must raise CryptoError."""
        with pytest.raises(CryptoError):
            decode_b64("!!!not-base64!!!")

    def test_is_plaintext_short_strings(self):
        """Short strings are plaintext."""
        assert is_plaintext("hello") is True
        assert is_plaintext("") is True
        assert is_plaintext("short") is True

    def test_is_plaintext_with_spaces(self):
        """Strings with spaces are plaintext."""
        assert is_plaintext("this is a long string with spaces that exceeds the minimum length for detection") is True

    def test_is_plaintext_base64_like(self):
        """Long base64-like strings are not plaintext."""
        b64_str = encode_b64(os.urandom(100))
        assert is_plaintext(b64_str) is False

    def test_is_plaintext_vector_list(self):
        """List of floats is a plaintext vector."""
        assert is_plaintext_vector([0.1, 0.2, 0.3]) is True

    def test_is_plaintext_vector_none(self):
        """None is not plaintext (no data)."""
        assert is_plaintext_vector(None) is False

    def test_is_plaintext_vector_b64_string(self):
        """Base64 string is not plaintext vector (it's encrypted)."""
        b64_str = encode_b64(os.urandom(100))
        assert is_plaintext_vector(b64_str) is False

    def test_encrypt_node_fields_roundtrip(self):
        """Encrypt then decrypt a node dict -- all fields roundtrip."""
        key = os.urandom(32)
        node = {
            "id": "node_123",
            "content": "This is secret content.",
            "synthesis": "Summary of the node.",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
            "weight": 1.0,
            "name": "Test Node",
        }

        encrypted = encrypt_node_fields(node, key)

        # ID, weight, name should be unchanged
        assert encrypted["id"] == "node_123"
        assert encrypted["weight"] == 1.0
        assert encrypted["name"] == "Test Node"

        # Encrypted fields should be base64 strings, not plaintext
        assert isinstance(encrypted["content"], str)
        assert encrypted["content"] != node["content"]
        assert isinstance(encrypted["synthesis"], str)
        assert encrypted["synthesis"] != node["synthesis"]
        assert isinstance(encrypted["embedding"], str)

        # Decrypt roundtrip
        decrypted = decrypt_node_fields(encrypted, key)
        assert decrypted["content"] == node["content"]
        assert decrypted["synthesis"] == node["synthesis"]
        assert len(decrypted["embedding"]) == 5
        for a, b in zip(decrypted["embedding"], node["embedding"]):
            assert abs(a - b) < 1e-15

    def test_encrypt_node_fields_none_values(self):
        """None-valued fields should pass through unchanged."""
        key = os.urandom(32)
        node = {
            "id": "node_456",
            "content": None,
            "synthesis": None,
            "embedding": None,
        }
        encrypted = encrypt_node_fields(node, key)
        assert encrypted["content"] is None
        assert encrypted["synthesis"] is None
        assert encrypted["embedding"] is None

    def test_decrypt_with_wrong_key_raises(self):
        """Decrypting with wrong key must raise CryptoError."""
        key1 = os.urandom(32)
        key2 = os.urandom(32)
        node = {"content": "secret", "synthesis": "summary", "embedding": [1.0]}
        encrypted = encrypt_node_fields(node, key1)
        with pytest.raises(CryptoError):
            decrypt_node_fields(encrypted, key2)

    def test_encrypt_preserves_non_encrypted_fields(self):
        """Fields not in ENCRYPTED_FIELDS should be preserved exactly."""
        key = os.urandom(32)
        node = {
            "id": "abc",
            "content": "secret",
            "synthesis": "summary",
            "embedding": [1.0, 2.0],
            "node_type": "thing",
            "weight": 0.5,
            "custom_field": "preserved",
        }
        encrypted = encrypt_node_fields(node, key)
        assert encrypted["node_type"] == "thing"
        assert encrypted["weight"] == 0.5
        assert encrypted["custom_field"] == "preserved"


# =============================================================================
# Integration: Full Key Lifecycle
# =============================================================================

class TestFullKeyLifecycle:
    """Integration test: create space, grant key, encrypt content, rotate, decrypt."""

    def test_full_lifecycle(self):
        """End-to-end: create space key, encrypt content, grant to actor, decrypt."""
        # Setup actors
        priv_alice, pub_alice = KeyManager.generate_keypair()
        priv_bob, pub_bob = KeyManager.generate_keypair()
        skm = SpaceKeyManager()

        # Create space with key
        space_key = SpaceKeyManager.create_space_key()

        # Grant to Alice (owner) and Bob (member)
        alice_enc_key = skm.grant_key(space_key, pub_alice)
        bob_enc_key = skm.grant_key(space_key, pub_bob)

        # Encrypt content in space
        node = {
            "id": "moment_1",
            "content": "A secret moment in the organization hall.",
            "synthesis": "Secret moment summary.",
            "embedding": [0.5, -0.3, 0.8],
        }
        encrypted_node = encrypt_node_fields(node, space_key)

        # Alice decrypts
        alice_pk = KeyManager.load_private_key(priv_alice)
        alice_space_key = skm.decrypt_granted_key(alice_enc_key, alice_pk)
        decrypted_by_alice = decrypt_node_fields(encrypted_node, alice_space_key)
        assert decrypted_by_alice["content"] == node["content"]

        # Bob decrypts
        bob_pk = KeyManager.load_private_key(priv_bob)
        bob_space_key = skm.decrypt_granted_key(bob_enc_key, bob_pk)
        decrypted_by_bob = decrypt_node_fields(encrypted_node, bob_space_key)
        assert decrypted_by_bob["content"] == node["content"]

    def test_rotation_invalidates_old_key(self):
        """After rotation, old key cannot decrypt new content."""
        priv, pub = KeyManager.generate_keypair()
        skm = SpaceKeyManager()

        old_key = SpaceKeyManager.create_space_key()
        new_key, encrypted_keys = skm.rotate_key(old_key, {"actor": pub})

        # Encrypt with new key
        node = {"content": "post-rotation content", "synthesis": "summary"}
        encrypted = encrypt_node_fields(node, new_key)

        # Old key cannot decrypt
        with pytest.raises(CryptoError):
            decrypt_node_fields(encrypted, old_key)

        # New key can decrypt
        pk = KeyManager.load_private_key(priv)
        actor_new_key = skm.decrypt_granted_key(encrypted_keys["actor"], pk)
        decrypted = decrypt_node_fields(encrypted, actor_new_key)
        assert decrypted["content"] == "post-rotation content"
