from loguru import logger

def bkn(pSkey):
    t, n, o = 5381, 0, len(pSkey)
    while n < o:
        t += (t << 5) + ord(pSkey[n])
        n += 1
    return t & 2147483647

def ptqrToken(qrsig):
    n, i, e = len(qrsig), 0, 0
    while n > i:
        e += (e << 5) + ord(qrsig[i])
        i += 1
    return 2147483647 & e

def gtk_tf_skey(skey: str) -> int:
    """将skey转换为gtk"""
    hash = 5381
    for c in skey:
        hash += (hash << 5) + ord(c)
    return hash & 0x7fffffff