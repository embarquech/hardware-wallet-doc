Cryptographic commands
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

The PIN verification is done in a standard way through the secure channel. The PIN chosen
during the initialization needs to be provided after each EC signature, because a signature
resets the PIN validity.

If the PIN entry is correct, the card returns ``0x9000`` and the PIN is marked as authenticated
for the entire session (until the application is deselected, the card is reset/teared, or a
signature is performed).

When there is no data in the command, the card returns 1 byte indicating the number of PIN
retries left. This allows the client to check the PIN status without attempting a verification.

The PIN must be between 4 and 9 figures long.

**Request Data — Verify mode (plaintext)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - PIN
     - 4-9B
     - Digit characters ``'0'``-``'9'``

**Request Data — Query mode**: Send with empty data.

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

**Retry behavior**: The PIN can be tested 3 times before a disconnection of the card is
required. Then it can be tested 3 more times before the PIN state is locked, requiring
unlocking with PUK. When the number of tries reaches 3 (per session), the card needs a power
cycle before accepting new PIN verification, and it returns ``0x63C0``. After a power cycle,
if the card still throws ``0x63C0``, that means the PIN is blocked and the ``UNBLOCK PIN``
command must be used.

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

**Preconditions**: Secure Channel must be opened. To change the PIN: user PIN must be
verified (else PUK must be provided in data).

Change the PIN or PUK. In case of invalid format, the code ``0x6A80`` is returned. If the
conditions match, the PIN or PUK is updated and ``0x9000`` is returned.

The new PIN must be 9 chars long, must start with at least 4 figure characters (``'0'``-``'9'``).
If the PIN is less than 9 numbers, it must be filled with ``0x00`` until 9 chars long. The
PUK must be 12 bytes long.

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

The current PUK added for auth in data is mandatory if PinAuth is disabled, as the PIN can't
be verified. The new PIN is verified for the session (until card power cycle or EC signature),
except if PinAuth is disabled.

**P1=0x00 — Change PIN** (PIN not verified, use PUK instead):

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

**Total plaintext**: 24 bytes.

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
     - PIN not validated or card not initialized. Also returned when bad PUK
       provided to change PIN (this is considered as PIN not validated).
   * - ``0x9840``
     - PUK given is invalid (when P1=0x01)
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

Unblock the user PIN. The data field must contain exactly 21 chars, otherwise SW ``0x6A80``
is returned. The first 12 bytes are the PUK and the last 9 digits are the new PIN. If the
PUK is correct the PIN is changed to the given one, PIN is unblocked and authenticated for
the rest of the session. The status code ``0x9000`` is returned.

The PIN must be 9 chars long, must start with 4 figure characters (``'0'``-``'9'``). If the
PIN is less than 9 numbers, it must be filled with ``0x00`` until 9 chars long.

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

If the PUK is wrong, the SW ``0x63Cx`` is sent back; ``x`` is the remaining tries left before
a power cycle is required. PUK tries are unlimited, but only 12 tries can be performed on each
power cycle. The card needs to be powered off (and then on) before sending new PUK. Else it
throws ``0x63C0`` without checking the PUK.

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success (PIN unblocked and authenticated)
   * - ``0x6A80``
     - Format invalid (not 21 bytes or non-digit PIN)
   * - ``0x6985``
     - PIN is not blocked or PinAuth disabled
   * - ``0x63Cx``
     - Wrong PUK. x = remaining tries before power cycle

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

Load a seed or a key pair. Can also be used for dual generation of the seed (shared with
2 cards paired beforehand). Once a seed is loaded in the card, this card now behaves like
the one it was backup from. Be aware that key derivation paths are not backed up and must be
identical to retrieve the same key pairs.

The PIN must be at the end of the data, unless a user key auth was performed. PIN when
provided is always right-filled with ``0x00`` up to 9 bytes. Load key checks the last 9 bytes
as the PIN in case no user auth by key is valid.

**P1 values**

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - P1
     - Description
   * - ``0x01``
     - ECC SECP256k1 keypair (k1 only). Key source set to ``'K'``.
   * - ``0x02``
     - ECC SECP256k1 extended keypair with chain code (k1 only). Key source set to ``'X'``.
   * - ``0x03``
     - Binary seed (BIP39, 16-64 bytes). Master key nodes computed following SLIP10,
       compatible with BIP32. One master key for k1, one for r1. Key source set to ``'L'``.
   * - ``0x04``
     - Dual Gen part 1: initializes the dual generation seed mode and sends back a public
       key signed with the Basic Group key. Nothing is done about any key or seed loading
       at this stage.
   * - ``0x05``
     - Dual Gen part 2: receives the public key from the other card (plus signature). After
       this, both cards have a common seed. Key source set to ``'D'``.

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
     - Public key tag (optional, can be omitted)
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

**P1=0x02 — Extended keypair**: Same as P1=0x01 with additional Tag ``0x82`` = chain code (32B).

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

**Dual generation protocol** (P1=0x04 and P1=0x05):

.. code-block:: none

   card 1 : 80D00400         -> PublicKeySigned of the 1st card
   card 2 : 80D00400         -> PublicKeySigned of the 2nd card
   card 1 : 80D00500 PK2     -> Send 2nd card's signed key to 1st card
   card 2 : 80D00500 PK1     -> Send 1st card's signed key to 2nd card

After this, the 2 cards have a common seed ``SHA256(ECDH)``. One card is a backup of the
other, even if no secrets were leaked externally. Even the computer doing the transfer
exchange can't compute the seed (protected by ECDH). The computer can't be part of the key
exchange, as this requires a signature with a secret key only located within the cards.

The common seed can be checked by making a derivation path and reading the blockchain public
keys of the cards, which should match.

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
     - Invalid format, invalid dual signature, or PIN expected (data len < 9B)
   * - ``0x6A86``
     - Invalid P1
   * - ``0x6986``
     - Key/seed already loaded (requires reset)

.. note::

   This command can only be performed once. There's no way to erase the seed except with a
   full reset using the PUK. After successful loading with PIN, the PIN is validated for the
   session. The PIN-less path is reset. Unless a ``DERIVE KEY`` is sent, a subsequent ``SIGN``
   command will use the master keypair for signature.

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

This command is used before a signing session to generate a private key according to the
BIP32 and SLIP10 specifications. The generated key is used for all subsequent ``SIGN``
sessions. The maximum depth of derivation from the master key is 8. Any attempt to get
deeper results in ``0x6A80`` being returned.

The BIP32 specifications define a few checks which must be performed on the derived keys. If
these fail (mostly using r1 curve), there is a looping mechanism described by the SLIP10
proposal, enforced by the card.

The ability to start derivation from the parent keys allows to more efficiently switch between
children of the same key. Note however that only the immediate parent of the current key is
cached so you cannot use this to go back in the hierarchy. If no valid parent key is available
(e.g. when the current key is the master root), the status code ``0x6B00`` is returned.

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
     - Sequence of 32-bit big-endian integers (0 to 8 levels). Empty = set master key
       as current.

Each path element is 4 bytes. For hardened derivation, set bit 31 (OR with ``0x80000000``).

A client can perform a ``GET PUBKEY`` command to get the actual current key path and resume
derivation using a different path.

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
     - Derivation from parent but no valid parent cached (e.g. master is current)
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

Used to generate some random data from the chip internal TRNG (AIS 20 class DRG.3). The given
size with P1 shall be between 16 and 64 bytes and must be a multiple of 4 (16, 20, 24, ..., 64).

This command is only an output, to use the chip secure random number generator. For example to
generate a mnemonic in the host machine from a confident random source. It doesn't change any
state in the card.

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

Generates a new seed and stores keys completely on card. The state of the card after execution
is the same as if a ``LOAD KEY`` command had been performed. With the use of this command, the
seed secret never escapes the card protection. If performed the simple way, there's no way to
get a backup of this seed.

The key source is set to ``'S'``.

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
     - Seed/key already loaded (requires reset)
   * - ``0x6A80``
     - PIN expected or bad data

.. note::

   This command can be performed only once after a card reset, as there's no way to erase
   nor change the current wallet seed key, except with a reset with the PUK. After successful
   generation with PIN, the PIN is validated for the session.

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

The card applet can sign any 256-bit hash provided, using ECDSA with 256k1 or 256r1 EC
parameters. Most blockchain systems use SHA2-256 to hash the message, but this card applet
is agnostic from this, since the signature is performed on a hash provided by the user.

The ephemeral ``k`` used in the ECDSA and Schnorr is random and different for each signature.
For ECDSA, this is automatically performed by the Signature function of the underlying JCOP4
platform. This applet does not use RFC6979 deterministic digital signature generation.

The derivation of the key pair node can also be done using the signature command (relative or
absolute). The card derives just before signing. This can't be used to sign with a different
key, and this cannot change the current stored key.

Additionally, to be compatible with blockchain specific signatures, the S part of the
signature is always output as "canonical", changed for S to be on the "lower" side (S lower
than n/2).

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

``P1=0x03`` is specifically thought for payment transactions. It can be executed without
Secure Channel (since no sensitive info is transmitted) and does not require PIN
authentication. The current derivation path on the card remains unchanged, but the signing
process is performed using the PIN-less derivation path previously defined using the
``SET PINLESS PATH`` command.

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
     - 256-bit hash to sign
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
     - 256-bit hash to sign
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
     - 256-bit hash to sign

**Response Data — ECDSA (P2=0x00 or 0x01)**

The signature is encoded as an X9.62 ASN1 DER sequence: ``SEQUENCE { r INTEGER, s INTEGER }``.
For usage on some blockchains, one needs to calculate the recovery ID in addition to the
signature. To calculate the recovery ID, apply the same algorithm used for public key recovery
from a transaction starting with a recovery ID of 0. If the public key matches, you have found
the recovery ID, otherwise increment and try again.

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Signature
     - 70-72B
     - ASN.1 DER X9.62 format

**Response Data — BIP340 Schnorr (P2=0x02)**

Returns 64 bytes ``R|S`` = 2x256 bits MSB first, as per BIP340 standard. The 32-byte nonce
is provided by a random source in the JCOP4 platform. Works only with k1 keys.

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

**PIN behavior**: The PIN must be with a 9 numbers fixed length, right-filled with ``0x00``.
If there was no valid user auth or not in pinless mode, the data length expected is counted
with the PIN included. A PIN try is always counted when calling this command with a path data
longer than a 9 bytes PIN.

An EC signature resets the PIN or user key auth. That means that a PIN verification (or user
sign auth) must be performed afterwards and before calling any commands which require a user
auth. If several hashes are granted by user-auth-for-sign, the card expects the signatures
to be done in the exact same order as the authentication. The reset of the auth occurs when
all signatures are done (up to 4).

After a successful signature session, the user auth is left opened: if a PIN was provided,
the PIN stays verified for other commands. If a user key auth was used, the EC auth is opened
for other commands. In case of bad PIN provided, the PIN auth is disengaged.

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
     - Unknown P1 or P2, or P2=2 with P1 not k1

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

Generates a symmetric secret for simplified ECIES using an EC key in the BIP32 tree. This
command is inspired by DECipher in OpenPGP smartcards. This allows an asymmetric encryption
using a key in the card seed tree. Anyone can encrypt with a public key from the card, and
only the (private) key in the card can decrypt.

During the seed loading, the card saves in a dedicated key slot the result of a fixed
derivation path. The child EC key used for this command is fixed (relative to a given seed).
The path is computed with SLIP17 for the URI "openpgp://cryptnox" with index=0:

.. code-block:: none

   m/17'/910196630'/2006168372'/332516148'/580566270'

The symmetric key is computed as ``SHA256(k . PubKey)``, where ``k`` is the private ECP256r1
key in the "decrypt" key slot.

**P1 values**

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - P1
     - Description
   * - ``0x00``
     - Output symmetric key
   * - ``0x01``
     - Decrypt data in card using the derived AES key

**P1=0x00 — Output symmetric key (plaintext)**

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
     - Third-party EC R1 uncompressed point (``04 | X | Y``)

**Total**: 74B (with PIN) or 65B (user auth).

**Response Data (P1=0x00)** — 32 bytes

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Symmetric key
     - 32B
     - ``SHA256(ECDH)`` = ``IV(16B) | AESkey(16B)``

**P1=0x01 — Decrypt in card (plaintext)**

When P1 is not 0, the hashed ECDH is used internally as an AES128 key: ``IV | Key``, with
CBC. The padding is left to the outer system, so data must be padded to 16 bytes alignment
(and un-padded by the caller).

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

**Response Data (P1=0x01)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Decrypted data
     - var
     - Plaintext output

**Example usage**: Let's call the user Alice and her friend Bob. Alice reads the "encrypt"
public key by calling ``GET PUBKEY`` with derive-from-master and derive-r1 for the SLIP17
path, getting ``PKA``. Alice shares this public key with Bob. Bob generates an ephemeral
ECr1 key pair ``kb/PKB``, computes ``key = SHA256(kb . PKA)`` to get ``IV | AESkey``, encrypts
the message with AES-CBC, and shares the ciphertext with Alice along with ``PKB``. Alice calls
``DECRYPT`` with ``PIN | PKB | ciphertext`` and the card gives out the decrypted data.

The PIN/noPIN case in the data is inferred from the current user key auth status. If a user
auth was performed with a user signature (CheckUserKey), this command expects no PIN. If no
user auth was validated, this command expects a PIN prepending the data.

The PIN state is changed by this command: if wrong PIN, the auth is reset. If correct, the
PIN is validated.

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

When the PUK code is sent into the RESET command, the card is reset. The reset PUK code is
chosen during the initialization stage. The PUK reset code is a 12 characters long string,
which allows a full reset of the card. On top of this 12 chars secret, the reset is also
secured by the user pairing key mechanism (if secret). That means that resetting a card
requires, on top of the PUK, to know the PairingKey to send the command encrypted. Still,
the PUK can act as a PairingKey on its own.

The reset command erases everything in the card, and makes the card as it was before the
initialization. All data in the card will be reset, with no way to recover (except from
seed/mnemonic recovery).

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

.. note::

   The PUK tries are unlimited, but there's an internal loop hash that takes time inside the
   card for each try. Every 12 tries, a power cycle is required to perform new tries.

   In the case of a power loss during reset, the card can only have its blockchain keys deleted.
   The card would have the flag "seeded" false and "initialized" true. This would need another
   reset for a full reset, or the keys need to be generated/loaded again.

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
