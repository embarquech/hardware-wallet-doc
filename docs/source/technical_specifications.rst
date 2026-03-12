Technical specifications
========================

The Cryptnox Hardware Wallet card integrates advanced hardware and cryptographic capabilities to
deliver a secure, high-performance environment for blockchain operations and key management. It
is implemented on a certified Secure Element platform and adheres to international smartcard and
cryptographic standards.

Cryptographic capabilities
--------------------------

The Cryptnox Hardware Wallet card supports a broad range of cryptographic functions for blockchain
signing, enterprise authentication, and key derivation.

It operates on both ``secp256k1`` and ``secp256r1`` elliptic curves, maintaining independent key
derivation trees for each. The hierarchical deterministic wallet structure supports up to eight
levels of derivation depth as defined in ``BIP32`` (for ``secp256k1``) and ``SLIP10`` (for
``secp256r1``).

The card supports multiple signature schemes, including ECDSA (DER-encoded with canonical low-S
enforcement), EOSIO-compatible ECDSA, and ``BIP340`` Schnorr signatures for Bitcoin use cases.

For symmetric cryptography, the card uses ``AES-256 CBC`` for data encryption and ``AES-256
CMAC`` for message integrity. Key derivation follows the ``HMAC-SHA512`` standard used in
``BIP32`` and ``SLIP10``.

.. list-table:: Cryptographic summary
   :header-rows: 1
   :widths: 25 35 40

   * - Category
     - Algorithm
     - Details
   * - Asymmetric (signing)
     - ECDSA, Schnorr (BIP340)
     - ``secp256k1``, ``secp256r1``
   * - Symmetric (encryption)
     - ``AES-256 CBC``
     - Secure Channel data encryption
   * - Symmetric (integrity)
     - ``AES-256 CMAC``
     - Message authentication codes
   * - Key derivation
     - ``HMAC-SHA512``
     - BIP32 / SLIP10 child key derivation
   * - Hashing
     - ``SHA-256``, ``SHA-512``
     - Digests, verification, session keys
   * - Random generation
     - TRNG (``AIS-20 DRG.3``)
     - Seeds, keypairs, session nonces

.. seealso::

   - :doc:`signing` — signature types and output formats
   - :doc:`key_derivation` — derivation depth, dual curve support, and caching
   - :doc:`seed_management` — seed generation and dual generation mode

Communication protocols
-----------------------

The Cryptnox Hardware Wallet card communicates using ISO 7816 APDUs over the ``T=1`` protocol, with
full support for extended APDUs to handle larger payloads. All sensitive operations are performed
through an authenticated Secure Channel, established via ECDH and protected by ``AES-256``
encryption.

APDU model
^^^^^^^^^^

The card follows a standard command/response exchange structure:

.. code-block:: text

   CLA | INS | P1 | P2 | Lc | Data | Le

Extended APDUs (>255 bytes) are supported for operations that require large data exchanges.

.. seealso::

   :doc:`commands_setup`, :doc:`commands_crypto`, :doc:`commands_data`,
   :doc:`commands_user_keys` — full APDU command reference

T=1 protocol
^^^^^^^^^^^^^

A block-oriented communication model with built-in error detection and message chaining, ensuring
reliable data transfer even during extended or chained APDUs.

Secure channel
^^^^^^^^^^^^^^

The Secure Channel is derived through an ECDH exchange combined with the pairing key, producing
session keys via ``SHA-512`` derivation. These keys protect the session using ``AES-256 CBC``
(encryption) and ``AES-256 CMAC`` (integrity), with replay protection managed by nonces and
counters.

.. seealso::

   :doc:`secure_channel` — full protocol description, mutual authentication, and error conditions

Authentication
^^^^^^^^^^^^^^

Access control relies on a multi-tiered authentication framework:

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Method
     - Credential
     - Description
   * - **PIN**
     - 4--9 digits
     - Required before sensitive operations. Three failed attempts trigger a lockout,
       recoverable via the PUK.
   * - **PUK**
     - 12 characters
     - Used for PIN recovery and card reset, with unlimited attempts but enforced delay
       mechanisms.
   * - **Pairing key**
     - 32 bytes
     - Required to open a Secure Channel; recoverable from PUK if lost.
   * - **User keys**
     - ECDSA / RSA / FIDO2
     - External authentication keys uploaded to authorize transactions.
   * - **FIDO2**
     - Challenge-response
     - External authenticator such as a YubiKey, TPM, or Secure Enclave.

.. seealso::

   :doc:`authentication` — PIN retry behavior, user key slots, and FIDO authentication details

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

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Certification
     - Scope
   * - Common Criteria ``EAL6+``
     - Hardware and embedded software assurance
   * - ``FIPS 140-2/3``
     - Cryptographic primitives (``AES``, ``SHA``, ``RNG``)

The architecture is hardened against side-channel attacks (``DPA``/``SPA``) and fault injection
attempts, safeguarding against both passive and active threats.

Memory and isolation
^^^^^^^^^^^^^^^^^^^^

Persistent data is stored in secure ``EEPROM``, which is physically and logically isolated from
the JavaCard operating system.

Hardware-level protections prevent unauthorized reads, and all write and erase operations include
integrity verification routines. This isolation also enforces non-exportability of private keys
and seeds. The hierarchical key derivation engine supports up to eight levels of depth, consistent
with ``BIP32`` and ``SLIP10`` standards.

Key management
^^^^^^^^^^^^^^

Private keys and seeds never leave the Secure Element. The card supports a dual-seed generation
protocol, allowing two cards to securely generate and share identical seeds without ever exposing
key material.

Independent key derivation trees exist for both ``secp256k1`` and ``secp256r1`` curves, enabling
simultaneous use across blockchain and enterprise contexts.

All cryptographic operations are gated by PIN-based authentication, with optional pinless paths
available for predefined derivation slots where repeated authentication is not required.

.. important::

   There is no APDU command or mechanism to export private keys or seeds from the card. Key
   material is strictly non-extractable by design.

Communication security
^^^^^^^^^^^^^^^^^^^^^^

Card communication is based on ISO 7816 APDU exchanges using the ``T=1`` protocol, with full
support for extended-length APDUs.

A Secure Channel protocol, built on ECDH key exchange and ``AES-256`` encryption, ensures the
confidentiality and integrity of all exchanges.

Each session is mutually authenticated, protected with ``AES-256 CBC`` for encryption and
``AES-256 CMAC`` for integrity, and reinforced with nonce-based replay protection.

Hardware random number generator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The integrated TRNG, compliant with ``AIS-20`` Class ``DRG.3``, provides entropy for all
critical security operations including seed creation, keypair generation, and cryptographic
session nonces.

This guarantees randomness at the hardware level, essential for maintaining cryptographic
unpredictability.

Hardware and JavaCard platform
------------------------------

The Cryptnox Hardware Wallet card is built on the ``NXP JCOP 4.x`` Secure Element platform, a
JavaCard-based architecture recognized for its robust security and versatility.

It provides dedicated memory partitions for cryptographic key storage and hierarchical key
derivation trees, ensuring strict separation between the secure and application layers.

The integrated True Random Number Generator (TRNG) complies with ``AIS-20`` Class ``DRG.3``
certification, providing high-entropy randomness for seed generation, keypair creation, and
session nonces.

.. note::

   For a complete overview of the card's lifecycle, from ``SELECT`` through initialization,
   pairing, and reset, see :doc:`lifecycle`.
