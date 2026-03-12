EC signature
============

Overview
--------

The card applet can sign any 256-bit hash provided, using ECDSA with 256k1 or 256r1 EC
parameters. Most blockchain systems use SHA2-256 to hash the message, but this card applet is
agnostic: the signature is performed on a hash provided by the user.

The derivation of the key pair node can also be done using the signature command (relative or
absolute). The card derives just before signing; this can't be used to sign with a different key,
and this cannot change the current stored key.

Signature types
---------------

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - P2
     - Signature Type
   * - ``0x00``
     - ECDSA with canonical low S
   * - ``0x01``
     - ECDSA with filter signature to fit EOSIO standard
   * - ``0x02``
     - Bitcoin Schnorr BIP340 signature (k1 only)

Ephemeral nonce
---------------

The ephemeral ``k`` used in the ECDSA and Schnorr is random and different for each signature.
For ECDSA, this is automatically performed by the Signature function of the underlying JCOP4
platform, which internally provides a source of high-quality randomness during the signature.

This applet does **not** use RFC6979 deterministic digital signature generation.

ECDSA output format
--------------------

The signature is encoded as an X9.62 ASN1 DER sequence of two INTEGER values, ``r`` and ``s``,
in that order:

.. code-block:: none

   SEQUENCE ::= { r INTEGER, s INTEGER }

Additionally, to be compatible with blockchain specific signatures, the S part of the signature
is always output as "canonical", changed for S to be on the "lower" side (S lower than n/2).

BIP340 Schnorr output format
-----------------------------

Returns 64 bytes ``R|S`` = 2x256 bits MSB first, as per BIP340 standard.

The 32-byte nonce rand value is directly provided by a random source in the JCOP4 platform.
Works only with k1 keys (current, derive or pinless).

Pinless signing
---------------

``P1 = 0x03`` is specifically designed for payment transactions. It can be executed without
Secure Channel (since no sensitive info is transmitted) and does not require PIN authentication.

The current derivation path on the card remains unchanged, but the signing process is performed
using the PIN-less derivation path previously defined using the ``SET PINLESS PATH`` command.

The pinless path is restricted to the EIP-1581 prefix (``m/43'/60'/1581'/...``).

PIN and auth reset after signing
---------------------------------

An EC signature resets the PIN or user key auth. A PIN verification (or user sign auth) must be
performed afterwards and before calling any commands which require user auth (or PIN) checked.

If several hashes are granted by user-auth-for-sign, the card expects the signatures to be done
in the exact same order as the authentication. The reset of the auth occurs when all signatures
are done (up to 4).

After a successful signature session, the user auth is left opened: if a PIN was provided, the PIN
stays verified for other commands. If a user key auth was used, the EC auth is opened for other
commands.

In case of bad PIN provided, the PIN auth is disengaged.

See the :ref:`cmd-sign` command for all details.
