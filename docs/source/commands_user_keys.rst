User Key & Configuration Commands
=================================

.. _cmd-add-user-key:

ADD USER KEY
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
     - ``0xD5``
     - ``0x00``
     - ``0x00``
     - var
     - MAC | Encrypted data

**Preconditions**: Secure Channel must be opened.

**Request Data — Slot 1 (EC 256r1, plaintext)** — 142 bytes

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Slot index
     - 1B
     - ``0x01``
   * - Info text
     - 64B
     - User-defined description (fixed 64 bytes)
   * - Public key
     - 65B
     - EC 256r1 uncompressed (``04 | X | Y``)
   * - PUK
     - 12B
     - PUK for authorization

**Request Data — Slot 2 (RSA 2048, plaintext)** — 333 bytes

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Slot index
     - 1B
     - ``0x02``
   * - Info text
     - 64B
     - User-defined description (fixed 64 bytes)
   * - RSA modulus
     - 256B
     - 2048-bit modulus, big-endian. Exponent must be 65537.
   * - PUK
     - 12B
     - PUK for authorization

.. note::

   RSA commands require extended frame format header.

**Request Data — Slot 3 (FIDO, plaintext)** — variable

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Slot index
     - 1B
     - ``0x03``
   * - Info text
     - 64B
     - User-defined description (fixed 64 bytes)
   * - CredID length
     - 1B
     - Length of credential ID (up to 64)
   * - CredID
     - 1-64B
     - FIDO credential identifier
   * - EC public key
     - 65B
     - EC 256r1 uncompressed (``04 | X | Y``)
   * - PUK
     - 12B
     - PUK for authorization

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6A80``
     - Invalid slot index
   * - ``0x6700``
     - Incorrect data length
   * - ``0x6985``
     - PIN not provided
   * - ``0x6984``
     - Invalid public key
   * - ``0x6986``
     - Slot already has a key (delete first)

Once a key is stored, it must be deleted with ``DELETE USER KEY`` before a new key can be
written to the same slot.

----

.. _cmd-check-user-key:

CHECK USER KEY
--------------

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
     - ``0xD6``
     - Mode
     - ``0x00``
     - var
     - MAC | Encrypted data

**Preconditions**: Secure Channel must be opened.

**P1=0x00 — Auth for Sign (single hash)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Slot index
     - 1B
     - ``0x01``-``0x03``
   * - Hash
     - 32B
     - Transaction hash to authorize
   * - Signature
     - var
     - EC 256r1 ASN.1 DER (slot 1/3) or RSA 2048 PKCS1 (slot 2)

**P1=0x10 — Auth for Sign (hash list)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Slot index
     - 1B
     - ``0x01``-``0x03``
   * - Hash count
     - 1B
     - Number of hashes (1-4, or 1-3 for FIDO)
   * - Hash list
     - n × 32B
     - Hashes to authorize (32B each)
   * - Signature
     - var
     - EC 256r1 ASN.1 DER (slot 1/3) or RSA 2048 PKCS1 (slot 2)

**P1=0x01 — Challenge Request**

No data required (or MAC only).

**Response Data** — 32 bytes

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Challenge
     - 32B
     - Random 256-bit nonce

**P1=0x02 — Challenge Response**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Slot index
     - 1B
     - ``0x01``-``0x03``
   * - Signature
     - var
     - Signature of the challenge (hash is provided by card internally)

On success, unlocks commands requiring PIN (except SIGN).

**P1P2=0x0301 — Read FIDO Credential ID**

**Response Data**:

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - CredID length
     - 1B
     - Length of credential ID
   * - CredID
     - var
     - FIDO credential identifier

**FIDO Signature Format (Slot 3)**

When slot 3 is used for auth-for-sign or challenge-response, the data includes a counter:

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Hash(es)
     - 32-97B
     - Transaction hash(es) to authorize
   * - Counter
     - 4B
     - FIDO monotonic counter
   * - EC signature
     - var
     - EC 256r1 ASN.1 DER

The card verifies as a webauthn "user verified" message:

.. code-block:: none

   sha256(rp_id) | 0x05 | counter | sha256(clientData)

Where ``rp_id = "cryptnox.ch"`` and ``clientData`` is a fixed JSON template with the hash as
challenge.

**Response Data (all modes except Challenge Request and CredID read)** — 1 byte

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Result
     - 1B
     - ``0x01`` = success, ``0x00`` = signature verification failed

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success (check result byte for verification outcome)
   * - ``0x6A80``
     - Invalid slot index or incorrect data
   * - ``0x6985``
     - FIDO key not registered (CredID read), or P1=2 before P1=1, or challenge
       expired (power cycle/deselect)

.. note::

   The card cannot be simultaneously unlocked for "PIN" commands and for SIGN. Use
   challenge-response (P1=1/2) for management commands, then auth-for-sign (P1=0/0x10) before
   signing.

   A failed challenge attempt requires a new challenge (P1=1) before retrying (P1=2).

----

DELETE USER KEY
---------------

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
     - ``0xD7``
     - ``0x00``
     - ``0x00``
     - var
     - MAC | Encrypted data

**Preconditions**: Secure Channel must be opened.

**Request Data (plaintext)** — 13 bytes

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Slot index
     - 1B
     - ``0x01``-``0x03``
   * - PUK
     - 12B
     - PUK for authorization

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6A80``
     - Invalid slot index
   * - ``0x6700``
     - Data length not 13 bytes
   * - ``0x63Cx``
     - Wrong PUK
   * - ``0x6986``
     - Slot is empty

----

SET PINLESS PATH
----------------

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
     - ``0xC1``
     - ``0x00``
     - ``0x00``
     - var
     - MAC | Encrypted data

**Preconditions**: Secure Channel opened, seed or extended key loaded.

**Request Data — Enable pinless (plaintext)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - PUK
     - 12B
     - PUK for authorization
   * - Path elements
     - 12-32B
     - 3-8 levels × 4 bytes (32-bit big-endian)

Path must start with ``m/43'/60'/1581'`` (EIP-1581 prefix):

.. code-block:: none

   0x8000002B | 0x8000003C | 0x8000062D | ...

**Request Data — Disable pinless (plaintext)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - PUK
     - 12B
     - PUK for authorization (no path = disable)

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
   * - ``0x6A80``
     - Data length not a multiple of 4 or out of range (12-32)
   * - ``0x6983``
     - Path doesn't start with EIP-1581 prefix
   * - ``0x6985``
     - No seed or extended key loaded

K1 key pair only.

----

.. _cmd-set-pin-auth:

SET PIN AUTH
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
     - ``0xC3``
     - ``0x00``
     - ``0x00``
     - var
     - MAC | Encrypted data

**Preconditions**: Secure Channel must be opened.

**Request Data (plaintext)** — 13 bytes

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Status
     - 1B
     - ``0x00`` = enable PIN auth; ``>0`` = disable PIN auth
   * - PUK
     - 12B
     - PUK for authorization

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x63Cx``
     - Wrong PUK
   * - ``0x6A80``
     - Data length is not 13 bytes
   * - ``0x6986``
     - Disable requested but no user public key loaded

When PIN auth is disabled, only user key authentication (challenge-response or auth-for-sign)
can be used.

----

SET PUB EXPORT
--------------

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
     - ``0xC5``
     - Feature
     - ``0x00``
     - var
     - MAC | Encrypted data

**Preconditions**: Secure Channel opened, seed loaded.

**P1 values**

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - P1
     - Description
   * - ``0x00``
     - xpub export capability
   * - ``0x01``
     - Clear public key reading (without PIN or SC)

**Request Data (plaintext)** — 13 bytes

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Status
     - 1B
     - ``0x00`` = disable; ``>0`` = enable
   * - PUK
     - 12B
     - PUK for authorization

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x63Cx``
     - Wrong PUK
   * - ``0x6A80``
     - Data length is not 13 bytes
   * - ``0x6985``
     - No seed or extended key loaded
   * - ``0x6A86``
     - P1 is not 0 or 1

Both features are disabled by default from factory/reset.
