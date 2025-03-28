# DentTrack - Diş Kliniği Yönetim Sistemi

DentTrack, Flask ile geliştirilmiş modüler mimari kullanan bir diş kliniği yönetim sistemidir. Hasta kayıtları, tedaviler ve ödemelerin takibini kolaylaştırır.

## Özellikler

- **Hasta Yönetimi**: Hasta kayıtları oluşturma, düzenleme ve silme
- **Tedavi Takibi**: Hastalar için tedavi kaydı, tedavi tipi ve fiyatlandırma
- **Ödeme İşlemleri**: Nakit, kredi kartı veya karışık ödeme seçenekleri
- **Finansal Raporlama**: Genel bakış, ödemeler ve borç durumu
- **Kullanıcı Yönetimi**: Rol tabanlı yetkilendirme (admin/kullanıcı)
- **Tema Desteği**: Açık/koyu tema desteği

## Kurulum

1. Repoyu klonlayın:
```bash
git clone https://github.com/yourusername/DentTrack.git
cd DentTrack
```

2. Sanal ortam oluşturun:
```bash
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. Veritabanını oluşturun:
```bash
flask db upgrade
```

5. İlk admin kullanıcısını oluşturun:
```bash
python create_admin.py admin
# Şifrenizi girin
```

## Uygulamayı Çalıştırma

Uygulamayı başlatın:
```bash
flask run
```

Uygulama `http://127.0.0.1:5000/` adresinde çalışacaktır.

## Ortam Modları

- **Development**: Hata ayıklama etkin, geliştirme veritabanı kullanır
- **Testing**: Testler için, test veritabanı kullanır
- **Production**: Üretim için optimize edilmiş, hata ayıklama devre dışı

## Proje Yapısı

```
DentTrack/
├── app/                    # Ana uygulama paketi
│   ├── admin/              # Admin paneli modülü
│   ├── auth/               # Kimlik doğrulama modülü
│   ├── core/               # Çekirdek modül (modeller, yardımcı işlevler)
│   ├── patients/           # Hasta modülü
│   ├── treatments/         # Tedavi modülü
│   ├── templates/          # HTML şablonları
│   └── static/             # Statik dosyalar (CSS, JS)
├── migrations/             # Veritabanı göçleri
├── instance/               # Örnek yapılandırma
├── create_admin.py         # Admin kullanıcısı oluşturma betiği
├── DEV_TASKS.md            # Geliştirme görevleri
├── requirements.txt        # Bağımlılıklar
├── README.md               # Bu dosya
└── run.py                  # Giriş noktası
```

## Kimlik Doğrulama

Sistem iki tür kullanıcı rolü destekler:
- **Admin**: Tam erişime sahiptir, kullanıcı yönetimini yapabilir
- **User**: Hasta ve tedavi işlemlerini yönetebilir

İlk kurulumda `create_admin.py` betiği ile bir admin kullanıcısı oluşturmanız gerekir.

## Güvenlik Özellikleri

- Rol tabanlı yetkilendirme
- Şifre hashleme
- CSRF koruması
- Oturum koruması

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. 