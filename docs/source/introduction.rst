Introduction
============

Overview
--------

The Cryptnox Basic Wallet Card is a JavaCard-based secure hardware wallet that provides hardware
security module (HSM)-grade protection for blockchain operations. It is engineered to manage
cryptographic keys, perform key derivation, and sign transactions directly within the card's
secure environment, ensuring that private keys never leave the Secure Element.

The card supports secure storage of seeds and private keys and offers compatibility with both
secp256k1 and secp256r1 elliptic curves. It is capable of generating ECDSA signatures and Bitcoin
Schnorr signatures (BIP340) depending on the selected curve. User authentication mechanisms include
PIN, PUK, pairing key, and optional external authentication through a user key or FIDO2
authenticator. These multiple layers of access control ensure both flexibility and robust security.

Security model
--------------

The Cryptnox Basic Wallet Card is built on a Common Criteria EAL6+ certified Secure Element,
providing resistance to both physical and logical attacks. All sensitive data exchanges are
protected by a Secure Channel protocol, based on principles similar to GlobalPlatform SCP03,
which ensures mutual authentication, confidentiality, and integrity through AES-256 encryption
and CMAC-based message authentication codes.

Access to card functions is enforced through PIN and PUK-based control, with retry limits and
delay mechanisms to prevent brute-force attacks. In addition to local authentication, users can
optionally employ an external key, such as a TPM, Secure Enclave, or FIDO2 device, to authorize
sensitive operations.

The design also supports a dual-card backup generation mode, allowing two cards to share identical
seeds securely. This redundancy mechanism guarantees recoverability without ever exporting or
revealing the private seed material outside the Secure Element.

Supported algorithms and curves
--------------------------------

The Cryptnox Basic Wallet Card supports a comprehensive suite of asymmetric, symmetric, and
hashing algorithms that align with current blockchain and authentication standards.

Elliptic curves
^^^^^^^^^^^^^^^

Two primary elliptic curves are supported:

- **secp256k1** — widely used in Bitcoin, Ethereum, and other blockchain ecosystems. It supports
  both ECDSA and Schnorr (BIP340) signatures.
- **secp256r1** (NIST P-256) — commonly used for enterprise security, TLS, and FIDO2/WebAuthn
  authentication, supporting ECDSA signatures.

Signature algorithms
^^^^^^^^^^^^^^^^^^^^

The card implements multiple signature schemes, including:

- ECDSA (DER-encoded with canonical low-S enforcement)
- EOSIO-compatible ECDSA
- Schnorr (BIP340) for secp256k1 curve applications

Symmetric cryptography
^^^^^^^^^^^^^^^^^^^^^^

All secure messaging operations use AES-256 CBC for encryption and AES-256 CMAC for message
integrity and authentication within the Secure Channel.

Key derivation
^^^^^^^^^^^^^^

Hierarchical deterministic key derivation is implemented following:

- **BIP32** for secp256k1
- **SLIP-0010** for secp256r1

Child keys are derived using HMAC-SHA512 as per standard definitions. The card also supports
pinless path derivation, compatible with EIP-1581, allowing selective derivation paths to operate
without requiring PIN entry.

Randomness
^^^^^^^^^^

The Secure Element integrates a hardware True Random Number Generator (TRNG) compliant with
AIS-20 Class DRG.3, used for generating seeds, keypairs, and session nonces.

Hash functions
^^^^^^^^^^^^^^

The card supports both SHA-256 and SHA-512 for cryptographic operations, including message digest
generation, PIN/PUK verification, and session key derivation.

Standards compliance
^^^^^^^^^^^^^^^^^^^^

The Cryptnox Basic Wallet Card conforms to major industry standards and blockchain
interoperability protocols, including:

- **ISO/IEC 7816** (Parts 1--4) — defining smartcard electrical, transmission, and APDU
  communication standards.
- **GlobalPlatform Secure Channel Protocol** (SCP03-like) — ensuring secure, authenticated
  communication between the host and card.
- **BIP32, BIP39, BIP44, and SLIP10** — defining hierarchical deterministic wallet structures
  and derivation mechanisms.
- **BIP340** — defining Schnorr signature schemes for Bitcoin and secp256k1 curve applications.

This compliance ensures compatibility across blockchain environments, enterprise identity
frameworks, and security infrastructures.
