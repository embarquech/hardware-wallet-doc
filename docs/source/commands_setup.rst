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

The ``SELECT`` command is documented in the ISO 7816-4 specifications and is used to select
the application on the card, making it the active one. The data field is the AID of the
application.

After receiving the ATR from the card, this must be the first command sent. It provides basic
information about the card applet status and flags, which the client should use to determine
the card's current state and capabilities before proceeding with further operations.

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

The custom bytes can be used to provide personal hints about how to authenticate with the card,
or what's stored inside the card. Note that whoever has the card can freely and easily read
this data.

The card serial ID can be read with the ``GET MANUFACTURER CERTIFICATE`` command which provides
the card certificate signed by the manufacturer. The card serial is the serial of the provided
X509 certificate.

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success

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

This command reads the card's static EC R1 public key. During the installation of the applet,
the card initializes its own EC R1 key pair. This command is only useful for the manufacturer
at factory to send the Cryptnox certificate in the card, which contains this card public key,
thus authenticating the genuineness of the card.

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

This command reads the Cryptnox card X509 certificate. This command should be used after each
``SELECT`` and before the ``OPEN SECURE CHANNEL`` command in order to:

- Read the Card Serial Number. This is useful to get the right pairing key associated with
  the card, especially when the user client communicates with several cards and needs to
  associate the PairingKey with the instance SN.
- Read the card public key, to further check the ECDH card public key authenticity during
  the secure channel setup.
- Check if the card is genuine by verifying the certificate against the Cryptnox public key.

The answer is limited to 255 bytes per page. ``P2=0`` returns the first 253 bytes of the
certificate prepended with 2 bytes of its total length. ``P2>0`` returns the remaining parts,
paginated by 255 bytes.

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success

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
     - Random nonce for certificate freshness

This command generates and provides the card basic certificate. It should be used after each
``GET MANUFACTURER CERTIFICATE`` and before the ``OPEN SECURE CHANNEL`` command in order to
securely get the card ephemeral public key for the channel encryption key exchange.

The nonce is provided by the command query, so the certificate can only be refreshed and live
generated by the card. This ensures that the session public key is fresh and has not been
replayed from a previous session.

**Response Data** — variable (~138-140 bytes)

The basic card certificate is a special compact format:

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
     - ASN1-DER ECDSA signature over the above fields, signed with the card private key

The session public key is the ephemeral EC 256r1 card key for the ECDH secure channel
establishment. The signature is made from the concatenation of the tag, nonce and session
public key, signed with the card's static private key (whose public key is in the Cryptnox
certificate). This allows the client to verify the session key authenticity.

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

This command is only available when the applet is in pre-initialized state and successful
execution brings the applet into the initialized state. This command is needed to allow
securely storing secrets on the applet. Currently these are the PIN, PUK and pairing password.
The user can also enter personal info (name and email).

The client must take the public key received after the ``GET CARD CERTIFICATE`` command,
generate a random keypair and perform R1 EC-DH to generate an AES key. It must then generate
a random IV and encrypt the payload using AES-CBC with ISO/IEC 9797-1 Method 2 padding.

This scheme guarantees protection against passive MITM attacks. Since the applet has no
"owner" before the execution of this command, protection against active MITM cannot be
provided at this stage. However since the communication happens locally (either through NFC
or contacted interface) the realization of such an attack at this point is unrealistic.

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

The payload is the concatenation of the User data, PIN, PUK and the Secure Channel first
pairing secret. The User data consists of the User Name and the User Email, each prepended
with a byte indicating their length. For example: ``0x07 | 'Cryptnox' | 0x14 | 'contact@cryptnox.com'``.

These user fields can carry whatever information the user wants to input in the card: their
name, an ID number, a key identifier, etc.

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

The PIN must be 4 to 9 figure number characters (``'0'``-``'9'``). If the PIN is less than 9
bytes, it must be filled with ``0x00`` until 9 chars long.

After successful execution, this command cannot be executed anymore (except after a full reset
with PUK). The regular SecureChannel (with pairing) is active and PIN and PUK are initialized
and validated.

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
     - Decryption invalid (wrong encryption key or bad padding)

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

This APDU command is the first step to establish a Secure Channel session. A session is
aborted when the application is deselected, either directly or because of a card power off
or tear away.

In a standard use of the applet, just after selecting the applet, the client opens a secure
channel using their PairingKey for this card. The user generates an EC key pair for the session
and provides the public key part in this command.

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

When ``P1=0xFF``, the PUK can be used as a pairing key. This is useful when the user has lost
their pairing info: the PUK hashed 32 times with SHA256 can always be used as a pairing key.

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

The card generates a random 256-bit salt which is sent to the client.

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Session salt
     - 32B
     - Random salt for key derivation

**Key derivation** — performed identically by both card and client:

.. code-block:: none

   ECDHsecret = PrivateKey . CounterpartPublicKey (x-coordinate)

   For the card:  ECDHsecret = SessionCardPrivateKey . SessionUserPublicKey (x)
   For the user:  ECDHsecret = SessionUserPrivateKey . SessionCardPublicKey (x)

   AESkey | MACkey = SHA512( ECDHsecret | PairingKey | Salt )
   [0..31]  = AESkey  (256-bit encryption key)
   [32..63] = MACkey  (256-bit MAC key)

The ``SessionCardPublicKey`` is received in the ``GET CARD CERTIFICATE`` response. The
``SessionUserPublicKey`` is transmitted to the card in this command.

For the mutual authentication, any IV can be used for the first encrypted message. Then the
IV to use is the latest MAC field received from the counterpart.

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

This APDU command allows both parties to verify that the keys generated in the
``OPEN SECURE CHANNEL`` step are matching and thus guarantee authentication of the counterpart.

The data sent by both parties is a 256-bit random number. The APDU data is sent encrypted
with the keys generated in the ``OPEN SECURE CHANNEL`` step. Each party must verify the MAC
of the received APDU. If the MAC and padding can be verified, it means that both parties are
using the same keys.

Only after this step has been executed can the secure channel be considered to be opened and
other commands sent.

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

If the authentication fails the card responds with ``0x6982``. In this case the
``OPEN SECURE CHANNEL`` command must be repeated to generate new keys.

.. note::

   Once the secure channel is opened, for commands requiring a secure channel, the status
   error codes are sent back as encrypted data through the tunnel. The last 2 bytes of the
   decoded data are the command status word, and the "outer plain" data are always ``0x9000``.
   The real status word is the one being encrypted in the secure channel inner data payload.

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

Update the SecureChannel PairingKey for a new one. The PUK is required for authorization.

In case the current pairing key was lost, preventing the opening of any secure channel (needed
to change it), one has to use the PUK derived key as the pairing key (key index ``0xFF`` in
``OPEN SECURE CHANNEL``). The PUK pairing slot can't be changed this way, but it is
automatically updated when the PUK is changed.

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

**Total plaintext**: 44 bytes.

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
