Lifecycle Management
====================

Card Startup
------------

After receiving the ATR from the card, one must select the applet to use it. The applet AID is
``0xA0000010000112``. This command provides some basic info about the card applet and status
flags. See the :ref:`cmd-select` and :ref:`cmd-get-mnftr-cert` commands for more details.

Initialization
--------------

Right after the installation, the applet is not initialized and the user needs to send some
parameters to use the card. The ``INIT`` command can only be executed on a fresh card; a reset is
required if the card was already initialized. Many base parameters changes require a card reset
(except PIN/PUK change).

The parameters are sent using "one shot encryption": the AES key is directly the ECDH of the
2 keys (card and computer). In addition to the personal code number, one needs to generate a
random common shared key for the card pairing, used later for a fully authenticated and secured
channel.

The sent parameters are:

- **Owner Name** — LEN byte + up to 20 chars
- **Owner Email** — LEN byte + up to 60 chars
- **PIN** — 9 digits
- **PUK** — 12 digits/letters/bytes
- **Secure Channel first pairing key** — 32 bytes

The PIN must be 4 to 9 figure number characters (``'0'``-``'9'``). If the PIN is less than 9 bytes,
it must be filled with ``0x00`` character until 9 chars long.

The parameters sent are encrypted and the command payload is::

    PubKey | IV | EncryptedParams

See the :ref:`cmd-init` command for more details.

Pairing
-------

After the initialization, the card and the host must share a common secret to be used as an
authenticated secure channel. This secret is required any time further to communicate with the
card (using a secure channel). The registration of the first common secret (pairing key) is done
during the init phase. There is 1 Pairing Key slot.

The user can use a common public PairingKey and only use PIN for authentication. Else, the user
host needs to store its pairing key in a safe place. In the case the client would communicate with
several cards, the user needs to associate the PairingKey with the instance SN of the card.

In the case the user lost their pairing info, one can use a stretched hash of the PUK
(32 times SHA256) as the pairing key (coded by ``0xFF`` slot).

See the :ref:`cmd-change-pairing-key` command for further details.

Reset
-----

When the PUK code is sent into the ``RESET`` command, the card is reset. The reset PUK code is
chosen during the initialization stage. The PUK reset code is a 12 characters long string,
which allows a full reset of the card.

On top of this 12 chars secret, the reset is also secured by the user pairing key mechanism
(if secret). That means that resetting a card requires, on top of the PUK, to know the PairingKey
to send the command encrypted. Still, the PUK can act as a PairingKey on its own.

The reset command erases everything in the card, and makes the card as it was before the
initialization.

.. note::

   The PUK tries are unlimited, but there's an internal loop hash that takes time inside the
   card for each try. Every 12 tries, a power cycle is required to perform new tries.
