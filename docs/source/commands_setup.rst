Setup & Channel Commands
========================

.. _cmd-select:

SELECT
------

**Request APDU**

.. list-table::
   :header-rows: 1
   :widths: 12 12 12 12 12 40

   * - CLA
     - INS
     - P1
     - P2
     - LC
     - Data
   * - ``0x00``
     - ``0xA4``
     - ``0x04``
     - ``0x00``
     - ``0x07``
     - AID

**Request Data**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - AID
     - 7B
     - Application identifier: ``0xA0000010000112``

**Response Data** — 24 bytes

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Applet type
     - 1B
     - ``'B'`` = Basic
   * - Applet version
     - 3B
     - Major.Middle.Minor (e.g. ``0x01 0x06 0x00`` = v1.6.0)
   * - Status flags
     - 2B
     - Big-endian short, see below
   * - PubKey flags
     - 2B
     - Big-endian short, see below
   * - Custom bytes
     - 16B
     - User-defined, written by ``WRITE DATA`` (``0xFC`` P1=1). Default: ``0x00``

**Status flag bits** (bit 15 = MSB, bit 0 = LSB):

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Bit
     - Meaning
   * - 6
     - Initialized
   * - 5
     - Seed (master seed or EC pair loaded)
   * - 4
     - Pin Auth possible
   * - 3
     - Pinless enabled
   * - 2
     - xpub output enabled
   * - 1
     - Clear read of current public key enabled

**PubKey flag bits**:

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Bit
     - Meaning
   * - 0
     - User Public Key #1 (ECDSA 256r1) active
   * - 1
     - User Public Key #2 (RSA 2048) active
   * - 2
     - User Public Key #3 (FIDO2) active

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success

The ``SELECT`` command is documented in ISO 7816-4 and is used to select the application on the
card. The card serial ID can be read with ``GET MANUFACTURER CERTIFICATE``.

----

GET CARD PUBKEY
---------------

**Request APDU**

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
     - ``0xF4``
     - ``0x00``
     - ``0x00``
     - —
     - None

**Response Data** — 65 bytes

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Card public key
     - 65B
     - EC R1 uncompressed point (``04 | X | Y``)

This command reads the card's static EC R1 public key, generated during applet installation.
Used by the manufacturer at factory to create the Cryptnox certificate.

----

.. _cmd-get-mnftr-cert:

GET MANUFACTURER CERTIFICATE
-----------------------------

**Request APDU**

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
     - ``0xF7``
     - ``0x00``
     - Page
     - —
     - None

**P2 values**

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - P2
     - Description
   * - ``0x00``
     - First 253 bytes of certificate + 2 bytes length prefix
   * - ``0x01+``
     - Remaining pages, 255 bytes each

**Response Data**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Certificate length
     - 2B
     - Big-endian short (P2=0 only)
   * - Certificate data
     - up to 253B/255B
     - X509 certificate fragment

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success

Should be used after each ``SELECT`` and before ``OPEN SECURE CHANNEL`` to:

- Read Card SN and associate with the right pairing key
- Read the card public key to check ECDH authenticity
- Check if the card is genuine against Cryptnox CA public key

----

.. _cmd-get-card-cert:

GET CARD CERTIFICATE
--------------------

**Request APDU**

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
     - ``0xF8``
     - ``0x00``
     - ``0x00``
     - ``0x08``
     - Nonce

**Request Data**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Nonce
     - 8B
     - Random nonce for freshness

**Response Data** — variable (~138-140 bytes)

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Tag
     - 1B
     - ``'C'`` (0x43)
   * - Nonce
     - 8B
     - Echo of the provided nonce
   * - Session public key
     - 65B
     - Ephemeral EC 256r1 card key for ECDH
   * - Signature
     - 70-72B
     - ASN1-DER ECDSA signature with the card private key

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6984``
     - Nonce length is not 8 bytes

Should be used after ``GET MANUFACTURER CERTIFICATE`` and before ``OPEN SECURE CHANNEL`` to
securely get the card ephemeral session public key.

----

.. _cmd-init:

INIT
----

**Request APDU**

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
     - ``0xFE``
     - ``0x00``
     - ``0x00``
     - var
     - PubKey(LV) | IV | Encrypted payload

**Preconditions**: Card must be in pre-initialized state.

**Request Data (wire format)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - PubKey length
     - 1B
     - Length of the EC public key (65)
   * - PubKey
     - 65B
     - Client ephemeral EC R1 uncompressed point for ECDH
   * - IV
     - 16B
     - AES-CBC initialization vector
   * - Encrypted payload
     - var
     - AES-CBC encrypted parameters (ISO 9797-1 M2 padded)

**Decrypted payload content**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Name length
     - 1B
     - Length of owner name (0-20)
   * - Name
     - 0-20B
     - Owner name
   * - Email length
     - 1B
     - Length of owner email (0-60)
   * - Email
     - 0-60B
     - Owner email
   * - PIN
     - 9B
     - 4-9 digit PIN, right-padded with ``0x00``
   * - PUK
     - 12B
     - PUK code
   * - Pairing secret
     - 32B
     - First secure channel pairing key

**Encryption**: The AES key is the raw ECDH shared secret between the client ephemeral key and
the card session key from ``GET CARD CERTIFICATE``.

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6D00``
     - Applet already initialized
   * - ``0x6A80``
     - Invalid data (bad pubkey, non-digits in PIN, wrong decrypted length)
   * - ``0x6984``
     - Decryption invalid (wrong key or bad padding)

After success, the card is initialized. This command cannot be executed again (except after full
reset).

----

.. _cmd-open-sc:

OPEN SECURE CHANNEL
--------------------

**Request APDU**

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
     - ``0x10``
     - Key idx
     - ``0x00``
     - ``0x41``
     - Client session public key

**P1 values**

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - P1
     - Description
   * - ``0x00``
     - Pairing key slot 0
   * - ``0xFF``
     - Use ``SHA256^32(PUK)`` as pairing key

**Request Data**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Client session public key
     - 65B
     - EC 256r1 uncompressed point (``04 | X | Y``)

**Response Data** — 32 bytes

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Session salt
     - 32B
     - Random salt for key derivation

**Key derivation** (performed by both card and client):

.. code-block:: none

   ECDHsecret = PrivateKey . CounterpartPublicKey (x-coordinate)
   AESkey | MACkey = SHA512( ECDHsecret | PairingKey | Salt )
   [0..31] = AESkey (256-bit encryption key)
   [32..63] = MACkey (256-bit MAC key)

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6A86``
     - Invalid P1 (unknown pairing key index)
   * - ``0x6A80``
     - Data is not a valid public key

----

.. _cmd-mutually-auth:

MUTUALLY AUTHENTICATE
---------------------

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
     - ``0x11``
     - ``0x00``
     - ``0x00``
     - var
     - MAC | Encrypted random

**Request Data (plaintext before encryption)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Random
     - 32B
     - 256-bit random number

**Response Data (plaintext after decryption)** — 32 bytes

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Random
     - 32B
     - 256-bit random number from the card

Both parties verify the MAC of the received APDU. If verified, both sides use the same keys and
mutual authentication is confirmed. Only after this step is the secure channel considered open.

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6985``
     - Previous APDU was not ``OPEN SECURE CHANNEL``
   * - ``0x6982``
     - Authentication failed or data is not 256-bit

----

.. _cmd-change-pairing-key:

CHANGE PAIRING KEY
------------------

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
     - ``0xDA``
     - ``0x00``
     - ``0x00``
     - var
     - MAC | Encrypted data

**Preconditions**: Secure Channel must be opened.

**Request Data (plaintext)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - New PairingKey
     - 32B
     - New pairing secret
   * - PUK
     - 12B
     - Current PUK for authorization

**Total plaintext**: 44 bytes

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6700``
     - Data is not 44 bytes
   * - ``0x63Cx``
     - Wrong PUK (x = remaining tries before power cycle)
   * - ``0x6A86``
     - P1 is not 0

In case the current pairing key was lost, use the PUK derived key (``P1=0xFF``) to open a
secure channel, then call this command to set a new pairing key.
