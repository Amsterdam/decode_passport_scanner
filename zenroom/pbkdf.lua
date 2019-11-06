-- Password-Based Key Derivation Function 2

-- symmetric encryption using pbkdf

rng = RNG.new()

-- user input
pin = str("1234") -- this is transformed into a 'secret' via PBKDF2

-- constants (can be hardcoded in host application)
salt = hex('c6e49670a3c65d7f19ee7d39a25478900f8e98ec1e9a82131e23e7b07d17c0c9') -- rng:octet(32)
kdf_iterations = 10000

ecdh = ECDH.new()

-- TODO: hash = HASH.new("sha512")
secret = ECDH.pbkdf2(ecdh, pin, salt, kdf_iterations, 32)

print(secret)

local cipher = { header = str("my header"),
 iv = rng:octet(16) }

cipher.text, cipher.checksum =
   ECDH.aead_encrypt(secret, str("my very private credentials"),
                     cipher.iv, cipher.header)

I.print(cipher)
output = map(cipher, hex)
print(JSON.encode(output))

------- receiver's stage
-- pin is again provided, kdf is ran so secret is there

local decode = { header = cipher.header }
decode.text, decode.checksum =
   ECDH.aead_decrypt(secret, cipher.text, cipher.iv, cipher.header)

-- this needs to be checked, can also be in the host application
-- if checksums are different then the data integrity is corrupted
-- assert(decode.checksum == cipher.checksum)

print(decode.header)
print(decode.text:str())