Status codes reference
======================

Standard status words
---------------------

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - SW
     - Description
   * - ``0x9000``
     - Success. When secure channel is open, this is always the outer SW; the real SW is
       encrypted in the response data.
   * - ``0x63Cx``
     - Authentication failure. ``x`` = remaining tries. ``0x63C0`` = no tries left (power cycle
       required for PIN, or PUK tries exhausted for this session).
   * - ``0x6700``
     - Wrong data length.
   * - ``0x6982``
     - Security status not satisfied. MAC verification failed — secure channel is aborted.
       Returned without MAC.
   * - ``0x6983``
     - Path not allowed (e.g. pinless path doesn't start with EIP1581).
   * - ``0x6984``
     - Invalid data (decryption failed, invalid public key).
   * - ``0x6985``
     - Conditions not satisfied (secure channel not open, PIN not verified, card not
       initialized, seed not loaded).
   * - ``0x6986``
     - Command not allowed (key slot already filled, PIN auth disabled, xpub at depth < 3).
   * - ``0x6A80``
     - Incorrect data parameters (invalid format, bad PIN format, malformed path).
   * - ``0x6A86``
     - Incorrect P1/P2 parameter.
   * - ``0x6A88``
     - Referenced data not found (pinless path not set, clear pubkey read not allowed).
   * - ``0x6B00``
     - Wrong parameters (invalid parent key, unknown P1/P2 value).
   * - ``0x6D00``
     - Instruction not supported (e.g. INIT on already initialized card).
   * - ``0x9840``
     - PUK verification not successful (used in CHANGE PIN with P1=PUK).

Secure channel status words
----------------------------

When the secure channel is open, all response status words are ``0x9000`` in the outer
(plaintext) APDU. The actual status word is the last 2 bytes of the decrypted response data.

The only exception is ``0x6982``, which indicates the secure channel has been aborted and is
returned in plaintext (without MAC).

PIN retry behavior
------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Counter
     - Behavior
   * - Per-session (transient)
     - 3 tries per power cycle. After 3 failures, returns ``0x63C0`` until power cycle.
   * - Persistent (OwnerPIN)
     - 6 total tries across sessions. Depleted = PIN blocked, requires PUK to unblock.

PUK retry behavior
------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Counter
     - Behavior
   * - Per-session (transient)
     - 12 tries per power cycle. After 12 failures, returns ``0x63C0`` until power cycle.
   * - Persistent
     - None. PUK tries are unlimited across power cycles.
