import requests

def send_request(latitude, longitude):
    # Construye la URL con los parámetros de latitud y longitud
    url = f'https://5f9b-131-178-54-1.ngrok-free.app/get_place_name?latitude={latitude}&longitude={longitude}'
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        
        return response.json()
    except requests.RequestException as e:
        
        print(f"Error al realizar la solicitud: {e}")
        return {'place_name': 'Error'}


try:
    latitude = float(input("Introduce la latitud (entre -90 y 90): "))
    longitude = float(input("Introduce la longitud (entre -180 y 180): "))

    
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise ValueError("Las coordenadas están fuera del rango válido.")
    
    
    response = send_request(latitude, longitude)
    
    
    place_name = response.get('place_name', 'Desconocido')
    print(f"Nombre del lugar: {place_name}")
except ValueError as e:
    print(f"Error en la entrada: {e}")
