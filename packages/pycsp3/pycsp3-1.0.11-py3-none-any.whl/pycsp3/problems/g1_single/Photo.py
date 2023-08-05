from pycsp3 import *

"""
 Betty, Chris, Donald, Fred, Gary, Mary, and Paul want to align in one row for taking a photo.
 Some of them have preferences next to whom they want to stand:
  - Betty wants to stand next to Gary and Mary.
  - Chris wants to stand next to Betty and Gary.
  - Fred wants to stand next to Mary and Donald.
  - Paul wants to stand next to Fred and Donald.
"""

# friends[i] is the position (in a row) of the ith friend
betty, chris, donald, fred, gary, mary, paul = friends = VarArray(size=7, dom=range(7))

preferences = [(betty, gary), (betty, mary), (chris, betty), (chris, gary), (fred, mary), (fred, donald), (paul, fred), (paul, donald)]

# costs[i] is the cost of not respecting the ith preference
costs = VarArray(size=len(preferences), dom={0, 1})

table = {(i, j, 0 if abs(i - j) == 1 else 1) for i in range(7) for j in range(7) if i != j}

satisfy(
    # all friends are at a different position
    AllDifferent(friends),

    # determining which preferences are not satisfied
    [(p1, p2, costs[i]) in table for i, (p1, p2) in enumerate(preferences)]
)

minimize(
    # minimizing the overall dissatisfaction
    Sum(costs)
)
