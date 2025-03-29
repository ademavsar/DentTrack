# DentTrack Deployment Guide

Bu belge, DentTrack uygulamasını üretim ortamında güvenli ve güvenilir bir şekilde dağıtmak için gerekli adımları ve en iyi uygulamaları içerir.

## İçindekiler

- [DentTrack Deployment Guide](#denttrack-deployment-guide)
  - [İçindekiler](#i̇çindekiler)
  - [Sistem Gereksinimleri](#sistem-gereksinimleri)
  - [Kurulum Adımları](#kurulum-adımları)
  - [Veritabanı Kurulumu](#veritabanı-kurulumu)
    - [1. Flask Migrations ile (Önerilen)](#1-flask-migrations-ile-önerilen)
    - [2. Setup Script ile](#2-setup-script-ile)
    - [Veritabanı Doğrulama](#veritabanı-doğrulama)
    - [Veritabanı Yolu Standardizasyonu](#veritabanı-yolu-standardizasyonu)
  - [Admin Kullanıcısı Oluşturma](#admin-kullanıcısı-oluşturma)
  - [Ortam Değişkenleri](#ortam-değişkenleri)
  - [Veritabanı Yedekleme](#veritabanı-yedekleme)
    - [SQLite için:](#sqlite-için)
    - [PostgreSQL için:](#postgresql-için)
  - [Uygulama Başlatma](#uygulama-başlatma)
  - [Sorun Giderme](#sorun-giderme)
    - [Veritabanı Sorunları](#veritabanı-sorunları)
    - [Bağlantı Sorunları](#bağlantı-sorunları)
  - [Güvenlik Önlemleri](#güvenlik-önlemleri)
  - [Dağıtım Kontrol Listesi](#dağıtım-kontrol-listesi)

## Sistem Gereksinimleri

- Python 3.11.8 veya daha yenisi (3.13.x'ten kaçının)
- Pip 22.0.0 veya daha yenisi
- SQLite (varsayılan) veya PostgreSQL/MySQL
- 1GB RAM (minimum)
- 2GB boş disk alanı

## Kurulum Adımları

1. **Kaynak Kodunu Alın**

```bash
git clone https://github.com/yourusername/DentTrack.git
cd DentTrack
```

2. **Sanal Ortam Oluşturun**

```bash
python -m venv venv

# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

3. **Bağımlılıkları Yükleyin**

```bash
pip install -r requirements.txt
```

4. **Ortam Değişkenlerini Yapılandırın**

```bash
# .env.example dosyasını kopyalayın
cp .env.example .env

# Dosyayı düzenleyin ve üretim için uygun değerleri ayarlayın
nano .env
```

## Veritabanı Kurulumu

DentTrack, üretim ortamında çalışırken veritabanının önceden kurulmuş olmasını bekler. Veritabanını kurmak için iki yöntem vardır:

### 1. Flask Migrations ile (Önerilen)

Bu yöntem, veritabanı şemasını adım adım oluşturur ve gelecekteki güncellemelere uyumludur:

```bash
flask db upgrade
```

### 2. Setup Script ile

Alternatif olarak, tüm tabloları doğrudan oluşturan kurulum betiğini kullanabilirsiniz:

```bash
python setup_db.py
```

Varsayılan verilerle başlamak için:

```bash
python setup_db.py --seed
```

### Veritabanı Doğrulama

Veritabanı kurulumunu doğrulamak için:

```bash
python db_check.py
```

Bu komut, veritabanı bağlantısını test eder ve tüm gerekli tabloların mevcut olduğunu doğrular.

### Veritabanı Yolu Standardizasyonu

**ÖNEMLİ:** DentTrack, veritabanı dosya yolu için standart bir format kullanır: `instance/denttrack.db`. Eski sürümlerde kullanılan `instance/dent_track.db` formatı artık desteklenmemektedir. Eğer eski formatta bir veritabanı dosyanız varsa, aşağıdaki komutla standart formata geçiş yapabilirsiniz:

```bash
python db_migrate_path.py
```

Bu komut:
1. Mevcut veritabanı dosyalarını tespit eder
2. Gerekirse dosyaları standart konuma kopyalar
3. .env dosyasındaki DATABASE_URL değişkenini günceller
4. Sorunsuz geçiş için adım adım rehberlik sunar

## Admin Kullanıcısı Oluşturma

Veritabanı kurulumundan sonra, sisteme giriş yapabilmek için bir admin kullanıcısı oluşturmanız **GEREKLİDİR**. Bu adım atlanırsa sisteme giriş yapılamaz ve admin paneline erişilemez.

Admin kullanıcısı oluşturmak için:

```bash
python create_admin.py
```

Bu komut, interaktif olarak sizden kullanıcı adı, e-posta ve şifre bilgilerini isteyecektir. Bu bilgileri girdikten sonra admin kullanıcısı oluşturulacaktır.

Otomatik bir kurulum yapıyorsanız, parametrelerle de kullanabilirsiniz:

```bash
# Parametrelerle kullanım örneği (parametreleri kendi değerlerinizle değiştirin)
python create_admin.py --username admin --email admin@example.com --password guvenli_sifre
```

**ÖNEMLİ**: Admin kullanıcısı oluşturulduktan sonra başarılı bir şekilde giriş yapabildiğinizden emin olun. Şifreyi güvenli bir yerde saklayın.

## Ortam Değişkenleri

Üretim ortamı için kritik ortam değişkenleri:

| Değişken | Açıklama | Önerilen Değer |
|----------|----------|----------------|
| FLASK_ENV | Uygulama ortamı | `production` |
| FLASK_DEBUG | Hata ayıklama modu | `0` |
| SECRET_KEY | Güvenlik anahtarı | Güçlü, rastgele bir değer (min. 24 karakter) |
| DATABASE_URL | Veritabanı bağlantı URL'si | SQLite: `sqlite:///instance/denttrack.db`<br>PostgreSQL: `postgresql://kullanici:sifre@localhost:5432/denttrack` |
| AUTO_CREATE_DB | Otomatik veritabanı oluşturma | `False` |
| ALLOW_EMPTY_DB | Boş veritabanına izin verme | `False` |
| SEED_DB | Örnek veri yükleme | `False` |
| STRICT_DB_CHECK | Eksik tablolar varsa uygulamayı başlatmama | `True` |

## Veritabanı Yedekleme

Veritabanınızı düzenli olarak yedekleyin:

### SQLite için:

```bash
# Yedekleme
cp instance/denttrack.db backups/denttrack_$(date +'%Y%m%d').db

# Geri yükleme
cp backups/denttrack_20250101.db instance/denttrack.db
```

### PostgreSQL için:

```bash
# Yedekleme
pg_dump -U username denttrack > backups/denttrack_$(date +'%Y%m%d').sql

# Geri yükleme
psql -U username denttrack < backups/denttrack_20250101.sql
```

## Uygulama Başlatma

Üretim ortamında uygulamayı başlatmak için:

```bash
# Doğrudan başlatma
python run.py

# Gunicorn ile başlatma (önerilen)
gunicorn --bind 0.0.0.0:5000 --workers 4 'app:create_app()'
```

## Sorun Giderme

### Veritabanı Sorunları

Eğer "no such table" hatası alırsanız:

1. Veritabanı tablolarının mevcut olduğunu doğrulayın:
   ```bash
   python db_check.py
   ```
   
2. Eksik tablolar varsa, göçleri çalıştırın:
   ```bash
   flask db upgrade
   ```

3. Göçler başarısız olursa, kurulum betiğini kullanın:
   ```bash
   python setup_db.py
   ```

### Bağlantı Sorunları

Eğer veritabanına bağlanılamazsa:

1. Veritabanı dosyasının/sunucusunun mevcut olduğunu kontrol edin
2. İzinleri kontrol edin (özellikle SQLite için dosya izinleri)
3. `.env` dosyasındaki `DATABASE_URL` değerini doğrulayın

## Güvenlik Önlemleri

1. **SECRET_KEY**: Her üretim ortamı için benzersiz, karmaşık bir değer kullanın.
2. **Güvenlik Duvarları**: Uygulamaya erişimi gerekli portlarla sınırlayın.
3. **HTTPS**: Üretim ortamında her zaman HTTPS kullanın (Nginx veya Apache ile yapılandırın).
4. **Düzenli Güncellemeler**: Bağımlılıkları güvenlik açıklarına karşı düzenli olarak güncelleyin:
   ```bash
   pip install --upgrade -r requirements.txt
   ```
5. **Yedeklemeler**: Düzenli yedeklemeler planlayın ve geri yükleme sürecini test edin.

## Dağıtım Kontrol Listesi

Uygulamayı üretim ortamına taşımadan önce:

- [ ] Tüm ortam değişkenleri uygun şekilde ayarlanmış
- [ ] Veritabanı yolu standardizasyonu tamamlanmış (`python db_migrate_path.py` ile kontrol edin)
- [ ] Veritabanı kurulumu tamamlanmış ve doğrulanmış
- [ ] Admin kullanıcısı oluşturulmuş (kritik: `python create_admin.py` ile)
- [ ] Uygulama, hata olmadan başlatılıyor
- [ ] Veritabanı yedekleme mekanizması yapılandırılmış
- [ ] Güvenlik duvarı ve HTTPS yapılandırılmış 