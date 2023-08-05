from pycsp3 import *

# similar model (called ttp) proposed by Kathryn Francis for the 2012 Minizinc Competition

distances, prices = data.cityDistances, data.productPrices
nCities, nProducts = len(distances), len(prices)

# s[i] is the city succeeding to the ith city (itself if not part of the route)
s = VarArray(size=nCities, dom=range(nCities))

# d[i] is the distance (seen as a travel cost) between cities i and its successor
d = VarArray(size=nCities, dom=lambda i: {v for v in distances[i] if v >= 0})

# l[i] is the purchase location of the ith product (last city has nothing for sale)
l = VarArray(size=nProducts, dom=range(nCities - 1))

# c[i] is the purchase cost of the ith product
c = VarArray(size=nProducts, dom=lambda i: set(prices[i]))

if variant("elt"):
    satisfy(
        # linking distances to successors
        [distances[i][s[i]] == d[i] for i in range(nCities)],

        # linking purchase locations to purchase costs 
        [prices[i][l[i]] == c[i] for i in range(nProducts)],

        # purchasing a product at a city is only possible if you visit that city 
        [imply(s[i] == i, l[j] != i) for i in range(nCities) for j in range(nProducts)]
    )

satisfy(
    Circuit(s),

    # last city must be visited (we start here)
    s[nCities - 1] != nCities - 1
)

minimize(
    Sum(d + c)
)
