import rsa
publicKey, privateKey = rsa.newkeys(512)
pvk = privateKey
puk = publicKey
abs = rsa.key.AbstractKey
print(abs)
print(privateKey)
print(publicKey)
n1 = pvk.n
print(type(n1))
e1 = pvk.e
d = pvk.d
p = pvk.p
q = pvk.q
n2 = puk.n
e2 = puk.e
retpubk = rsa.key.PublicKey(n2, e2)
print(retpubk)
retprivk = rsa.key.PrivateKey(n2, e2, d, p, q)
print(retprivk)
print(type(privateKey))
print(type(publicKey))
print(type('bruh'))
def decrypt(apppass):
    decodemessage= rsa.decrypt(apppass, retprivk).decode()
    return decodemessage

def encrypt(apppass):
    encodemessage = rsa.encrypt(apppass.encode(), retpubk)
    return encodemessage
#b'\xa3.r\x1e\xd8o\xc5\xf3T\x1b\xf7\xae3\x18\xdf\xc8U\xff\xf3\xd1w\x81\x08\xf5\xb1\x17x\xa7\x153B\x13m\x84UC\xef\xcb\x08e\xe7\xe3\xbb\x8d\xcb\x91\xb3\xd8`@\xcc\xec\xff\xfai\x13$Q\xb5\xf6\xef\xd5\xd4\xd8'

text = 'test'
print(text)
encryptext=encrypt(text)
print(encryptext)
decryptext = decrypt(encryptext)
print(decryptext)


#decrypt(b'\xad!\x99\xe1\xca\x81\xd7\xdd\xd9\xc6\xf0\x91\xe6\x93\xa8I\x0c\x86wi\xb9\xaef\xd6<\xbc\xae\xb7\xf9T\xcf\xc9uL\x9f{\xf08C\xad\x86\xc8J\x95\xf8\xb7r\xc4\xf9\xab\x9c\x13\xd9\xd5\x0f\x89\x13\xe9\x06+\xd1\xc1\xd5\xca'
#)


'''l = ('testapp2', 'testuser', 'b\'(\\x1e\\xca\\xf2\\x15\\x91\\xde\\xeb\\xc80 \\x11\\xd9\\x7fp\\\\\\xcd.\\xcd\\xd3\\xd2\\xb3$\\x8a\\xed\\x87\\x95q\\\\N\\xaa\\xfet\\xe3D%\\xa0X\\r\\xa2\\x19\\xae\\xfajZ<\\xeb\\xf2\\xff"\\xaeR\\xb6\\xc4,\\xf9\\xa7\\xeb?\\xb6^R\\xc5}\'')


l = list(l)

prestripval = list(l[-1])

print(prestripval)

prestripval.pop(0)
prestripval.pop(0)
prestripval.pop(-1)

print(prestripval)

prefinalval = ''.join(prestripval)
finalval = prefinalval.encode()

print(finalval)

print(encrypt('test'))
print(decrypt(finalval))'''


pvk = '7605365950502004882873345891192953033003232300806068000639011742916403187376343439192547024527806187981579705632736341072013079839470358070749555360705871'
counter = 0
pvkl = list(pvk)

for i in pvkl:
    counter = counter + 1
print(counter)