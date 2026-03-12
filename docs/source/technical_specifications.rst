Technical specifications
========================

The Cryptnox Basic Wallet Card integrates advanced hardware and cryptographic capabilities to
deliver a secure, high-performance environment for blockchain operations and key management. It
is implemented on a certified Secure Element platform and adheres to international smartcard and
cryptographic standards.

Cryptographic capabilities
--------------------------

The Cryptnox Basic Wallet Card supports a broad range of cryptographic functions for blockchain
signing, enterprise authentication, and key derivation.

It operates on both secp256k1 and secp256r1 elliptic curves, maintaining independent key
derivation trees for each. The hierarchical deterministic wallet structure supports up to eight
levels of derivation depth as defined in BIP32 (for secp256k1) and SLIP10 (for secp256r1).

The card supports multiple signature schemes, including ECDSA (DER-encoded with canonical low-S
enforcement), EOSIO-compatible ECDSA, and BIP340 Schnorr signatures for Bitcoin use cases.

For symmetric cryptography, the card uses AES-256 CBC for data encryption and AES-256 CMAC for
message integrity. Key derivation follows the HMAC-SHA512 standard used in BIP32 and SLIP10.

These capabilities allow the card to act as a secure signing device for both blockchain
transactions and enterprise-level cryptographic operations.

Communication protocols
-----------------------

The Cryptnox Basic Wallet Card communicates using ISO 7816 APDUs over the T=1 protocol, with
full support for extended APDUs to handle larger payloads. All sensitive operations are performed
through an authenticated Secure Channel, established via ECDH and protected by AES-256
encryption.

APDU model
^^^^^^^^^^

The card follows a standard command/response exchange structure
(CLA | INS | P1 | P2 | Lc | Data | Le). Extended APDUs (>255 bytes) are supported for operations
that require large data exchanges.

T=1 protocol
^^^^^^^^^^^^^

A block-oriented communication model with built-in error detection and message chaining, ensuring
reliable data transfer even during extended or chained APDUs.

Secure channel
^^^^^^^^^^^^^^

The Secure Channel is derived through an ECDH exchange combined with the pairing key, producing
session keys via SHA-512 derivation. These keys protect the session using AES-256 CBC
(encryption) and AES-256 CMAC (integrity), with replay protection managed by nonces and
counters.

Authentication
^^^^^^^^^^^^^^

Access control relies on a multi-tiered authentication framework:

- **PIN** (4--9 digits) — required before executing sensitive operations such as signing. Three
  failed attempts trigger a lockout, recoverable via the PUK.
- **PUK** (12 characters) — used for PIN recovery and card reset, with unlimited attempts but
  enforced delay mechanisms.
- **Pairing key** (32 bytes) — required to open a Secure Channel; recoverable from PUK if lost.
- **User keys** — external authentication keys (ECDSA, RSA, or FIDO2) uploaded to authorize
  transactions.
- **FIDO2 authentication** — challenge-response mechanism using an external authenticator such
  as a YubiKey, TPM, or Secure Enclave.

Query/response model
^^^^^^^^^^^^^^^^^^^^

Communication is strictly one command per response, ensuring predictable and deterministic
interactions without concurrency.

Secure element features
-----------------------

The Secure Element serves as the foundation of the card's security model, designed to protect
cryptographic materials and enforce all access control mechanisms within a tamper-resistant
environment.

Security certifications
^^^^^^^^^^^^^^^^^^^^^^^

The card operates on a Common Criteria EAL6+ certified Secure Element, providing one of the
highest levels of assurance available for both hardware and embedded software. All cryptographic
primitives — AES, SHA, and RNG — are FIPS 140-2/3 compliant, ensuring interoperability and
validated cryptographic strength.

The architecture is hardened against side-channel attacks (DPA/SPA) and fault injection attempts,
safeguarding against both passive and active threats.

Memory and isolation
^^^^^^^^^^^^^^^^^^^^

Persistent data is stored in secure EEPROM, which is physically and logically isolated from the
JavaCard operating system.

Hardware-level protections prevent unauthorized reads, and all write and erase operations include
integrity verification routines. This isolation also enforces non-exportability of private keys
and seeds. The hierarchical key derivation engine supports up to eight levels of depth, consistent
with BIP32 and SLIP10 standards.

Key management
^^^^^^^^^^^^^^

Private keys and seeds never leave the Secure Element. The card supports a dual-seed generation
protocol, allowing two cards to securely generate and share identical seeds without ever exposing
key material.

Independent key derivation trees exist for both secp256k1 and secp256r1 curves, enabling
simultaneous use across blockchain and enterprise contexts.

All cryptographic operations are gated by PIN-based authentication, with optional pinless paths
available for predefined derivation slots where repeated authentication is not required.

Communication security
^^^^^^^^^^^^^^^^^^^^^^

Card communication is based on ISO 7816 APDU exchanges using the T=1 protocol, with full support
for extended-length APDUs.

A Secure Channel protocol, built on ECDH key exchange and AES-256 encryption, ensures the
confidentiality and integrity of all exchanges.

Each session is mutually authenticated, protected with AES-256 CBC for encryption and AES-256
CMAC for integrity, and reinforced with nonce-based replay protection.

Hardware random number generator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The integrated TRNG, compliant with AIS-20 Class DRG.3, provides entropy for all critical
security operations including seed creation, keypair generation, and cryptographic session nonces.

This guarantees randomness at the hardware level, essential for maintaining cryptographic
unpredictability.

Hardware and JavaCard platform
------------------------------

The Cryptnox Basic Wallet Card is built on the NXP JCOP 4.x Secure Element platform, a
JavaCard-based architecture recognized for its robust security and versatility.

It provides dedicated memory partitions for cryptographic key storage and hierarchical key
derivation trees, ensuring strict separation between the secure and application layers.

The integrated True Random Number Generator (TRNG) complies with AIS-20 Class DRG.3
certification, providing high-entropy randomness for seed generation, keypair creation, and
session nonces.

This combination of certified hardware and deterministic security primitives ensures both
reliability and protection against unauthorized access or tampering.
