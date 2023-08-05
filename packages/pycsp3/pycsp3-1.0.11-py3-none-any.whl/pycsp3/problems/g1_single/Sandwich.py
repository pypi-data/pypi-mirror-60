from pycsp3 import *

persons = alice, bob, sascha = 0, 1, 2

# culprit is among alice (0), bob (1) and sascha (2)
culprit = Var(persons)

# likes[i][j] is 1 iff the ith guy likes the jth guy
likes = VarArray(size=[3, 3], dom={0, 1})

# taller[i][j] is 1 iff the ith guy is taller than the jth guy
taller = VarArray(size=[3, 3], dom={0, 1})

satisfy(
    # the culprit likes Alice
    likes[culprit][alice] == 1,

    # the culprit is taller than Alice
    taller[culprit][alice] == 1,

    # nobody is taller than himself
    [taller[i][i] == 0 for i in persons],

    # the ith guy is taller than the jth guy iff the jth guy is not taller than the ith guy
    [taller[i][j] != taller[j][i] for i in persons for j in persons if i != j],

    # Bob likes no one that Alice likes
    [imply(likes[alice][i], ~likes[bob][i]) for i in persons],

    # Alice likes everybody except Bob
    [likes[alice][i] == 1 for i in persons if i != bob],

    # Sascha likes everyone that Alice likes
    [imply(likes[alice][i], likes[sascha][i]) for i in persons],

    # nobody likes everyone
    [Count(likes[i], value=0) >= 1 for i in persons]
)
