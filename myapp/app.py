from dotenv import load_dotenv
load_dotenv()  # .env dosyasını yükler
from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
import os

app.config.from_object(Config)  # Config sınıfından ayarları yükler

# Veritabanı ve LoginManager
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Giriş yapılmamışsa yönlendirilecek sayfa

# Kullanıcı modeli
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Ders (Course) modeli
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Anasayfa
@app.route('/')
def index():
    return render_template('index.html')

# Kayıt Olma (Register)
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Aynı kullanıcı adı var mı?
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kayıtlı.', 'danger')
            return redirect(url_for('register'))

        # Yeni kullanıcı oluşturur
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Giriş Yapma (Login)
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Kullanıcı adı veya şifre hatalı.', 'danger')
    return render_template('login.html')

# Otomatik eklenmiş dersleri gösterir
@app.route('/dashboard')
@login_required
def dashboard():
    courses = Course.query.all()  # Tüm dersleri alıyoruz
    return render_template('dashboard.html', name=current_user.username, courses=courses)

# Çıkış (Logout)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yapıldı.', 'info')
    return redirect(url_for('index'))

# Sürükle-Bırak Dosya Yükleme
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        
        if 'file' not in request.files:
            flash('Dosya bulunamadı.', 'danger')
            return redirect(url_for('upload'))
        file = request.files['file']
        if file.filename == '':
            flash('Dosya seçilmedi.', 'danger')
            return redirect(url_for('upload'))

        # Uploads klasörüne kaydetme
        filepath = os.path.join('uploads', file.filename)
        file.save(filepath)
        flash(f'{file.filename} başarıyla yüklendi.', 'success')
        return redirect(url_for('upload'))

    return render_template('upload.html')

# Veritabanı oluşturma ve örnek dersleri ekleme 
def seed_courses():
    existing_courses = {course.title for course in Course.query.all()}
    
    courses = [
        {'title': 'Software Development', 'description': 'Helps you learn how to create, design, deploy, and support computer software'},
        {'title': 'Research Methods', 'description': 'It details the what, where and how of data collection and analysis'},
        {'title': 'Computer Interface', 'description': 'The different ways in which individuals interact with computational technologies, such as inputting data or manipulating software'}
    ]
    
    for course in courses:
        if course['title'] not in existing_courses:
            new_course = Course(title=course['title'], description=course['description'])
            db.session.add(new_course)
    
    db.session.commit()

# Uygulamayı başlat
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_courses()  # Dersleri veritabanına ekler
    app.run(debug=True)

