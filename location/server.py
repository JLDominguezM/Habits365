from flask import Flask, request, jsonify
from geopy.geocoders import Nominatim
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from geopy.distance import great_circle

app = Flask(__name__)
geolocator = Nominatim(user_agent="my_unique_application_name")

df = pd.read_csv('user_locations.csv')

df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')

df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.dayofweek
df = df[['user_id', 'latitude', 'longitude', 'hour', 'day_of_week']]

# Convertir coordenadas en una representación numérica
coords = df[['latitude', 'longitude']].values
scaler = StandardScaler()
coords_scaled = scaler.fit_transform(coords)

# Aplicar DBSCAN
db = DBSCAN(eps=0.1, min_samples=5, metric='haversine').fit(coords_scaled)
df['cluster'] = db.labels_

# Identificar hábitos
habit_clusters = df['cluster'].value_counts()[df['cluster'].value_counts() > 10].index
habit_df = df[df['cluster'].isin(habit_clusters)]

def get_place_name(latitude, longitude):
    location = geolocator.reverse((latitude, longitude))
    if location:
        return location.address
    return 'Desconocido'

@app.route('/get_place_name', methods=['GET'])
def get_place_name_endpoint():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    
    if latitude and longitude:
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            
            user_data = habit_df[(habit_df['latitude'] == latitude) & (habit_df['longitude'] == longitude)]
            if not user_data.empty:
                most_frequent_loc = most_frequent_location(user_data)
                place_name = get_place_name(most_frequent_loc[0], most_frequent_loc[1])
                return jsonify({'place_name': place_name})
            else:
                return jsonify({'place_name': 'Ubicación no encontrada en los datos'})
        except ValueError:
            return jsonify({'place_name': 'Error en los datos'})
    else:
        return jsonify({'place_name': 'Faltan parámetros'})

def most_frequent_location(user_data):
    return user_data.groupby(['latitude', 'longitude']).size().idxmax()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
