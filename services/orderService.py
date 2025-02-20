def getShippingPrice(product):
    weight = product.price
    if (weight < 500):
        return 5.0
    elif (weight < 2000):
        return 10.0
    return 25.0