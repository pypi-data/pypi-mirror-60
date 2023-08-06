import sys
import hashlib

BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
sha = hashlib.sha256()

with open(sys.argv[1], 'rb') as f:
    while True:
        data = f.read(BUF_SIZE)
        if not data:
            break
        sha.update(data)

print("SHA256: {0}".format(sha.hexdigest()))
