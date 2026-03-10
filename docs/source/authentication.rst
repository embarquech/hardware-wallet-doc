Authentication
==============

PIN Authentication
------------------

The PIN chosen during the initialization needs to be provided after each EC signature, because
a signature resets the PIN validity.

The PIN verification is done in a standard way through the secure channel. The PIN must be
between 4 and 9 figures long.

Retry Behavior
^^^^^^^^^^^^^^

- The PIN can be tested **3 times** before a disconnection of the card is required.
- After a power cycle, it can be tested **3 more times** before the PIN state is locked.
- When locked, the PIN requires unlocking with the PUK.
- When PIN tries need a power cycle, the command always returns ``0x63C0``, even if the PIN
  is inserted correctly.
- After a power cycle, if the card still throws ``0x63C0``, the PIN is blocked and the
  ``UNBLOCK PIN`` command must be used.

After a successful signature command, the PIN verification is reset. A PIN verification is valid
until the card powers off or a signature is performed.

See the :ref:`cmd-verify-pin` command for more details.

User Key Authentication
-----------------------

Another way to authenticate the user is with an EC256r1 or RSA key pair. There's a random
challenge to be signed for PIN-like behavior. The public key is registered in the card, and
the "blockchain" EC signature can be allowed with a signature from this user key: hash to be
signed with the card must be signed with the user key.

The goal of this function is to use the Basic wallet card (to make transactions) in conjunction
with a key storage such as iOS secure enclave Touch ID or a PC TPM, instead of using the PIN.

The PIN check and user authentication is reset after any EC signature (of all the authorized
hashes).

This user auth by ECDSA can also be performed by an external FIDO authenticator.

A user key can be uploaded in a slot only once, and requires a delete user key command if
there's already a key in the slot.

Key Slots
^^^^^^^^^

- **Slot 1**: EC 256r1 public key (X9.62 uncompressed format, 65 bytes: ``04|X|Y``)
- **Slot 2**: RSA 2048 public key (256 bytes modulus, exponent must be 65537)
- **Slot 3**: FIDO key (``CredIDLength(1B) | CredID(up to 64B) | ECpubkey(65B)``)

Authentication Modes
^^^^^^^^^^^^^^^^^^^^

There are 2 kinds of user auth:

**Challenge-Response** (``P1=1`` and ``P1=2``):
  Auth for all commands except SIGN. The card provides a random challenge, the user signs it.

**Auth for Sign** (``P1=0`` or ``P1=0x10``):
  Auth the transaction hash. The challenge is one or a set of hashes to be "blockchain" signed.
  When ``P1`` is OR'd with ``0x10``, the data message is a hash list (1 to 4 hashes).

FIDO Authentication
^^^^^^^^^^^^^^^^^^^

When the slot index is 3, this is a special case for a FIDO signature. The data must include
the counter, making the data input:

.. code-block:: none

   hash(33-97B) | counter(4B) | ECsignature(EC256r1 ASN1)

The card checks the signature as a webauthn "user verified" message:

.. code-block:: none

   sha256hash(rp_id) | [0x05] | counter_word | sha256hash(clientData)

Where:

- ``rp_id = "cryptnox.ch"``
- ``clientData = '{"type": "webauthn.get", "origin": "https://cryptnox.ch", "challenge": "", "clientExtensions": {}}'``

The restriction for FIDO2 user-auth-for-sign is a maximum of 3 hashes can be authorized at once
(instead of 4).

Disabling PIN Auth
------------------

With the ``SET PIN AUTH`` command, one can disable the PIN auth and only let the auth performed
by user authentication (public keys registered).

See the :ref:`cmd-add-user-key`, :ref:`cmd-check-user-key`, and :ref:`cmd-set-pin-auth` commands
for all details.
