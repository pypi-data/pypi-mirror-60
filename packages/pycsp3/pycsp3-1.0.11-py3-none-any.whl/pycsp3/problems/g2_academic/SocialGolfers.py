from pycsp3 import *

# Problem 010 at CSPLib

nGroups, size, nWeeks = data.nGroups, data.groupSize, data.nWeeks
nPlayers = nGroups * size

if not variant():
    # g[w][p] is the group admitting on week w the player p
    g = VarArray(size=[nWeeks, nPlayers], dom=range(nGroups))

    satisfy(
        # ensuring that two players don't meet more than one time
        [(g[w1][p1] != g[w1][p2]) | (g[w2][p1] != g[w2][p2]) for w1 in range(nWeeks)
         for w2 in range(w1 + 1, nWeeks) for p1 in range(nPlayers) for p2 in range(p1 + 1, nPlayers)],

        # respecting the size of the groups
        [Cardinality(g[w], occurrences={i: size for i in range(nGroups)}) for w in range(nWeeks)],

        # tag(symmetry-breaking)
        [
            LexIncreasing(g, matrix=True),

            [g[0][p] == (p // size) for p in range(nPlayers)],

            [g[w][k] == k for k in range(size) for w in range(1, nWeeks)]
        ]
    )
elif variant("01"):
    # x[w][g][p] is 1 iff on week w the group g admits the player p
    x = VarArray(size=[nWeeks, nGroups, nPlayers], dom={0, 1})

    # tw[p1][p2][w] is 1 iff players p1 and p2 play together on week w
    tw = VarArray(size=[nPlayers, nPlayers, nWeeks], dom=lambda p1, p2, w: {0, 1} if p1 < p2 else None)

    # twg[p1][p2][w][g] is 1 iff players p1 and p2 play together on week w in group g
    twg = VarArray(size=[nPlayers, nPlayers, nWeeks, nGroups], dom=lambda p1, p2, w, g: {0, 1} if p1 < p2 else None)

    satisfy(
        # each week, each player plays exactly once
        [Sum([x[w][g][p] for g in range(nGroups)]) == 1 for w in range(nWeeks) for p in range(nPlayers)],

        # each week, each group contains exactly the right number of players
        [Sum(x[w][g]) == size for w in range(nWeeks) for g in range(nGroups)],

        # two players cannot meet twice
        [Sum(tw[p1][p2]) <= 1 for p1 in range(nPlayers) for p2 in range(p1 + 1, nPlayers)],

        # deciding when two players play together
        [Sum(twg[p1][p2][w]) == tw[p1][p2][w] for p1 in range(nPlayers) for p2 in range(p1 + 1, nPlayers) for w in range(nWeeks)],

        # deciding when two players play in the same group
        [x[w][g][p1] * x[w][g][p2] == twg[p1][p2][w][g] for w in range(nWeeks) for g in range(nGroups) for p1 in range(nPlayers) for p2 in
         range(p1 + 1, nPlayers)],

        # tag(symmetry-breaking)
        [
            # each week, groups are strictly ordered
            [LexDecreasing(x[w], strict=True) for w in range(nWeeks)],

            # weeks are strictly ordered (it suffices to consider the first group)
            LexDecreasing([x[w][0] for w in range(nWeeks)], strict=True),

            # golfers are strictly ordered
            LexDecreasing([[x[i][j][k] for i in range(nWeeks) for j in range(nGroups)] for k in range(nPlayers)], strict=True)
        ]

    )
