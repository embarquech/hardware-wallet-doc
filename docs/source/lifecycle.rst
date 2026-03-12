Lifecycle management
====================

Card startup
------------

After receiving the ATR from the card, one must select the applet to use it. The applet AID is
``0xA0000010000112``. This command provides some basic info about the card applet and status
flags.

.. seealso::

   :ref:`cmd-select` and :ref:`cmd-get-mnftr-cert` commands for full details on the startup
   sequence and response fields.

Initialization
--------------

Right after the installation, the applet is not initialized and the user needs to send some
parameters to use the card. The ``INIT`` command can only be executed on a fresh card; a reset is
required if the card was already initialized. Many base parameters changes require a card reset
(except PIN/PUK change).

The parameters are sent using "one shot encryption": the ``AES`` key is directly the ECDH of the
2 keys (card and computer). In addition to the personal code number, one needs to generate a
random common shared key for the card pairing, used later for a fully authenticated and secured
channel.

.. list-table:: Initialization parameters
   :header-rows: 1
   :widths: 30 20 50

   * - Parameter
     - Size
     - Description
   * - Owner Name
     - 1 + 20B max
     - Length byte + up to 20 characters
   * - Owner Email
     - 1 + 60B max
     - Length byte + up to 60 characters
   * - PIN
     - 9B
     - 4--9 digit number, padded with ``0x00`` to 9 bytes
   * - PUK
     - 12B
     - 12 digits/letters/bytes
   * - Pairing key
     - 32B
     - Secure Channel first pairing key

The PIN must be 4 to 9 figure number characters (``'0'``--``'9'``). If the PIN is less than 9
bytes, it must be filled with ``0x00`` until 9 characters long.

The parameters sent are encrypted and the command payload is:

.. code-block:: none

   PubKey | IV | EncryptedParams

.. seealso::

   :ref:`cmd-init` command for the full APDU specification.

Pairing
-------

After the initialization, the card and the host must share a common secret to be used as an
authenticated secure channel. This secret is required any time further to communicate with the
card (using a secure channel). The registration of the first common secret (pairing key) is done
during the init phase. There is 1 pairing key slot.

The user can use a common public pairing key and only use PIN for authentication. Otherwise, the
user host needs to store its pairing key in a safe place. In the case the client would communicate
with several cards, the user needs to associate the pairing key with the instance serial number
of the card.

.. note::

   If the user loses their pairing info, a stretched hash of the PUK (``SHA256`` applied 32
   times) can be used as the pairing key (slot ``0xFF``).

.. seealso::

   - :ref:`cmd-change-pairing-key` command for pairing key management
   - :doc:`secure_channel` for the full Secure Channel protocol description

Reset
-----

When the PUK code is sent into the ``RESET`` command, the card is reset. The reset PUK code is
chosen during the initialization stage. The PUK reset code is a 12 characters long string,
which allows a full reset of the card.

On top of this 12 characters secret, the reset is also secured by the user pairing key mechanism
(if secret). That means that resetting a card requires, on top of the PUK, to know the pairing
key to send the command encrypted. Still, the PUK can act as a pairing key on its own.

The reset command erases everything in the card, and makes the card as it was before the
initialization.

.. important::

   The PUK tries are unlimited, but there is an internal loop hash that takes time inside the
   card for each try. Every 12 tries, a power cycle is required to perform new tries.

.. seealso::

   - :ref:`cmd-reset` for the full APDU specification
   - :doc:`status_codes` for PUK retry behavior details
