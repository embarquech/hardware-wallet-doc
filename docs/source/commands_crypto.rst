Cryptographic Commands
======================

.. _cmd-verify-pin:

VERIFY PIN
----------

**Request APDU** (encrypted)

.. list-table::
   :header-rows: 1
   :widths: 12 12 12 12 12 40

   * - CLA
     - INS
     - P1
     - P2
     - LC
     - Data
   * - ``0x80``
     - ``0x20``
     - ``0x00``
     - ``0x00``
     - var
     - MAC | Encrypted PIN (or empty)

**Preconditions**: Secure Channel must be opened.

**Request Data (plaintext)** — two modes:

*Query retries (no data)*: Send with empty data. Returns 1 byte for PIN retries left.

*Verify PIN*:

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - PIN
     - 4-9B
     - Digit characters ``'0'``-``'9'``

**Response Data (query mode)** — 1 byte

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Retries remaining
     - 1B
     - Number of PIN attempts left

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - PIN correct (verified for session)
   * - ``0x63Cx``
     - Wrong PIN. x = remaining attempts
   * - ``0x63C0``
     - Session tries exhausted (power cycle required) or PIN blocked
   * - ``0x6700``
     - Incorrect data length
   * - ``0x6986``
     - Card not initialized or PIN auth disabled

**Retry behavior**: 3 attempts per power cycle (transient counter). 6 total attempts across
sessions (persistent OwnerPIN). When persistent counter reaches 0, PIN is blocked and
``UNBLOCK PIN`` is required.

----

CHANGE PIN
----------

**Request APDU** (encrypted)

.. list-table::
   :header-rows: 1
   :widths: 12 12 12 12 12 40

   * - CLA
     - INS
     - P1
     - P2
     - LC
     - Data
   * - ``0x80``
     - ``0x21``
     - Selector
     - ``0x00``
     - var
     - MAC | Encrypted data

**Preconditions**: Secure Channel must be opened.

**P1=0x00 — Change PIN** (PIN already verified):

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - New PIN
     - 9B
     - 4-9 digits, right-padded with ``0x00``

**P1=0x00 — Change PIN** (PIN not verified, use PUK):

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - New PIN
     - 9B
     - 4-9 digits, right-padded with ``0x00``
   * - PUK
     - 12B
     - Current PUK for authorization

**P1=0x01 — Change PUK**:

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - New PUK
     - 12B
     - New PUK code
   * - Current PUK
     - 12B
     - Current PUK for authorization

**Total plaintext**: 24 bytes

**P1=other** — Returns remaining PIN tries with ``0x63Cx``. Resets any user auth.

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6A80``
     - Invalid PIN/PUK format
   * - ``0x6985``
     - PIN not validated or card not initialized
   * - ``0x9840``
     - Wrong PUK (when P1=0x01)
   * - ``0x63Cx``
     - Remaining PIN tries (when P1=other)

----

UNBLOCK PIN
-----------

**Request APDU** (encrypted)

.. list-table::
   :header-rows: 1
   :widths: 12 12 12 12 12 40

   * - CLA
     - INS
     - P1
     - P2
     - LC
     - Data
   * - ``0x80``
     - ``0x22``
     - ``0x00``
     - ``0x00``
     - var
     - MAC | Encrypted data

**Preconditions**: Secure Channel opened, PIN must be blocked, PinAuth enabled.

**Request Data (plaintext)** — 21 bytes

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - PUK
     - 12B
     - PUK code
   * - New PIN
     - 9B
     - 4-9 digits, right-padded with ``0x00``

On success, PIN is changed, unblocked and authenticated for the rest of the session.

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6A80``
     - Format invalid (not 21 bytes or non-digit PIN)
   * - ``0x6985``
     - PIN is not blocked or PinAuth disabled
   * - ``0x63Cx``
     - Wrong PUK. x = remaining tries before power cycle

PUK tries: 12 per power cycle, unlimited across power cycles.

----

.. _cmd-load-key:

LOAD KEY
--------

**Request APDU** (encrypted)

.. list-table::
   :header-rows: 1
   :widths: 12 12 12 12 12 40

   * - CLA
     - INS
     - P1
     - P2
     - LC
     - Data
   * - ``0x80``
     - ``0xD0``
     - Key type
     - ``0x00``
     - var
     - MAC | Encrypted data

**Preconditions**: Secure Channel opened, PIN or challenge-response validated.

**P1 values**

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - P1
     - Description
   * - ``0x01``
     - ECC SECP256k1 keypair
   * - ``0x02``
     - ECC SECP256k1 extended keypair (with chain code)
   * - ``0x03``
     - Binary seed (BIP39, 16-64 bytes)
   * - ``0x04``
     - Dual Gen part 1 (init half-key generation)
   * - ``0x05``
     - Dual Gen part 2 (receive other card's key)

**P1=0x01 — EC keypair (plaintext)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Tag ``0xA1``
     - 1B
     - Keypair template tag
   * - Template length
     - 1-2B
     - BER-TLV length
   * - Tag ``0x80``
     - 1B
     - Public key tag (optional)
   * - Public key length
     - 1-2B
     - BER-TLV length
   * - Public key
     - 65B
     - EC uncompressed point (optional)
   * - Tag ``0x81``
     - 1B
     - Private key tag
   * - Private key length
     - 1-2B
     - BER-TLV length
   * - Private key
     - 32B
     - EC private key scalar
   * - PIN
     - 9B
     - Right-padded with ``0x00`` (omit if user auth done)

**P1=0x02 — Extended keypair**: Same as P1=0x01 plus Tag ``0x82`` = chain code (32B).

**P1=0x03 — Binary seed (plaintext)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Seed
     - 16-64B
     - BIP39 binary seed
   * - PIN
     - 9B
     - Right-padded with ``0x00`` (omit if user auth done)

**P1=0x04 — Dual Gen part 1 (plaintext)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - PIN
     - 9B
     - Right-padded with ``0x00`` (omit if user auth done)

**Response Data (P1=0x04)**: Signed public key for the dual generation.

**P1=0x05 — Dual Gen part 2 (plaintext)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Other card's signed public key
     - var
     - Public key + signature from the other card
   * - PIN
     - 9B
     - Right-padded with ``0x00`` (omit if user auth done)

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success. PIN is validated for the session.
   * - ``0x63Cx``
     - Wrong PIN
   * - ``0x6A80``
     - Invalid format, invalid dual signature, or PIN expected
   * - ``0x6A86``
     - Invalid P1
   * - ``0x6986``
     - Key/seed already loaded (requires reset)

.. note::

   This command can only be performed once. There's no way to erase the seed except with a
   full reset using the PUK. The PIN-less path is reset after loading.

----

.. _cmd-derive-key:

DERIVE KEY
----------

**Request APDU** (encrypted)

.. list-table::
   :header-rows: 1
   :widths: 12 12 12 12 12 40

   * - CLA
     - INS
     - P1
     - P2
     - LC
     - Data
   * - ``0x80``
     - ``0xD1``
     - Options
     - ``0x00``
     - var
     - MAC | Encrypted path

**Preconditions**: Secure Channel opened, PIN or challenge-response validated, seed loaded.

**P1 bit fields**

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Bits
     - Description
   * - bit 4
     - ``0`` = secp256k1; ``1`` = secp256r1
   * - bits 7-6
     - ``00`` = from master; ``01`` = from parent; ``10`` = from current

**Request Data (plaintext)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Path elements
     - n × 4B
     - Sequence of 32-bit big-endian integers (0 to 8 levels). Empty = master key.

Each path element is 4 bytes. Hardened derivation: set bit 31 (OR with ``0x80000000``).
Maximum depth: 8 levels.

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6A80``
     - Invalid format or depth > 8
   * - ``0x6B00``
     - Derivation from parent but no valid parent cached
   * - ``0x6985``
     - No seed loaded or PIN not verified

----

GENERATE TRNG RANDOM
--------------------

**Request APDU** (encrypted)

.. list-table::
   :header-rows: 1
   :widths: 12 12 12 12 12 40

   * - CLA
     - INS
     - P1
     - P2
     - LC
     - Data
   * - ``0x80``
     - ``0xD3``
     - Size
     - ``0x00``
     - —
     - None

**Preconditions**: Secure Channel must be opened.

**P1**: Output size in bytes (16 to 64, must be a multiple of 4).

**Response Data**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Random data
     - P1 bytes
     - Raw TRNG output from the chip

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6A86``
     - Invalid P1 (not 16-64 or not multiple of 4)

Does not change any state in the card.

----

GENERATE KEY
------------

**Request APDU** (encrypted)

.. list-table::
   :header-rows: 1
   :widths: 12 12 12 12 12 40

   * - CLA
     - INS
     - P1
     - P2
     - LC
     - Data
   * - ``0x80``
     - ``0xD4``
     - ``0x00``
     - ``0x00``
     - var
     - MAC | Encrypted PIN

**Preconditions**: Secure Channel opened.

**Request Data (plaintext)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - PIN
     - 9B
     - Right-padded with ``0x00`` (omit if user auth done)

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success. PIN is validated for the session.
   * - ``0x63Cx``
     - Wrong PIN
   * - ``0x6986``
     - Seed/key already loaded
   * - ``0x6A80``
     - PIN expected or bad data

Generates a new seed on-card using the chip TRNG (AIS 20 class DRG.3). Can only be performed
once after a card reset. Key source is set to ``'S'``.

----

.. _cmd-sign:

SIGN
----

**Request APDU** (encrypted, except pinless mode)

.. list-table::
   :header-rows: 1
   :widths: 12 12 12 12 12 40

   * - CLA
     - INS
     - P1
     - P2
     - LC
     - Data
   * - ``0x80``
     - ``0xC0``
     - Key/derive
     - Sig type
     - var
     - MAC | Encrypted data (or plaintext for pinless)

**Preconditions**: Secure Channel opened (except pinless), PIN or user auth or pinless, key
loaded.

**P1 values**

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - P1
     - Description
   * - ``0x00``
     - Current key (k1)
   * - ``0x10``
     - Current key (r1)
   * - ``0x01``
     - Derive + sign with k1 (OR with bits 7-6 for source)
   * - ``0x11``
     - Derive + sign with r1 (OR with bits 7-6 for source)
   * - ``0x03``
     - Pinless path (k1 only, no SC required)

**P2 values**

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - P2
     - Description
   * - ``0x00``
     - ECDSA with canonical low S
   * - ``0x01``
     - ECDSA with EOSIO canonical filter
   * - ``0x02``
     - Bitcoin Schnorr BIP340 (k1 only)

**Request Data — P1=0x00/0x10 (current key, plaintext)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Hash
     - 32B
     - SHA256 hash to sign
   * - PIN
     - 9B
     - Right-padded with ``0x00`` (omit if user auth or pinless)

**Request Data — P1=0x01/0x11 (derive + sign, plaintext)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Hash
     - 32B
     - SHA256 hash to sign
   * - Path elements
     - n × 4B
     - Derivation path (32-bit big-endian integers)
   * - PIN
     - 9B
     - Right-padded with ``0x00`` (omit if user auth)

**Request Data — P1=0x03 (pinless, plaintext, no SC)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Hash
     - 32B
     - SHA256 hash to sign

**Response Data — ECDSA (P2=0x00 or 0x01)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Signature
     - 70-72B
     - ASN.1 DER X9.62 format: ``SEQUENCE { r INTEGER, s INTEGER }``

**Response Data — BIP340 Schnorr (P2=0x02)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - R
     - 32B
     - Schnorr R component (MSB first)
   * - S
     - 32B
     - Schnorr S component (MSB first)

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6A80``
     - Data too short or path not multiple of 4
   * - ``0x6A88``
     - Pinless path not defined (P1=0x03)
   * - ``0x6985``
     - No key loaded
   * - ``0x63Cx``
     - Wrong PIN
   * - ``0x6700``
     - Data length mismatch with expected PIN
   * - ``0x6B00``
     - Unknown P1 or P2

.. note::

   After a successful signature, PIN/user auth is reset. A new verification is required before
   the next sign. When multiple hashes are authorized via user key auth, signatures must be
   performed in the exact same order.

----

DECRYPT
-------

**Request APDU** (encrypted)

.. list-table::
   :header-rows: 1
   :widths: 12 12 12 12 12 40

   * - CLA
     - INS
     - P1
     - P2
     - LC
     - Data
   * - ``0x80``
     - ``0xC4``
     - Mode
     - ``0x00``
     - var
     - MAC | Encrypted data

**Preconditions**: Secure Channel opened, PIN or user auth, seed loaded.

**P1 values**

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - P1
     - Description
   * - ``0x00``
     - Output symmetric key
   * - ``0x01``
     - Decrypt data in card

Uses the fixed derivation path: ``m/17'/910196630'/2006168372'/332516148'/580566270'``
(SLIP17, URI="openpgp://cryptnox", index=0).

Symmetric key = ``SHA256( privateKey . PubKey )``, where ``privateKey`` is the EC R1 key at the
fixed path.

**P1=0x00 — Output symmetric key (plaintext, no user auth)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - PIN
     - 9B
     - Right-padded with ``0x00`` (omit if user auth done)
   * - PubKey
     - 65B
     - Third-party EC R1 uncompressed point

**Total**: 74B (with PIN) or 65B (user auth).

**P1=0x00 — Response Data** — 32 bytes

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Symmetric key
     - 32B
     - ``SHA256(ECDH shared secret)`` = ``IV(16B) | AESkey(16B)``

**P1=0x01 — Decrypt in card (plaintext, no user auth)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - PIN
     - 9B
     - Right-padded with ``0x00`` (omit if user auth done)
   * - PubKey
     - 65B
     - Third-party EC R1 uncompressed point
   * - Encrypted data
     - n × 16B
     - AES-CBC encrypted data (must be 16-byte aligned)

**P1=0x01 — Response Data**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Decrypted data
     - var
     - Plaintext output (padding left to caller)

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6A80``
     - Incorrect data length
   * - ``0x6985``
     - No key/seed loaded
   * - ``0x63Cx``
     - Wrong PIN
   * - ``0x6982``
     - Data too large (outside secure channel)

----

RESET
-----

**Request APDU** (encrypted)

.. list-table::
   :header-rows: 1
   :widths: 12 12 12 12 12 40

   * - CLA
     - INS
     - P1
     - P2
     - LC
     - Data
   * - ``0x80``
     - ``0xFD``
     - ``0x00``
     - ``0x00``
     - var
     - MAC | Encrypted PUK

**Preconditions**: Secure Channel must be opened.

**Request Data (plaintext)** — 12 bytes

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - PUK
     - 12B
     - PUK code

Erases everything in the card: seed, keys, PIN, PUK, pairing, user data. Card returns to
pre-initialized state.

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x63Cx``
     - Wrong PUK (x = remaining tries before power cycle)
   * - ``0x63C0``
     - Power cycle required before new PUK attempts
   * - ``0x6A80``
     - Data length is not 12 bytes

.. note::

   In case of power loss during reset, the card may have keys deleted but remain initialized.
   A second reset would then be needed for a full reset.
