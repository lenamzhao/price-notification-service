class Property:

    # Initializer / Instance attributes
    def __init__(self, id: str, typeId: int, dynamicDisplayPrice: float, basePrice: float):
        self._id = id
        self._typeId = typeId
        self._dynamicDisplayPrice = dynamicDisplayPrice
        self._basePrice = basePrice

    @property
    def id(self):
        return self._id

    @property
    def typeId(self):
        return self._typeId

    @property
    def dynamicDisplayPrice(self):
        return self._dynamicDisplayPrice

    @property
    def basePrice(self):
        return self._basePrice

    def condition(self, typeId: int) -> bool:
        # Apartments
        if typeId == 1:
            return self._dynamicDisplayPrice < self._basePrice
        # Homes
        if typeId == 2:
            return self._dynamicDisplayPrice > self._basePrice

    def toTuple(self) -> list:
        result = (self._id, self._typeId, self._dynamicDisplayPrice, self._basePrice)
        return result;