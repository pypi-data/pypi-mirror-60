from phlasch.shortener.settings import SHORTENER_BASE


def convert_base(num):
    if num == 0:
        return SHORTENER_BASE[0]
    arr = []
    base = len(SHORTENER_BASE)
    while num:
        num, rem = divmod(num, base)
        arr.append(SHORTENER_BASE[rem])
    arr.reverse()
    return ''.join(arr)
