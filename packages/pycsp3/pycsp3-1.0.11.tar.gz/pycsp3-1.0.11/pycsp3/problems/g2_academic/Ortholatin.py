from pycsp3 import *

'''
A Latin square of order n is an n by n array filled with n different symbols (for example, values between 1 and n),
each occurring exactly once in each row and exactly once in each column.
Two latin squares of the same order n are orthogonal if each pair of elements in the same position occurs exactly once.
The most easy way to see this is by concatenating elements in the same position and verify that no pair appears twice.
There are orthogonal latin squares of any size except 1, 2, and 6.
'''

n = data.n

# x is the first Latin square
x = VarArray(size=[n, n], dom=range(n))

# y is the second Latin square
y = VarArray(size=[n, n], dom=range(n))

# z is the matrix used to control orthogonality
z = VarArray(size=[n * n], dom=range(n * n))

table = {(i, j, i * n + j) for i in range(n) for j in range(n)}

satisfy(
    # ensuring that x is a Latin square
    AllDifferent(x, matrix=True),

    # ensuring that y is a Latin square
    AllDifferent(y, matrix=True),

    # ensuring orthogonality of x and y through z
    AllDifferent(z),

    # computing z from x and y
    [(x[i][j], y[i][j], z[i * n + j]) in table for i in range(n) for j in range(n)],

    # tag(symmetry-breaking)
    [
        [x[0][j] == j for j in range(n)],
        [y[0][j] == j for j in range(n)]
    ]
)
