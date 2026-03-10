Data Commands
=============

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
     - —
     - None (or MAC only)

**Preconditions**: Secure Channel must be opened.

**P1/P2 combinations**

.. list-table::
   :header-rows: 1
   :widths: 10 10 80

   * - P1
     - P2
     - Description
   * - ``0x00``
     - ``0x00``
     - Card info (name, email, sig counter)
   * - ``0x01-0x03``
     - ``0x00``
     - User key slot info (slot = P1)
   * - ``0x00``
     - ``0x01-0x03``
     - User data pages (page = P2-1)

**Response Data — P1=0, P2=0 (Card info)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Key source info
     - 1B
     - ``0x00``/``'K'``/``'X'``/``'L'``/``'S'``/``'D'`` (see :doc:`seed_management`)
   * - Name length
     - 1B
     - Length of owner name
   * - Name
     - 0-20B
     - Owner name
   * - Email length
     - 1B
     - Length of owner email
   * - Email
     - 0-60B
     - Owner email
   * - Signature counter
     - 4B
     - Big-endian unsigned integer

**Response Data — P1=1-3, P2=0 (User key slot)**

Requires PIN or challenge-response.

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Info text
     - 64B
     - User-provided description
   * - Public key
     - 65B or 256B
     - EC R1 (65B) or RSA (256B)

**Response Data — P2=1-3 (User data pages)**

Requires PIN or challenge-response.

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
     - SC not opened or PIN/challenge not validated (P2>0 or P1>0)
   * - ``0x6B00``
     - Invalid P1/P2 or user data slot out of range

.. note::

   When reading user data (P2>0), use extended frame format header to receive data larger
   than 256 bytes.

----

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
     - —
     - None (or MAC only)

**Preconditions**: Secure Channel opened, PIN or challenge-response validated.

**P1**: History slot number (0 to 148).

**Response Data** — 36 bytes

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
     - The hash that was signed

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6985``
     - SC not opened or PIN/challenge not performed
   * - ``0x6A86``
     - Invalid P1 (slot out of range)

----

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

**P1=0x00 — Write user data page**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - User data
     - 1-1200B
     - Data for this page

P2 = page index (0 to 2). Pages must be written sequentially from page 0. Total user data
length = (P2 × 1200) + data size.

**P1=0x01 — Write custom bytes**

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
     - PIN not validated, or previous pages not fully written
   * - ``0x6700``
     - Data length incorrect (>1200B for P1=0, !=16B for P1=1)
   * - ``0x6A86``
     - P1 not 0 nor 1, or P2 out of range
   * - ``0x6982``
     - Data too large (outside secure channel)

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
     - Derive with k1 (OR with bits 7-6 for source)
   * - ``0x11``
     - Derive with r1 (OR with bits 7-6 for source)

**P2 values**

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - P2
     - Description
   * - ``0x00``
     - Current derivation path
   * - ``0x01``
     - Public key
   * - ``0x02``
     - Extended public key (BIP32, P1 must be ``0x00``)

**Request Data — P1=0x01/0x11 (derive, plaintext)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Path elements
     - n × 4B
     - 32-bit big-endian integers (1 to 8 levels)

**Request Data — P1=0x00/0x10 P2=0x00/0x01**: No data.

**Response Data — P2=0x00 (path)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Path elements
     - n × 4B
     - Current derivation path (32-bit big-endian integers)

**Response Data — P2=0x01 (public key)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Public key
     - 65B
     - EC uncompressed point (``04 | X | Y``)

**Response Data — P2=0x02 (extended public key)**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Field
     - Size
     - Description
   * - Version
     - 4B
     - BIP32 version bytes (default: BTC mainnet)
   * - Depth
     - 1B
     - Derivation depth
   * - Fingerprint
     - 32B
     - Parent key fingerprint (needs external RIPEMD160 to get 4B)
   * - Child number
     - 4B
     - Child index
   * - Chain code
     - 32B
     - BIP32 chain code
   * - Public key
     - 33B
     - Compressed public key

Requires depth >= 3 (BIP44 compliance). Must be enabled via ``SET PUB EXPORT``.

**Status Words**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - SW
     - Description
   * - ``0x9000``
     - Success
   * - ``0x6985``
     - Not initialized, no key loaded, PIN not verified, or xpub disabled
   * - ``0x6A80``
     - Malformed path
   * - ``0x6A86``
     - Invalid P1/P2 combination
   * - ``0x6A88``
     - Pinless path not setup, or clear read not allowed
   * - ``0x6986``
     - xpub at depth < 3
   * - ``0x6983``
     - Pinless query but current path not in allowed range
   * - ``0x6700``
     - Current key requested with data present, or derive without data
