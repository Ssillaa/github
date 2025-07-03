from flask import Flask, render_template, jsonify
import random
from datetime import datetime

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')

# Dijital İkiz API rotası - JSON veri üretir
@app.route('/api/digital_twin')
def digital_twin():
    # occupant, araç içindeki kişinin kimliğini temsil eder
    occupant = random.choice(['Sıla', 'Bilinmiyor'])  # izinsiz giriş
    camera_status = random.choice(['OK', 'ERROR'])   # Kamera durumu simülasyonu
    # Üretilen dijital ikiz verileri
    data = {
        'vehicle': {
            'vehicle_id': 'V001',
            'speed': round(random.uniform(0, 120), 2), # Araç hızı
            'battery': round(random.uniform(0, 100), 2), # Pil durumu
            'engine_status': 'ON',
            'telemetry': {
                'rpm': random.randint(800, 2000), # Motor Devri
                'temperature': round(random.uniform(70, 120), 1) # Motor Sıcaklığı
            },
            'sensors': {
                'lidar_distance': round(random.uniform(0.5, 100.0), 2), # LIDAR Mesafesi (m)
                'camera_status': camera_status
            }
        },
        'environment': {
            'road_condition': random.choice(['Dry', 'Wet', 'Icy']), # Yol durumu
            'traffic': random.choice(['Light', 'Moderate', 'Heavy']), # Trafik durumu
            'weather': random.choice(['Sunny', 'Cloudy', 'Rainy', 'Snowy']) # Hava Durumu
        },
        'location': {
            'latitude': round(random.uniform(37.0, 38.0), 4),
            'longitude': round(random.uniform(-122.0, -121.0), 4)
        },
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),# Zaman damgası
        'occupant': occupant  # Araç içindeki kişi
    } # JSON formatında veri döndür
    return jsonify(data)
# Uygulamayı başlat
if __name__ == '__main__':
    app.run(debug=True)
