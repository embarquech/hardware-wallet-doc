Seed management
===============

Overview
--------

The applet manages a 256-bit master secret called the "seed". This is the BIP32 Master seed,
and can be externally computed from a mnemonic to a binary seed using BIP39. The key pairs
used for ECDSA are then computationally derived from this seed using SLIP10/BIP32 derivation
scheme.

Once the card has a seed or a master key, it is not possible to erase or change it, except by
performing a reset with the PUK.

Generation
----------

The master seed can be generated in the card using the random number generator in the chip
system (AIS 20 class DRG.3). With the use of the ``GENERATE KEY`` command, the seed secret
never escapes the card protection. If performed the simple way, there's no way to get a backup
of this seed.

Dual generation mode
^^^^^^^^^^^^^^^^^^^^

The Dual Generation mode allows a cross generation between 2 cards which then share a common
seed. One card is a backup of the other. The secret seed can't be output in any way.

The 2 cards generate each a part of the secret, which is mixed with the other. This is secure
because it is not possible to read the seed, and it provides a backup, as the 2 cards are
identical after a dual generation initialization. Still in this mode, there is no way to extract
the seed and put it in another blockchain wallet.

The common seed is ``SHA256(ECDH)``. Even the computer doing the transfer exchange can't compute
the seed, protected by ECDH. Similarly, the computer can't be part of the key exchange, as this
requires a signature shared with a secret key, only located within the cards pair.

Dual generation protocol:

.. code-block:: none

   card 1 : 80D00400         -> PublicKeySigned of the 1st card
   card 2 : 80D00400         -> PublicKeySigned of the 2nd card
   card 1 : 80D00500 PK2     -> PublicKeySigned of the 2nd card sent
   card 2 : 80D00500 PK1     -> PublicKeySigned of the 1st card sent

After this, the 2 cards have a common seed. One card is a backup of the other.

See the :ref:`cmd-load-key` command for more details.

External random entropy
^^^^^^^^^^^^^^^^^^^^^^^

The card can output random data. The query answer is only output data and is not used internally
by the card. It is the user's responsibility to compute a mnemonic using the ``GENERATE RANDOM``
command and then compute the corresponding seed, which can be uploaded in the card using the
``LOAD KEY`` command.

Recovery
--------

The JavaCard applet can load a binary seed (or eventually just an EC key pair). Once this seed
is loaded in the card, this card now behaves like the one it was backup.

Be aware that key derivation paths are not backed up and must be identical to retrieve the same
key pairs.

See the :ref:`cmd-load-key` command for more details about the recovery command.

Key source types
----------------

After loading or generating, the key source info byte indicates the origin:

.. list-table::
   :header-rows: 1
   :widths: 10 90

   * - Code
     - Description
   * - ``0x00``
     - No key (not seeded)
   * - ``'K'``
     - A single 256k1 EC pair was loaded
   * - ``'X'``
     - An extended 256k1 key was loaded (a BIP32 node)
   * - ``'L'``
     - An external seed was loaded
   * - ``'S'``
     - Internal seed generated
   * - ``'D'``
     - Seed generated using dual generation mode
