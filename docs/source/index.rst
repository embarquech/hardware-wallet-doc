Cryptnox Hardware Wallet — API Reference
============================================

**Doc revision 1.0** — for Cryptnox Hardware Wallet v1.6.1

Basic version with user auth by ECDSA 256r1, RSA2048 and FIDO auth.

This JavaCard Open Platform 3 applet provides basic HSM-like "cryptoki" capabilities for
managing crypto-currencies private key secure storage and signature for any blockchain using
SECP256k1 or SECP256r1 for ECDSA of the transactions. This applet acts like a hierarchical
key tree hardware wallet.

The main purposes are key generation, key derivation, authentication and signing.

Communication with the card happens through a simple APDU interface, together with a Secure
Channel guaranteeing confidentiality, authentication and integrity of all commands. Many parts
of the card comply with ISO/IEC 7816 (1/2/3/...) and Global Platform standards. T=1 mode used.

The secure channel is quite similar to GP SCP03. The applet uses Extended APDU to stick on T=1
single query, single answer.

The applet hosts a "Dual Basic Group Secret" EC secret key, which is a secret designed to be
shared within a pair of Basic wallet cards. This is loaded at factory with a one-shot encryption.
This secures the dual generation process.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   introduction
   technical_specifications
   lifecycle
   secure_channel
   authentication
   seed_management
   key_derivation
   signing
   commands_setup
   commands_crypto
   commands_data
   commands_user_keys
   status_codes
