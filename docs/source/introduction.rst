Introduction
============

The Cryptnox Hardware Wallet card is a JavaCard-based secure hardware wallet that provides hardware
security module (HSM)-grade protection for blockchain operations. It is engineered to manage
cryptographic keys, perform key derivation, and sign transactions directly within the card's
secure environment, ensuring that private keys never leave the Secure Element.

The card supports secure storage of seeds and private keys and offers compatibility with both
``secp256k1`` and ``secp256r1`` elliptic curves. It is capable of generating ECDSA signatures
and Bitcoin Schnorr signatures (BIP340) depending on the selected curve. User authentication
mechanisms include PIN, PUK, pairing key, and optional external authentication through a user
key or FIDO2 authenticator. These multiple layers of access control ensure both flexibility and
robust security.

Security model
--------------

The Cryptnox Hardware Wallet card is built on a Common Criteria EAL6+ certified Secure Element,
providing resistance to both physical and logical attacks. All sensitive data exchanges are
protected by a Secure Channel protocol, based on principles similar to GlobalPlatform SCP03,
which ensures mutual authentication, confidentiality, and integrity through ``AES-256``
encryption and ``CMAC``-based message authentication codes.

Access to card functions is enforced through PIN and PUK-based control, with retry limits and
delay mechanisms to prevent brute-force attacks. In addition to local authentication, users can
optionally employ an external key, such as a TPM, Secure Enclave, or FIDO2 device, to authorize
sensitive operations.

The design also supports a dual-card backup generation mode, allowing two cards to share identical
seeds securely. This redundancy mechanism guarantees recoverability without ever exporting or
revealing the private seed material outside the Secure Element.

.. important::

   Private keys and seeds are generated and stored exclusively within the Secure Element. There
   is no command or mechanism to extract raw key material from the card.

.. seealso::

   - :doc:`secure_channel` — detailed Secure Channel protocol and session key derivation
   - :doc:`authentication` — PIN, PUK, user key, and FIDO2 authentication mechanisms
   - :doc:`seed_management` — seed generation, dual generation mode, and key source types

Supported algorithms and curves
--------------------------------

The Cryptnox Hardware Wallet card supports a comprehensive suite of asymmetric, symmetric, and
hashing algorithms that align with current blockchain and authentication standards.

Elliptic curves
^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Curve
     - Usage
     - Signature types
   * - ``secp256k1``
     - Bitcoin, Ethereum, and other blockchain ecosystems
     - ECDSA, Schnorr (BIP340)
   * - ``secp256r1`` (NIST P-256)
     - Enterprise security, TLS, FIDO2/WebAuthn
     - ECDSA

Signature algorithms
^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Scheme
     - Curve
     - Notes
   * - ECDSA (canonical low-S)
     - ``secp256k1``, ``secp256r1``
     - DER-encoded, default mode
   * - ECDSA (EOSIO)
     - ``secp256k1``, ``secp256r1``
     - Filtered to fit EOSIO standard
   * - Schnorr (BIP340)
     - ``secp256k1`` only
     - 64-byte raw signature

.. seealso::

   :doc:`signing` — signature types, output formats, and pinless signing

Symmetric cryptography
^^^^^^^^^^^^^^^^^^^^^^

All secure messaging operations use ``AES-256 CBC`` for encryption and ``AES-256 CMAC`` for
message integrity and authentication within the Secure Channel.

Key derivation
^^^^^^^^^^^^^^

Hierarchical deterministic key derivation is implemented following:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Standard
     - Curve
     - Description
   * - ``BIP32``
     - ``secp256k1``
     - Bitcoin HD wallet standard
   * - ``SLIP-0010``
     - ``secp256r1``
     - Alternative derivation for non-k1 curves

Child keys are derived using ``HMAC-SHA512`` as per standard definitions. The card also supports
pinless path derivation, compatible with ``EIP-1581``, allowing selective derivation paths to
operate without requiring PIN entry.

.. seealso::

   :doc:`key_derivation` — dual curve support, derivation sources, and parent key caching

Randomness
^^^^^^^^^^

The Secure Element integrates a hardware True Random Number Generator (TRNG) compliant with
``AIS-20`` Class ``DRG.3``, used for generating seeds, keypairs, and session nonces.

Hash functions
^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Algorithm
     - Usage
   * - ``SHA-256``
     - Message digests, PIN/PUK verification, fingerprint computation
   * - ``SHA-512``
     - Session key derivation, ``HMAC-SHA512`` for BIP32/SLIP10

Standards compliance
^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Standard
     - Scope
   * - **ISO/IEC 7816** (Parts 1--4)
     - Smartcard electrical, transmission, and APDU communication
   * - **GlobalPlatform SCP03**
     - Secure, authenticated communication between host and card
   * - **BIP32**, **BIP39**, **BIP44**
     - Hierarchical deterministic wallet structures and derivation
   * - **SLIP10**
     - Key derivation for non-k1 curves
   * - **BIP340**
     - Schnorr signature scheme for Bitcoin / ``secp256k1``
   * - **EIP-1581**
     - Pinless derivation path standard

This compliance ensures compatibility across blockchain environments, enterprise identity
frameworks, and security infrastructures.
