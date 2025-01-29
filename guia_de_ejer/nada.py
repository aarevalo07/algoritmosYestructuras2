def t(arr):
    n = len(arr)
    if n>0:
        return arr[n-1] + t(arr[:n-1])
    else:
        return 0

print(t([1,2,3,4]))