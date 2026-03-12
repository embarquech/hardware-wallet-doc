Key derivation
==============

Overview
--------

The card applet is fully compliant with ``BIP32`` (``secp256k1`` curve) and ``SLIP10``
(``secp256r1`` curve), except the maximum depth of derivation from the master key is
**8 levels**.

The card stores the present key pair (and its parent), used for signature. This can be changed
using the ``DERIVE KEY`` command, giving a relative path (from the present or parent key pair),
or an absolute path (from the master key pair).

.. seealso::

   :doc:`seed_management` for how the master seed is generated or loaded before derivation
   can be used.

Dual curve support
------------------

The card can derive with:

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Curve
     - Standard
     - Usage
   * - ``secp256k1``
     - ``BIP32``
     - Bitcoin, Ethereum, and other blockchain ecosystems
   * - ``secp256r1``
     - ``SLIP10``
     - Enterprise security, TLS, FIDO2/WebAuthn

A flag in ``DERIVE KEY``, ``GET PUBKEY``, or ``SIGN`` is used to select one or the other curve.
There are 2 separate key trees in the card, one for ``secp256r1`` and one for ``secp256k1``.
They are separated, only linked from the same seed.

Derivation sources
------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - P1 bits 7-6
     - Source
   * - ``00``
     - Derive from master keys (absolute path)
   * - ``01``
     - Derive from parent keys
   * - ``10``
     - Derive from current keys (relative path)
   * - ``11``
     - Reserved

Parent key caching
------------------

The ability to start derivation from the parent keys allows to more efficiently switch between
children of the same key. Note however that only the immediate parent of the current key is
cached so one cannot use this to go back in the keys hierarchy.

If no valid parent key is available (e.g., when the current key pair is the master root), the
status code ``0x6B00`` is returned.

.. note::

   Parent key caching is particularly useful for wallet software that needs to iterate over
   multiple child addresses (e.g., ``m/44'/60'/0'/0/0`` through ``m/44'/60'/0'/0/n``) without
   re-deriving from the master each time.

Performance considerations
--------------------------

For ease of use, the user can derive from the root master node key pair (absolute path) at each
card startup, or even before each signature. This takes some time. It is better to store
intermediate public keys hash and check the status to observe the current key pair in use.

This off-card complex key management is not needed if the signature volume is below one thousand
per day.

.. seealso::

   - :ref:`cmd-derive-key` and :ref:`cmd-get-pubkey` commands for the full APDU specifications
   - :doc:`signing` for on-the-fly derivation during signature operations
