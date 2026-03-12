Authentication
==============

PIN authentication
------------------

The PIN chosen during the initialization needs to be provided after each EC signature, because
a signature resets the PIN validity.

The PIN verification is done in a standard way through the secure channel. The PIN must be
between 4 and 9 figures long.

Retry behavior
^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Event
     - Behavior
   * - Per-session tries
     - The PIN can be tested **3 times** before a disconnection of the card is required.
   * - After power cycle
     - 3 more tries are available before the PIN state is locked.
   * - PIN locked
     - Requires unlocking with the PUK via the ``UNBLOCK PIN`` command.
   * - ``0x63C0`` response
     - Returned when tries need a power cycle, even if the PIN is correct.
   * - Persistent ``0x63C0``
     - After power cycle, if the card still throws ``0x63C0``, the PIN is blocked.

After a successful signature command, the PIN verification is reset. A PIN verification is valid
until the card powers off or a signature is performed.

.. seealso::

   - :ref:`cmd-verify-pin` command for the full APDU specification
   - :doc:`status_codes` for PIN and PUK retry counter details

User key authentication
-----------------------

Another way to authenticate the user is with an ``EC256r1`` or ``RSA`` key pair. There is a
random challenge to be signed for PIN-like behavior. The public key is registered in the card,
and the "blockchain" EC signature can be allowed with a signature from this user key: hash to be
signed with the card must be signed with the user key.

The goal of this function is to use the Cryptnox Hardware Wallet card (to make transactions) in conjunction
with a key storage such as iOS Secure Enclave Touch ID or a PC TPM, instead of using the PIN.

The PIN check and user authentication is reset after any EC signature (of all the authorized
hashes).

This user auth by ECDSA can also be performed by an external FIDO authenticator.

A user key can be uploaded in a slot only once, and requires the ``DELETE USER KEY`` command if
there is already a key in the slot.

Key slots
^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 10 25 65

   * - Slot
     - Key type
     - Format
   * - 1
     - ``EC 256r1``
     - X9.62 uncompressed (65 bytes: ``04 | X | Y``)
   * - 2
     - ``RSA 2048``
     - 256 bytes modulus, exponent must be ``65537``
   * - 3
     - FIDO
     - ``CredIDLength(1B) | CredID(up to 64B) | ECpubkey(65B)``

Authentication modes
^^^^^^^^^^^^^^^^^^^^

There are 2 kinds of user auth:

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Mode
     - P1
     - Description
   * - Challenge-response
     - ``0x01`` / ``0x02``
     - Auth for all commands except ``SIGN``. The card provides a random challenge,
       the user signs it.
   * - Auth for sign
     - ``0x00`` / ``0x10``
     - Auth the transaction hash. The challenge is one or a set of hashes to be
       "blockchain" signed. When ``P1`` is OR'd with ``0x10``, the data message is a
       hash list (1 to 4 hashes).

FIDO authentication
^^^^^^^^^^^^^^^^^^^

When the slot index is 3, this is a special case for a FIDO signature. The data must include
the counter, making the data input:

.. code-block:: none

   hash(33-97B) | counter(4B) | ECsignature(EC256r1 ASN1)

The card checks the signature as a WebAuthn "user verified" message:

.. code-block:: none

   sha256hash(rp_id) | [0x05] | counter_word | sha256hash(clientData)

Where:

- ``rp_id`` = ``"cryptnox.ch"``
- ``clientData`` = ``'{"type": "webauthn.get", "origin": "https://cryptnox.ch", "challenge": "", "clientExtensions": {}}'``

.. note::

   The restriction for FIDO2 user-auth-for-sign is a maximum of 3 hashes can be authorized at
   once (instead of 4).

Disabling PIN auth
------------------

With the ``SET PIN AUTH`` command, one can disable the PIN auth and only let the auth performed
by user authentication (public keys registered).

.. important::

   When PIN auth is disabled, only user key authentication (slots 1--3) can authorize operations.
   Make sure at least one user key is registered before disabling PIN auth.

.. seealso::

   - :ref:`cmd-add-user-key`, :ref:`cmd-check-user-key`, and :ref:`cmd-set-pin-auth` commands
     for full APDU specifications
   - :doc:`signing` for details on how signing resets authentication state
