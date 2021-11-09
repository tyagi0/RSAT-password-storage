
__all__ = ["bytestoint", "randbit", "prime_tester"]
import secrets
import logging
import typing
import os
import struct
from rsa.common import NotRelativePrimeError
from rsa.key import PublicKey, PrivateKey
from hmac import compare_digest
import math
from rsa.pkcs1 import _pad_for_encryption, DecryptionError
from rsa.parallel import getprime

exponent = 65537
log = logging.getLogger(__name__)

def pubformat(n, e):
    return PublicKey(n, e)


def privformat(n, e, d, p, q):
    return PrivateKey(n, e, d, p, q)


def ceildiv(num: int, div: int):
    quanta, mod = divmod(num, div)
    if mod:
        quanta += 1
    return quanta


def bytesize(number: int):
    if number == 0:
        return 1
    return ceildiv(bitsize(number), 8)


def inttobytes(number: int, fill_size: int = 0) -> bytes:
    if number < 0:
        raise ValueError("Number must be an unsigned integer: %d" % number)

    bytes_required = max(1, math.ceil(number.bit_length() / 8))

    if fill_size > 0:
        return number.to_bytes(fill_size, 'big')

    return number.to_bytes(bytes_required, 'big')


def bytestoint(raw_bytes: bytes) -> int:
    return int.from_bytes(raw_bytes, 'big', signed=False)


def randbit(n):
    output = secrets.randbits(n)
    return output


def prime_tester(number) -> bool:
    if number < 10:
        return number in {2, 3, 5, 7}

    if not (number & 1):
        return False

    k = get_rounds(number)
    return primality_test(number, k + 1)



def product(p, q):
    d = p*q
    return d


def phi(p, q):
    phi = (p-1)*(q-1)
    return phi


def gcd(p, q):
    while q != 0:
        (p, q) = (q, p % q)
    return p


def egcd(a, b):
    x = 0
    y = 1
    lx = 1
    ly = 0
    oa = a  
    ob = b  
    while b != 0:
        q = a // b
        (a, b) = (b, a % b)
        (x, lx) = ((lx - (q * x)), x)
        (y, ly) = ((ly - (q * y)), y)
    if lx < 0:
        lx += ob
    if ly < 0:
        ly += oa
    return a, lx, ly


def coprime(a: int, b: int) -> bool:
    d = gcd(a, b)
    return d == 1


def bitsize(num):
    try:
        return num.bit_length()
    except AttributeError:
        raise TypeError('this shit aint the right type')

def get_rounds(number):

    bitsizer = bitsize(number)
    if bitsizer >= 1536:
        return 3
    if bitsizer >= 1024:
        return 4
    if bitsizer >= 512:
        return 7
    return 10

def retrieve_random_bits(nbits) -> bytes:
    nbytes, rbits = divmod(nbits, 8)

    randomdata = os.urandom(nbytes)

    if rbits > 0:
        randomvalue = ord(os.urandom(1))
        randomvalue >>= (8 - rbits)
        randomdata = struct.pack("B", randomvalue) + randomdata

    return randomdata


def retrieve_random_int(nbits):
    randomdata = retrieve_random_bits(nbits)
    value = bytestoint(randomdata)
    value |= 1 << (nbits-1)
    return value


def retrieve_random_odd_int(nbits):

    value = retrieve_random_int(nbits)
    return value | 1


def randint(maxvalue):
    bit_size = bitsize(maxvalue)

    tries = 0
    while True:
        value = retrieve_random_int(bit_size)
        if value <= maxvalue:
            break
        if tries % 10 == 0 and tries:
            bit_size -= 1
        tries += 1
    return value

def get_prime(nbits:int)->int:
    assert nbits > 3

    while True:
        integer = retrieve_random_odd_int(nbits)

        if prime_tester(integer):
            return integer

def primality_test(num, k):
    if num < 2:
        return False

    d = num - 1
    r = 0

    while not (d & 1):
        r +=1
        d >>= 1

    for i in range(k):
        a = randint(num-3) + 1
        x = pow(a, d, num)
        if x == 1 or x == num - 1:
            continue
        for _ in range(r - 1):
            x = pow(a, 2, num)
            if x == 1:
                return False
            if x == num - 1:
                break
        else:
            return False
    return True




def inverse(x: int, n: int) -> int:

    (divider, inv, _) = egcd(x, n)

    if divider != 1:
        raise NotRelativePrimeError(x, n, divider)

    return inv


def calckeysCUSTOMEXPONENT(p, q, exponent: int = exponent):

    phil = phi(p, q)
    try:
        d = inverse(exponent, phil)
    except NotRelativePrimeError as ex:
        raise NotRelativePrimeError(exponent, phil, ex.d, msg="e (%d) and phi_n (%d) are not relatively prime (divider=%i)" %
                (exponent, phil, ex.d))
    if (exponent * d) % phil != 1:
        raise ValueError("e (%d) and d (%d) are not mult. inv. modulo "
                         "phi_n (%d)" % (exponent, d, phil))

    return exponent, d

def find_p_q(nbits: int,
             getprime_func: typing.Callable[[int], int] = get_prime,
             accurate: bool = True) -> typing.Tuple[int, int]:
    total_bits = nbits * 2

    # Make sure that p and q aren't too close or the factoring programs can
    # factor n.
    shift = nbits // 16
    pbits = nbits + shift
    qbits = nbits - shift

    # Choose the two initial primes
    log.debug('find_p_q(%i): Finding p', nbits)
    p = getprime_func(pbits)
    log.debug('find_p_q(%i): Finding q', nbits)
    q = getprime_func(qbits)
    def is_acceptable(p: int, q: int) -> bool:
        """Returns True iff p and q are acceptable:

            - p and q differ
            - (p * q) has the right nr of bits (when accurate=True)
        """

        if p == q:
            return False

        if not accurate:
            return True

        # Make sure we have just the right amount of bits
        found_size = bitsize(p * q)
        return total_bits == found_size

    # Keep choosing other primes until they match our requirements.
    change_p = False
    while not is_acceptable(p, q):
        # Change p on one iteration and q on the other
        if change_p:
            p = getprime_func(pbits)
        else:
            q = getprime_func(qbits)

        change_p = not change_p

    # We want p > q as described on
    # http://www.di-mgt.com.au/rsa_alg.html#crt
    return max(p, q), min(p, q)

def calckeys(p, q):
    return calckeysCUSTOMEXPONENT(p, q, exponent)


def genkeys(nbits: int,
             getprime_func: typing.Callable[[int], int],
             accurate: bool = True,
             exponent: int = exponent) -> typing.Tuple[int, int, int, int]:
    while True:
        (p, q) = find_p_q(nbits // 2, getprime_func, accurate)
        try:
            (e, d) = calckeysCUSTOMEXPONENT(p, q, exponent=exponent)
            break
        except ValueError:
            pass

    return p, q, e, d


def newkeys(nbits: int,
            accurate: bool = True,
            poolsize: int = 1,
            exponent: int = exponent) -> typing.Tuple[PublicKey, PrivateKey]:
    if nbits < 16:
        raise ValueError('Key too small')

    if poolsize < 1:
        raise ValueError('Pool size (%i) should be >= 1' % poolsize)

    # Determine which getprime function to use
    if poolsize > 1:
        from rsa import parallel

        def getprime_func(nbits: int) -> int:
            return parallel.getprime(nbits, poolsize=poolsize)
    else:
        getprime_func = getprime

    # Generate the key components
    (p, q, e, d) = genkeys(nbits, getprime_func, accurate=accurate, exponent=exponent)

    # Create the key objects
    n = p * q

    return (
        PublicKey(n, e),
        PrivateKey(n, e, d, p, q)
    )





def assert_int(var: int, name: str) -> None:
    if isinstance(var, int):
        return

    raise TypeError('%s should be an integer, not %s' % (name, var.__class__))


def encryptint(message: int, ekey: int, n: int) -> int:
    assert_int(message, 'message')
    assert_int(ekey, 'ekey')
    assert_int(n, 'n')

    if message < 0:
        raise ValueError('Only non-negative numbers are supported')

    if message > n:
        raise OverflowError("The message %i is too long for n=%i" % (message, n))

    return pow(message, ekey, n)


def encrypt(message: bytes, pub_key: PublicKey) -> bytes:
    keylength = bytesize(pub_key.n)
    padded = _pad_for_encryption(message, keylength)

    payload = bytestoint(padded)
    encrypted = encryptint(payload, pub_key.e, pub_key.n)
    block = inttobytes(encrypted, keylength)

    return block


def decrypt(crypto: bytes, priv_key: PrivateKey) -> bytes:
    blocksize = bytesize(priv_key.n)
    encrypted = bytestoint(crypto)
    decrypted = priv_key.blinded_decrypt(encrypted)
    cleartext = inttobytes(decrypted, blocksize)

    if len(crypto) > blocksize:
        # This is operating on public information, so doesn't need to be constant-time.
        raise DecryptionError('Decryption failed')

    cleartext_marker_bad = not compare_digest(cleartext[:2], b'\x00\x02')
    sep_idx = cleartext.find(b'\x00', 2)

    sep_idx_bad = sep_idx < 10

    anything_bad = cleartext_marker_bad | sep_idx_bad
    if anything_bad:
        raise DecryptionError('Decryption failed')

    return cleartext[sep_idx + 1:]