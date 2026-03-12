Secure channel
==============

Opening a secure channel
-------------------------

In a standard use of the applet, just after selecting the applet, the client opens a secure
channel using their pairing key for this card.

Just after ``SELECT``, the user queries the card certificate and asks the card for its session
public key. The session key of the card is provided in a minimalist certificate, which holds a
salt provided by the user.

The user generates an EC key pair (``SessionUserPrivateKey`` / ``SessionUserPublicKey``) for the
session and provides the public key part when querying to open the secure channel.

The card responds with a session salt. All parameters of the secure channel are computed using:

.. code-block:: none

   ECDHXsecret = SessionCardPrivateKey . SessionUserPublicKey (x)   [Card side]
               = SessionUserPrivateKey . SessionCardPublicKey (x)   [Client side]

   SessionCardPublicKey  — received in the SELECT command card answer
   SessionUserPublicKey  — transmitted to the card in the OPEN SECURE CHANNEL command

   AESkey | MACkey = SHA512( ECDHXsecret | PairingKey | SessionSalt )

When ``P1=0xFF``, the pairing key used is ``SHA256^32(PUKcode)``. That way, the PUK can be used
as a pairing key, and a user losing their pairing key can still use the PUK to access the card.

.. seealso::

   :ref:`cmd-get-card-cert`, :ref:`cmd-open-sc`, and :ref:`cmd-mutually-auth` commands for
   full APDU specifications.

Mutual authentication
---------------------

Right after the secure channel is opened, the user shall test it using the ``MUTUALLY AUTHENTICATE``
command. A successful encryption-decryption full loop means the device and the client have the
same pairing key, authenticating each other.

If the authentication fails the card responds with ``0x6982``. In this case the
``OPEN SECURE CHANNEL`` command must be repeated to generate new keys.

.. seealso::

   :doc:`authentication` for PIN and user key authentication that occurs after the Secure
   Channel is established.

Encrypted APDUs
---------------

After a successful ``OPEN SECURE CHANNEL`` command, all communications between card and client
are encrypted.

.. note::

   Only the data fields of C-APDUs are encrypted. ``CLA``, ``INS``, ``P1``, ``P2`` for C-APDUs
   are plaintext. This means no sensitive data should be sent in these parameters. Additionally
   a MAC is calculated for the entire APDU, including the unencrypted fields.

Because R-APDUs can only contain data if their SW is a success or warning status word
(``0x9000``, ``0x62XX``, ``0x63XX``), when the secure channel is open all responses will have
SW ``0x9000``. The actual SW is always appended at the end of the response data before
encryption, which means the client must interpret the last two bytes of the plaintext
response as the SW.

An exception to this is SW ``0x6982``, which indicates that the Secure Channel has been
aborted and as such is returned without any MAC.

Encryption process
^^^^^^^^^^^^^^^^^^

To encrypt the data both the card and the client do the following:

1. The data is padded using the ``ISO/IEC 9797-1`` Method 2 algorithm.
2. The data is encrypted using ``AES`` in ``CBC`` mode using the session key.
3. An ``AES CBC-MAC`` is calculated over the entire APDU data.
4. The data field of the APDU is set to the MAC followed by the encrypted data.

Decryption process
^^^^^^^^^^^^^^^^^^

To decrypt the data both the card and the client do the following:

1. The first 16 bytes of the APDU data are the MAC to be verified.
2. The remaining data is decrypted using ``AES`` in ``CBC`` mode using the session key.
3. The padding is removed.

The IV used for the encryption is the last seen MAC from the counterpart. This optimizes the
number of transmitted bytes and guarantees protection from replay attacks. For the MAC
generation, a zero IV is always used.

MAC generation for C-APDUs
^^^^^^^^^^^^^^^^^^^^^^^^^^

Calculated on the concatenation of:

.. code-block:: none

   CLA INS P1 P2 LC1 LC2 LC3 00 00 00 00 00 00 00 00 00 | encrypted data field

The 9-byte long padding does not become part of the data field and does not affect ``LCx``.

- ``LCx`` = ``(Len 00 00)`` if len < 256 bytes
- ``LCx`` = ``(00 LenMSB LenLSB)`` if len >= 256 bytes (big endian short)

MAC generation for R-APDUs
^^^^^^^^^^^^^^^^^^^^^^^^^^

Calculated on the concatenation of:

.. code-block:: none

   LR1 LR2 LR3 00 00 00 00 00 00 00 00 00 00 00 00 00 | encrypted data field

The 13-byte long padding does not become part of the response field. ``LRx`` is the length of the
encrypted response data field and is not transmitted.

- ``LRx`` = ``(Len 00 00)`` if len < 256 bytes
- ``LRx`` = ``(00 LenMSB LenLSB)`` if len >= 256 bytes (big endian short)

Error conditions
^^^^^^^^^^^^^^^^

1. If a sensitive command is received without an active Secure Channel, the card shall respond
   with SW ``0x6985`` (``SW_CONDITIONS_NOT_SATISFIED``).
2. If a MAC cannot be verified the card shall respond ``0x6982`` and the Secure Channel must be
   closed.

.. warning::

   When sending very large data commands in the secure channel (much larger than expected), the
   reply can be illegible and cannot be decrypted. If the command is too large, the MAC-IV chain
   is broken, since the auth data for the received command data will not be properly read by the
   card, and any further message will use outdated MAC data.

.. seealso::

   :doc:`status_codes` for a complete reference of all status words, including Secure Channel
   specific error codes.
