from CBOR import CBOR

a = CBOR(12354)
a.dump()

b = CBOR('hello')
b.dump()

c = CBOR ([a,  b])
c.dump()

d = CBOR([c,  CBOR(-1)])
d.dump()
