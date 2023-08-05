def bSearch(l, t):
    """ l must be sorted """
    s = 0
    e = len(l) - 1
    while s <= e:
        m = (s+e)//2
        if l[m] == t:
            return m
        elif l[m] > t:
            e = m-1
        else:
            s = s+1
    return -1
