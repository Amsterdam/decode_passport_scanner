-- print(VERSION)

external_key = read_json(KEYS)

curve = "ed25519"
internal_key = ECDH.keygen(curve)

payload = {}
payload['data'] = DATA

header = {}
-- user public key is added in order for server to check signature
header['pub_key'] = internal_key:public():base64()

-- payload is encrypted with server public key so only server can read it with own private key
-- header is signed? so server can check it with added public key? 
output = ECDH.encrypt(internal_key, base64(external_key.public), str(MSG.pack(payload)), str(MSG.pack(header)))
output = map(output, base64)
output.zenroom = VERSION
output.encoding = 'base64'
output.curve = curve

print(JSON.encode(output))