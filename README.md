# 🧬 Biology Test Bot

> Biologiya fanidan inline, quiz va diagnostik testlarni yaratish, boshqarish va avtomatik tekshirish imkonini beruvchi Telegram bot platformasi.

---

## 📖 Description

Biology Test Bot — o‘qituvchilar va o‘quv markazlari uchun mo‘ljallangan qulay test tizimi bo‘lib, rasmli/rasmsiz testlar yaratish, ularni himoyalash va foydalanuvchilar natijalarini tahlil qilish imkonini beradi. Bot to‘liq admin panel orqali boshqariladi va foydalanuvchilar faoliyatini real vaqt davomida kuzatib boradi.

---

## 🧩 Features

- 🧪 **Rasmli va rasmsiz testlar yaratish** — har bir test ma’lum bir sarlavha ostida yaratiladi  
- 🔐 **Kontentni himoyalash** — testlar skrinshotdan yoki tarqatilishdan himoyalangan  
- 👥 **Foydalanuvchilar faoliyatini kuzatish** — kim qaysi testni qachon boshlagan yoki tugatganini ko‘rish  
- 📁 **Diagnostik va faylli testlar** — yirik testlarni to‘liq boshqarish imkoniyati  
- ✔️ **Avtomatik tekshiruv** — bot test natijalarini tekshiradi va toza formatda chiqaradi  
- 🛠️ **Admin panel boshqaruvi** — testlar, savollar, foydalanuvchilar va statistikani boshqarish

---
<img width="500" alt="image" src="https://github.com/user-attachments/assets/92444519-c5d9-4759-bae7-d811db77f7b2" />
<img width="500" alt="image" src="https://github.com/user-attachments/assets/31fbf776-c822-4d18-a35a-e787354c92a6" />
<img width="500" alt="image" src="https://github.com/user-attachments/assets/23cec9f3-0c29-4b73-b81e-c680a5a5f6cb" />
<img width="500" alt="image" src="https://github.com/user-attachments/assets/130e5bbc-5da7-4f4d-b015-47a68f067e30" />
<img width="500" alt="image" src="https://github.com/user-attachments/assets/febf9c54-f250-49eb-9767-901d678c9005" />
<img width="500" alt="image" src="https://github.com/user-attachments/assets/b7bfdd1a-2427-4bc9-8aea-598f4dd48518" />
<img width="500" alt="image" src="https://github.com/user-attachments/assets/81c7fc8f-a0bf-4e8e-b611-41f1d2d2b698" />
<img width="500" alt="image" src="https://github.com/user-attachments/assets/4ab34cc9-3279-4b81-933d-b684d95f23e6" />
<img width="500" alt="image" src="https://github.com/user-attachments/assets/03343e15-718a-4d6c-943b-cfb7396334cd" />
<img width="500" alt="image" src="https://github.com/user-attachments/assets/af137b14-57e6-4ad9-b12b-3512d41a9671" />
<img width="500" alt="image" src="https://github.com/user-attachments/assets/ee3990cd-292a-4420-b762-5ac12df52355" />
<img width="500" alt="image" src="https://github.com/user-attachments/assets/003b1619-6281-4f81-b9b8-0d624bf2d277" />
<img width="500" alt="image" src="https://github.com/user-attachments/assets/bc3a4f7a-5ebf-47f4-b526-6561f4acbc41" />
<img width="500" alt="image" src="https://github.com/user-attachments/assets/dcfc3fd0-0bb7-4235-b9a9-9790df6eb1f8" />
<img width="500" alt="image" src="https://github.com/user-attachments/assets/c5e82e11-3e36-4a91-a769-4d2186dd10ac" />
<img width="500" alt="image" src="https://github.com/user-attachments/assets/3cca887f-867e-4d72-8dcc-ca9b95921ee5" />


## 📦 Tech Stack

- **Python 3.x**  
- **Django 4.2.20**  
- **aiogram 3.20.0**  
- **PostgreSQL**  
- **Redis**  
- **django-ckeditor 6.7.2**  
- **django-jazzmin 3.0.0**  
- **django-ordered-model 3.7.4**  
- **phonenumbers 8.13.7**  
- **whitenoise 6.9.0**  
- **uvicorn 0.20.0**  
- **shortuuid 1.0.13**

---

## ⚙️ Installation

1. **Repository’ni klonlang:**
   ```bash
   git clone https://github.com/shamshod8052/biology_test_bot.git
   cd biology_test_bot
   ```
2. Virtual muhit yaratish va ishga tushirish:
```bash
  python -m venv venv
  source venv/bin/activate  # Linux/macOS
  venv\Scripts\activate     # Windows
```
3. Kerakli kutubxonalarni o‘rnating:
```bash
  pip install -r requirements.txt
```
4. .env.example faylini .env fayliga ko'chiring va kerakli ma'lumotlarni to'ldiring.
5. Migratsiyalarni bajarish:
```bash
  python manage.py makemigrations
  python manage.py migrate
```
6. Django serverni ishga tushiring:
```bash
python manage.py runserver
```
7. Botni ishga tushiring:
```bash
python manage.py runbot
```
🧑‍💻 Author

Shamshod Ramazonov
Python Backend Developer
