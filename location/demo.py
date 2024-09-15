from geopy.geocoders import Nominatim
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from geopy.distance import great_circle


geolocator = Nominatim(user_agent="my_unique_application_name")

def haversine(coord1, coord2):
    return great_circle(coord1, coord2).meters


def get_place_name(latitude, longitude):
    location = geolocator.reverse((latitude, longitude))
    if location:
        return location.address
    return 'Desconocido'

df = pd.read_csv('user_locations.csv')
# Ajustar el formato de fecha y hora
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')


df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.dayofweek
df = df[['user_id', 'latitude', 'longitude', 'hour', 'day_of_week']]


coords = df[['latitude', 'longitude']].values
scaler = StandardScaler()
coords_scaled = scaler.fit_transform(coords)

db = DBSCAN(eps=0.1, min_samples=5, metric='haversine').fit(coords_scaled)
df['cluster'] = db.labels_


habit_clusters = df['cluster'].value_counts()[df['cluster'].value_counts() > 10].index
habit_df = df[df['cluster'].isin(habit_clusters)]

print("Habit DataFrame:")
print(habit_df.head())


def most_frequent_location(user_data):
    return user_data.groupby(['latitude', 'longitude']).size().idxmax()


def generate_reminders(user_data):
    reminders = []
    for user_id, group in user_data.groupby('user_id'):
       
        most_frequent_loc = most_frequent_location(group)
        lat, lon = most_frequent_loc
        place_name = get_place_name(lat, lon)
    
        print(f"Usuario: {user_id}, Ubicación más frecuente: ({lat}, {lon}), Nombre del lugar: {place_name}")
        # Suponiendo que el usuario visita una ubicación específica entre 3 PM y 7 PM
        if (group['hour'].between(15, 19)).all() and (group['day_of_week'] < 5).all():
            reminders.append({
                'user_id': user_id,
                'place_name': place_name,
                'reminder': f"Recuerda llegar a {place_name} a las 15:00"
            })
    return reminders

reminders = generate_reminders(habit_df)
print("Recordatorios generados:")
for reminder in reminders:
    print(f"Usuario {reminder['user_id']}: {reminder['reminder']}")
