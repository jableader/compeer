from datetime import datetime, timedelta
import time
from base64 import b64encode, b64decode

_key = bytearray('ReallySuperSafeKey69', 'utf-8')
_key_len = len(_key)

def encrypt(b):
    return bytearray([(b[i] + _key[i % _key_len]) % 256 for i in range(len(b))])

def decrypt(b):
    return bytearray([(b[i] - _key[i % _key_len]) % 256 for i in range(len(b))])

def get_pair(lst):
    query = lst.items.extra(select={'random': 'RANDOM()'}).order_by('random')
    return tuple(query[:2])

def create_nonce(pair):
    unencrypted = '%d|%d|%.3f' % (pair[0].pk, pair[1].pk, time.time())
    encrypted = encrypt(bytearray(unencrypted, 'utf-8'))
    return b64encode(encrypted).decode('utf-8')


def check_nonce(nonce, pair):
    decrypted = decrypt(bytearray(b64decode(bytearray(nonce, 'utf-8')))).decode('utf-8')
    pk1, pk2, timestamp = decrypted.split('|')

    timestamp = datetime.fromtimestamp(float(timestamp))
    isold = (timestamp + timedelta(seconds=30)) < datetime.utcnow()

    expected, actual = [int(pk1), int(pk2)], [item.pk for item in pair]
    pksMatch = (expected == actual) or (reversed(expected) == actual)
    return pksMatch and not isold
