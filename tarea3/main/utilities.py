from math import radians, cos, sin, asin, sqrt

#La funcion de harvesine para calcular la distancia entre dos coordenadas
#Devuelve true si la disntacia es menor a 15 metros
def haversine(lon1, lat1, lon2, lat2):
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    d = (c * r) * 1000  # in meters
    if (d <= 100):
        return True
    return False
