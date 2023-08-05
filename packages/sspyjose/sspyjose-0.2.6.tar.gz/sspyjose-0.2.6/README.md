SingleSource PyJOSE Library
===========================

An (interim) JOSE library, featuring support for Ed25519, X25519,
ChaCha20/Poly1305 and AES256-GCM as required for PyKauriID.


Installation
------------

To install use pip:

    $ pip install sspyjose


Or clone the repo:

    $ git clone https://gitlab.com/kauriid/sspyjose.git
    $ python setup.py install

Set up and activate for Python 3:

    virtualenv ${HOME}/.virtualenvs/sspyjose \
               --system-site-packages --python=/usr/bin/python3
    source ${HOME}/.virtualenvs/sspyjose/bin/activate

Install required packages:

    pip install -e .

For installing the additional development, testing or documentation
dependencies, add a qualifier with one or more of these commands:

    pip install -e .[dev]       # Development dependencies
    pip install -e .[test]      # Testing dependencies
    pip install -e .[dev,test]  # All dependencies together


Usage
-----

### Signing to a JWS

    from sspyjose.jwk import Ed25519Jwk
    from sspyjose.jws import Ed25519Jws
    
    # Make a signing key object from a JWK as a JSON string.
    # The JWK must contain the private key seed.
    jwk = Ed25519Jwk(from_json=jwk_string)
    # If the JWK is already parsed to a Python dictionary, use this:
    # jwk = Ed25519Jwk(from_dict=jwk_dict)
    
    # Make a JWS signing object.
    signer = Ed25519Jws(jwk=jwk)
    
    # Assign the content to authenticate.
    signer.payload = {'answer': 42}
    
    # Sign it, and get the content in a compact serialisation format
    # (`jws` is a string).
    signer.sign()
    jws = jws.serialise()


### Verifying a JWS

    from sspyjose.jwk import Ed25519Jwk
    from sspyjose.jws import Ed25519Jws
    
    # Make a signing key object from a JWK as a JSON string.
    # The JWK only needs to contain the public key.
    jwk = Ed25519Jwk(from_json=jwk_string)
    # If the JWK is already parsed to a Python dictionary, use this:
    # jwk = Ed25519Jwk(from_dict=jwk_dict)
    
    # Make a JWS verifier object.
    verifier = Ed25519Jws(jwk=jwk)
    
    # Load the signed JWS as a compact form string.
    verifier.load_compact(jws)
    
    # Verify it, and get the payload.
    verifier.verify()
    print(verifier.payload)


Contributing
------------

TBD


Example
-------

TBD


## Licence

Copyright 2018 by SingleSource Limited, Auckland, New Zealand

This work is licensed under the Apache 2.0 open source licence.
Terms and conditions apply.
