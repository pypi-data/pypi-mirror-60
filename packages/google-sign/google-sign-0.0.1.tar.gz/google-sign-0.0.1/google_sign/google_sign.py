r'''
https://github.com/ssut/py-googletrans/blob/master/googletrans/gtoken.py

tkk = '426151.3141811846'

playground\google-fanyi\crud-boy
sign_based_on_googletrans_acquirer.py

from googletrans.gtoken import TokenAcquirer
TOKENAC = TokenAcquirer()

def google_sign(text):
    return TOKENAC.do(text)
'''
import math

# tkk = '436443.3778881810'


def rshift(val, n):
    """python port for '>>>'(right shift with padding)
    """
    return (val % 0x100000000) >> n


def _xr(a, b):
    size_b = len(b)
    c = 0
    while c < size_b - 2:
        d = b[c + 2]
        d = ord(d[0]) - 87 if 'a' <= d else int(d)
        d = rshift(a, d) if '+' == b[c + 1] else a << d
        a = a + d & 4294967295 if '+' == b[c] else a ^ d

        c += 3
    return a


def google_sign(text, tkk='436443.3778881810'):
    a = []
    # Convert text to ints
    for i in text:
        val = ord(i)
        if val < 0x10000:
            a += [val]
        else:
            # Python doesn't natively use Unicode surrogates, so account for those
            a += [
                math.floor((val - 0x10000) / 0x400 + 0xD800),
                math.floor((val - 0x10000) % 0x400 + 0xDC00),
            ]

    b = tkk if tkk != '0' else ''
    d = b.split('.')
    b = int(d[0]) if len(d) > 1 else 0

    # assume e means char code array
    e = []
    g = 0
    size = len(text)
    while g < size:
        l = a[g]
        # just append if l is less than 128(ascii: DEL)
        if l < 128:
            e.append(l)
        # append calculated value if l is less than 2048
        else:
            if l < 2048:
                e.append(l >> 6 | 192)
            else:
                # append calculated value if l matches special condition
                if (l & 64512) == 55296 and g + 1 < size and a[g + 1] & 64512 == 56320:
                    g += 1
                    l = (
                        65536 + ((l & 1023) << 10) + (a[g] & 1023)
                    )  # This bracket is important
                    e.append(l >> 18 | 240)
                    e.append(l >> 12 & 63 | 128)
                else:
                    e.append(l >> 12 | 224)
                e.append(l >> 6 & 63 | 128)
            e.append(l & 63 | 128)
        g += 1
    a = b
    for i, value in enumerate(e):
        a += value
        a = _xr(a, '+-a^+6')
    a = _xr(a, '+-3^+b+-f')
    a ^= int(d[1]) if len(d) > 1 else 0
    if a < 0:  # pragma: nocover
        a = (a & 2147483647) + 2147483648
    a %= 1000000  # int(1E6)

    return '{}.{}'.format(a, a ^ b)


def test_sanity():
    ''' test sanity '''
    assert google_sign('test') == '476257.126138'
