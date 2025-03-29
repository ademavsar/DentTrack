# DentTrack - Diş Kliniği Yönetim Sistemi

DentTrack, Flask ile geliştirilmiş modüler mimari kullanan bir diş kliniği yönetim sistemidir. Hasta kayıtları, tedaviler ve ödemelerin takibini kolaylaştırır.

## Özellikler

- **Hasta Yönetimi**: Hasta kayıtları oluşturma, düzenleme ve silme
- **Tedavi Takibi**: Hastalar için tedavi kaydı, tedavi tipi ve fiyatlandırma
- **Ödeme İşlemleri**: Nakit, kredi kartı veya karışık ödeme seçenekleri
- **Finansal Raporlama**: Genel bakış, ödemeler ve borç durumu
- **Kullanıcı Yönetimi**: Rol tabanlı yetkilendirme (admin/kullanıcı)
- **Tema Desteği**: Açık/koyu tema desteği ve sistem tercihine göre otomatik değişim
- **Telefon Formatı**: Otomatik telefon numarası formatlaması (5XX-XXX-XX-XX)
- **WhatsApp Entegrasyonu**: Hastalara hızlı ödeme hatırlatması mesajları gönderme

## Son Güncellemeler

- **WhatsApp Hatırlatma Sistemi**: Ödenmemiş tedaviler için WhatsApp üzerinden özelleştirilebilir mesajlarla ödeme hatırlatmaları gönderme
- **Ödeme İşlemleri İyileştirmesi**: Ödenmemiş tedaviler sayfasında "Ödeme Ekle" butonu ile doğrudan ödeme alma özelliği
- **Arayüz İyileştirmeleri**: Tutarlı tablo yapısı ve kullanıcı dostu modaller
- **Hasta Görünümü**: Hasta detay sayfasında güncellenmiş tedavi listeleme ve ödeme alma mekanizması
- **Basitleştirilmiş Formlar**: Telefon numarası gibi alanlar için daha temiz ve kullanıcı dostu giriş formları

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

4. Ortam değişkenlerini ayarlayın:
```bash
# .env.example dosyasını .env olarak kopyalayın
cp .env.example .env
# Dosyayı açıp gerekli değişikliklerini yapın
# Windows için:
# copy .env.example .env
```

5. Veritabanını oluşturun:
```bash
flask db upgrade
```

6. İlk admin kullanıcısını oluşturun:
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

## Temel İş Akışları

1. **Hasta Yönetimi**:
   - Ana sayfadan "Hastalar" sekmesine gidin
   - "Yeni Hasta" butonu ile yeni hasta ekleyin veya mevcut hastaları düzenleyin

2. **Tedavi İşlemleri**:
   - Hasta detay sayfasından tedavi ekleyin
   - Tedavi için fiyat ve tarih belirleyin

3. **Ödeme Alma**:
   - Ödeme için iki yol vardır:
     - Hasta detay sayfasından
     - "Ödemeler" sekmesindeki ödenmemiş tedaviler listesinden "Ödeme Ekle" butonu ile

4. **WhatsApp Hatırlatmaları**:
   - "Ödemeler" sayfasında ödenmemiş tedaviler listesinde "Hatırlat" butonuna tıklayın
   - KVKK uyarısını onaylayın
   - Önceden hazırlanmış mesajı gerekirse düzenleyin
   - "Devam Et" butonuna tıklayarak WhatsApp'a yönlendirilin

## Ortam Değişkenleri

`.env` dosyasında aşağıdaki değişkenleri ayarlayabilirsiniz:

- `FLASK_ENV`: Uygulama ortamı (development, testing, production)
- `FLASK_DEBUG`: Hata ayıklama modunu açar/kapatır
- `SECRET_KEY`: Güvenlik anahtarı
- `DATABASE_URL`: Veritabanı bağlantı URL'si
- `AUTO_CREATE_DB`: Veritabanının otomatik oluşturulmasını sağlar
- `SEED_DB`: Başlangıç verilerinin yüklenmesini sağlar

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
│   │   ├── partials/       # Yeniden kullanılabilir şablon parçaları
│   └── static/             # Statik dosyalar (CSS, JS)
├── migrations/             # Veritabanı göçleri
├── instance/               # Örnek yapılandırma
├── create_admin.py         # Admin kullanıcısı oluşturma betiği
├── requirements.txt        # Bağımlılıklar
├── .env.example            # Örnek ortam değişkenleri dosyası
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
- KVKK uyumlu iletişim onayları

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. 