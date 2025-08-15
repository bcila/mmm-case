# KPI Backend

Bu proje, Django Rest Framework ve Celery kullanarak finansal işlemlerin KPI (Key Performance Indicator) raporlarını üreten bir backend servisidir. PostgreSQL ve Redis ile Docker ortamında çalışır.

---

## 🚀 Kurulum

### Gereksinimler

- Docker  
- Docker Compose  
- Python 3.10+  
- Django 4  

### Projeyi klonlayın

```bash
git clone https://github.com/bcila/mmm-case.git
cd mmm-case
```

### Projeyi Docker ile başlatın

```bash
docker compose up --build
```

### Swagger Dokümantasyonu

[http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)

### Süper Kullanıcı Oluşturma

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

---

## 🔐 Kimlik Doğrulama

### ✅ Kayıt (Register)

```http
POST /auth/register/
```

#### Body (JSON)

```json
{
  "username": "burak",
  "email": "burak@example.com",
  "password": "burak5151",
  "password2": "burak5151"
}
```

#### Curl Örneği

```bash
curl -X POST http://127.0.0.1:8000/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "burak", "email": "burak@example.com", "password": "burak5151", "password2": "burak5151"}'
```

### 🔓 Giriş (Login)

```http
POST /auth/login/
```

#### Body (JSON)

```json
{
  "email": "burak@example.com",
  "password": "burak5151"
}
```

#### Response

```json
{
  "refresh": "<jwt_refresh_token>",
  "access": "<jwt_access_token>"
}
```

### ♻️ Token Yenileme (Refresh)

```http
POST /auth/refresh/
```

#### Body (JSON)

```json
{
  "refresh": "<jwt_refresh_token>"
}
```

#### Response

```json
{
  "access": "<new_access_token>"
}
```

---

## 📊 KPI Raporu

```http
GET /reports/summary/
```

### Header

```
Authorization: Bearer <access_token>
```

### Query Parameters (isteğe bağlı)

- `start_date=YYYY-MM-DD`
- `end_date=YYYY-MM-DD`
- `currency=TRY|USD|EUR`

#### Örnek Yanıt

```json
{
  "total_income": 420.64,
  "total_expense": 196.87,
  "net_cash_flow": 223.77,
  "top_expense_categories": [
    { "category": "Payroll", "total": 122.28 },
    { "category": "Rent", "total": 29.35 }
  ],
  "currency": "USD"
}
```

---

## 💸 Transactions API

### 📥 CSV ile Yükleme

```http
POST /transactions/upload/
```

#### Header

```
Authorization: Bearer <access_token>
Idempotency-Key: <unique_key>
```

#### Content-Type

```
multipart/form-data
```

#### Form-Data

```
file: transactions.csv
```

#### Örnek Curl

```bash
curl -X POST http://127.0.0.1:8000/transactions/upload/ \
  -H 'Authorization: Bearer <access_token>' \
  -H 'Idempotency-Key: test123' \
  -F 'file=@/path/to/transactions.csv'
```

---

### 📃 Listeleme (Filtreli)

```http
GET /transactions/
```

#### Header

```
Authorization: Bearer <access_token>
```

#### Query Parameters (isteğe bağlı)

- `start_date=YYYY-MM-DD`
- `end_date=YYYY-MM-DD`
- `transaction_type=credit|debit`
- `category=Rent, Utilities, vb.`

#### Yanıt Örneği

```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "date": "2025-07-01T00:00:00Z",
      "amount": "4500.00",
      "currency": "TRY",
      "transaction_type": "credit",
      "description": "Satış: Fatura #1023",
      "category": "Sales"
    }
  ]
}
```

---

## ⏱️ Celery Görevleri

- Haftalık KPI raporları `celery beat` ile otomatik çalıştırılır.

### Manuel Çalıştırma

```bash
docker compose exec web python manage.py shell
```

```python
from reports.tasks import generate_weekly_reports
generate_weekly_reports.delay()
```

---

## ⚠️ Notlar

- Proje, PostgreSQL ve Redis ile Docker ortamında çalışmaktadır.
- JWT ile kimlik doğrulama sağlanır (`djangorestframework-simplejwt`).
- Tarih filtrelerinde UTC/timezone ayarlarına dikkat edilmelidir.

---

##### 👤 **Burak Anıl Cila**
🔗 [LinkedIn](https://www.linkedin.com/in/burakanilcila)
