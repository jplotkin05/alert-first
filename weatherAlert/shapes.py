import shapely.geometry

pOne = shapely.geometry.Point(-101.36,40.34)
pTwo = shapely.geometry.Point(-101.22,40.1)
pThree = shapely.geometry.Point(-101.25,39.86)
pFour = shapely.geometry.Point(-102.05,39.86)
pFive = shapely.geometry.Point(-102.2099999,40.3)
pSix = shapely.geometry.Point(-102.06,40.339999999999996)
pSeven = shapely.geometry.Point(-101.36,40.34)

pointUser = shapely.geometry.Point(-101.347056,  40.239980)
poly = shapely.geometry.Polygon(

    [
        pOne,pTwo,pThree,pFour,pFive,pSix,pSeven
    ]
)

print(pointUser.within(poly))
