def list_of_lists(l, n):
    q = len(l) // n
    r = len(l) % n
    if r == 0:
        return [l[i * n:(i + 1) * n] for i in range(q)]
    else:
        return [l[i * n:(i + 1) * n] if i <= q else l[i * n:i * n + r] for i in range(q + 1)]
