# 🚀 Blyss - E-commerce Platform

![Django](https://img.shields.io/badge/Django-5.0.9-green.svg)
![MySQL](https://img.shields.io/badge/Database-MySQL-blue.svg)
![AJAX](https://img.shields.io/badge/AJAX-Enabled-orange.svg)
![E-commerce](https://img.shields.io/badge/E--commerce-Platform-red.svg)

## 📌 Description
**Blyss** is a structured and feature-rich **E-commerce platform** built using **Django 5.0.9** and **MySQL**. The platform includes a fully functional shopping cart, user account management, product customization, advanced search, and an **admin panel** for inventory management, analytics, and marketing.

## 🎯 Features
✅ **Customizable Banners & Product Carousels**.<br>
✅ **Product Listings & Category Management**.<br>
✅ **Advanced Search & Filtering**.<br>
✅ **Real-time Notifications**.<br>
✅ **Shopping Cart & Order History**.<br>
✅ **Favorite Products & Wishlist**.<br>
✅ **User Directory & Account Management**.<br>
✅ **Admin Panel for Inventory & User Management**.<br>
✅ **Reports & Analytics**.<br>
✅ **Marketing & Promotions Management**.<br>
✅ **AJAX Integration for Dynamic UI**.<br>

## 🏗️ Project Structure
```
Blyss/               # Main Django App
EcommerceProject/    # Django Project Settings and Configuration
static/             # Static Files (CSS, JavaScript, Images)
templates/          # HTML Templates for Frontend
```

## ⚙️ Database Configuration
The database settings are located in:
```
EcommerceProject/settings.py
```
Modify the following section if needed:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'Blyss',  # Database name
        'USER': 'root',  # Database user
        'PASSWORD': '',  # Database password
        'HOST': 'localhost',  # Host address
        'PORT': '3306',  # Default MySQL port
        'OPTIONS': {
            'charset': 'utf8mb4',  # Charset to support special characters & emojis
        },
    }
}
```

## 🔑 Admin Panel
To access the **Admin Panel**, go to:
```
http://127.0.0.1:8000/admin/
```

## 🛠️ How to Clone and Run
1. **Clone the repository**
   ```sh
   git clone https://github.com/JJuan777/Blyss.git
   cd Blyss
   ```
2. **Create a Virtual Environment** (Recommended)
   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```
3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Configure Database & Migrate**
   - Ensure MySQL is running and create a database named `Blyss`.
   - Run database migrations:
     ```sh
     python manage.py migrate
     ```
5. **Create a Superuser for Admin Panel**
   ```sh
   python manage.py createsuperuser
   ```
6. **Start the Django Development Server**
   ```sh
   python manage.py runserver
   ```
7. **Open the Application in Browser**
   ```
   http://127.0.0.1:8000/Blyss/
   ```

## 📧 Contact
For any questions or suggestions, you can contact me via **[GitHub](https://github.com/JJuan777)**.

---
**© 2025 - Blyss E-commerce** 🚀
