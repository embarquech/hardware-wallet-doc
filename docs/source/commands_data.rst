Data Commands
=============

.. _cmd-read-data:

GET CARD INFO / READ DATA
--------------------------

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
     - ``0xFA``
     - Mode
     - Selector
     - ---
     - None (or MAC only)

**Preconditions**: Secure Channel must be opened.

This command is the main data-retrieval interface of the card. Depending on the P1/P2 combination,
it returns card-level metadata, user key slot information, or arbitrary user data pages. It is used
after establishing a secure channel to inspect the card's state and read back stored data.

**P1/P2 combinations**

.. list-table::
   :header-rows: 1
   :widths: 10 10 80

   * - P1
     - P2
     - Description
   * - ``0x00``
     - ``0x00``
     - Card info (name, email, signature counter)
   * - ``0x01-0x03``
     - ``0x00``
     - User key slot info (slot = P1)
   * - ``0x00``
     - ``0x01-0x03``
     - User data pages (page = P2-1)

**Response Data --- P1=0, P2=0 (Card info)**

When both P1 and P2 are zero, the card returns general identity and status information that was
set during initialization with the ``INIT`` command. This is useful to display the cardholder's name
and email, check whether a key has been loaded, and monitor the signing activity through the
signature counter.

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Key source info
     - 1B
     - ``0x00`` = no key; ``'K'`` = single k1 pair; ``'X'`` = extended k1 node; ``'L'`` = external seed; ``'S'`` = internal seed; ``'D'`` = dual generation (see :doc:`seed_management`)
   * - Name length
     - 1B
     - Length of owner name
   * - Name
     - 0-20B
     - Owner name (as set during ``INIT``)
   * - Email length
     - 1B
     - Length of owner email
   * - Email
     - 0-60B
     - Owner email (as set during ``INIT``)
   * - Signature counter
     - 4B
     - Big-endian unsigned integer, incremented with each ``SIGN``

**Response Data --- P1=1-3, P2=0 (User key slot)**

When P1 is set to a slot index (1--3) with P2=0, the card returns the description and public key
stored in that user key slot. These were originally written with the :ref:`ADD USER KEY <cmd-add-user-key>`
command. This requires PIN verification or a successful challenge-response beforehand.

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Info text
     - 64B
     - User-provided description (fixed 64 bytes, as written by ``ADD USER KEY``)
   * - Public key
     - 65B or 256B
     - EC R1 uncompressed (65B for slot 1/3) or RSA modulus (256B for slot 2)

**Response Data --- P2=1-3 (User data pages)**

When P2 is set to a page index (1--3), the card returns the user data stored on that page. Pages
are written with the :ref:`WRITE DATA <cmd-write-data>` command and can hold up to 1200 bytes each,
for a total of 3600 bytes of user-defined storage. This also requires PIN or challenge-response.

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - User data
     - 0-1200B
     - Data from the requested page

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6985``
     - Secure channel not opened, or PIN/challenge not validated (required when P1>0 or P2>0)
   * - ``0x6B00``
     - Invalid P1/P2 combination or user data slot out of range

.. note::

   When reading user data (P2>0), the command must be sent using the extended frame format header
   to receive data larger than 256 bytes. This is required by the ISO 7816 standard for long
   response payloads, even though the command frame itself is short.

----

.. _cmd-get-history:

GET HISTORY
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
     - ``0xFB``
     - Slot
     - ``0x00``
     - ---
     - None (or MAC only)

**Preconditions**: Secure Channel opened, PIN or challenge-response validated.

The card maintains a circular history buffer of the last 149 signing operations. Each entry records
the value of the signature counter at the time of signing and the 32-byte hash that was signed.
This allows the host application to audit past transactions and verify that the card's signing
history matches expected blockchain activity.

The history slot number is provided in P1 (0 to 148). Slot 0 is the most recent entry.

**Response Data** --- 36 bytes

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Signing counter
     - 4B
     - Big-endian unsigned integer (counter value at time of signing)
   * - Signed hash
     - 32B
     - The 32-byte hash that was signed in this transaction

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6985``
     - Secure channel not opened or PIN/challenge not performed
   * - ``0x6A86``
     - Invalid P1 (slot number out of range, must be 0--148)

----

.. _cmd-write-data:

WRITE DATA
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
     - ``0xFC``
     - Mode
     - Page
     - var
     - MAC | Encrypted data

**Preconditions**: Secure Channel opened, PIN or challenge-response validated.

This command writes data to one of two storage areas: the user data pages (P1=0) or the custom
bytes field (P1=1) that is returned in every ``SELECT`` response.

**P1=0x00 --- Write user data page**

The card provides three pages of user-defined storage, each up to 1200 bytes, for a total of
3600 bytes. Pages are indexed by P2 (0 to 2) and must be written sequentially starting from
page 0. The total user data length is computed as ``(P2 x 1200) + data_size``, meaning
that lower pages are considered fully written. The card verifies that previous pages were fully
written before allowing a higher page to be written; otherwise it returns ``0x6985``.

For example, writing 200 bytes with P2=1 sets the total user data length to 1400 bytes (1200
for page 0 + 200 for page 1). The data can later be read back with the
:ref:`READ DATA <cmd-read-data>` command.

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - User data
     - 1-1200B
     - Data for this page

**P1=0x01 --- Write custom bytes**

The custom bytes are 16 bytes of public data that are returned in every ``SELECT`` response. They
can be used to provide personal hints about how to authenticate with the card, or to indicate
what is stored inside. Take care that anyone who has physical access to the card can freely read
these bytes.

By default, the custom bytes are set to 16 times ``0x00``.

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Custom bytes
     - 16B
     - Public data returned in every ``SELECT`` response

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6985``
     - PIN not validated, or previous pages not fully written (P1=0)
   * - ``0x6700``
     - Data length incorrect (>1200B for P1=0, or not exactly 16B for P1=1)
   * - ``0x6A86``
     - P1 not 0 nor 1, or P2 out of range (0--2)
   * - ``0x6982``
     - Data too large (outside secure channel frame capacity)

----

.. _cmd-get-pubkey:

GET PUBKEY
----------

**Request APDU** (encrypted, or plaintext for pinless/clear read)

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
     - ``0xC2``
     - Derive
     - Export
     - var
     - MAC | Encrypted path (or empty)

**Preconditions**: Secure Channel opened, PIN or challenge-response validated (except pinless
or clear public key read), key loaded.

This is the primary command for exporting public keys from the card. It can return the current
key's public key, the current derivation path, or a full BIP32 extended public key (xpub).
It also supports on-the-fly derivation: the card computes the derived key from a given path
without changing the card's current derivation state, which is useful when the host needs
a public key at a specific path for address generation without affecting the signing key.

**P1 values**

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - P1
     - Description
   * - ``0x00``
     - Current key k1
   * - ``0x10``
     - Current key r1
   * - ``0x01``
     - Derive with k1 (OR with bits 7-6 for derivation source)
   * - ``0x11``
     - Derive with r1 (OR with bits 7-6 for derivation source)

When using derivation (P1 LSB = 1), the source key can be selected by OR'ing P1 with the
same derivation source flags as the ``DERIVE KEY`` command:

- Bits 7-6 = ``00``: derive from master
- Bits 7-6 = ``01``: derive from parent
- Bits 7-6 = ``10``: derive from current

**P2 values**

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - P2
     - Description
   * - ``0x00``
     - Read current derivation path
   * - ``0x01``
     - Read public key
   * - ``0x02``
     - Read extended public key (BIP32 xpub, P1 must be ``0x00``)

**Request Data --- P1=0x01/0x11 (derive, plaintext)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Path elements
     - n x 4B
     - 32-bit big-endian integers (1 to 8 levels)

When P1=0x00/0x10 with P2=0x00 or P2=0x01, no data is required.

**Response Data --- P2=0x00 (path)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Path elements
     - n x 4B
     - Current derivation path as 32-bit big-endian integers

**Response Data --- P2=0x01 (public key)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Public key
     - 65B
     - EC uncompressed point (``04 | X | Y``)

**Response Data --- P2=0x02 (extended public key)**

The xpub export must first be enabled using :ref:`SET PUB EXPORT <cmd-set-pub-export>` (P1=0).
By default this capability is disabled from factory and after reset.

The response approximately matches the binary serialization format defined in the BIP32 standard.
The difference is the fingerprint is given as 32 bytes (the full SHA-256 of the parent key) instead
of the standard 4 bytes --- the host must apply an external RIPEMD-160 computation and take the
first 4 bytes to obtain the final BIP32 fingerprint (except for the master key, which is all zeros).
There is no checksum, as the data is not Base58-encoded.

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Version
     - 4B
     - BIP32 version bytes (default: BTC mainnet ``0x0488B21E``)
   * - Depth
     - 1B
     - Derivation depth
   * - Fingerprint
     - 32B
     - Parent key fingerprint (needs external RIPEMD-160 to get 4B)
   * - Child number
     - 4B
     - Child index
   * - Chain code
     - 32B
     - BIP32 chain code
   * - Public key
     - 33B
     - Compressed public key

The xpub can only be read at depth >= 3, in compliance with the BIP44 standard (the first 3
levels are hardened). The first 4 version bytes can be changed on the fly by the host to match
the target blockchain; the card always sends BTC mainnet version bytes by default.

The extended public key is useful for wallet software to derive the last account address levels
outside the card, manage address changes for each transaction, compute payment addresses in
advance, and scan the address chain --- all without requiring the card for each derivation.

**Pinless and clear read modes**

The public key can be read without PIN or secure channel in two scenarios:

1. **Pinless path**: If a pinless path was set with :ref:`SET PINLESS PATH <cmd-set-pinless-path>`,
   and the current derivation path starts with the EIP-1581 prefix (``m/43'/60'/1581'/...``),
   the public key (P2=1) can be read without authentication. No derivation is allowed in this mode.

2. **Clear public key read**: If enabled via :ref:`SET PUB EXPORT <cmd-set-pub-export>` (P1=1),
   the current public key (P1=0/0x10, P2=1) can be read without PIN or secure channel. This is
   designed for point-of-sale systems that need to read the card's payment address via NFC tap.
   No derivation is allowed in this mode.

.. note::

   Using the derive option (P1 LSB=1), the card expects a path in the data. There is no way to
   derive with a null path within this command, so the master key cannot be read via live
   derivation. If the master public key is needed, set it as the current key with ``DERIVE KEY``
   and then read the current key.

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6985``
     - Not initialized, no key loaded, PIN not verified, or xpub export disabled
   * - ``0x6A80``
     - Malformed path
   * - ``0x6A86``
     - Invalid P1/P2 combination (e.g. P2=2 with P1 != 0)
   * - ``0x6A88``
     - Pinless path not set up, or clear read not allowed
   * - ``0x6986``
     - xpub requested at depth < 3
   * - ``0x6983``
     - Pinless query but current path not in the allowed range
   * - ``0x6700``
     - Current key requested with data present, or derive requested without data
