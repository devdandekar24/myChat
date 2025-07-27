# 💬 My Chat App

A modern real-time chat application built with Django, ASGI, and HTMX — featuring user authentication, self-chat, email verification, and real-time messaging.

🌐 **Live Demo**: [https://mychat-fg9w.onrender.com](https://mychat-fg9w.onrender.com)

---

## 🚀 Features

- 🧠 **Real-Time Chat** with Django Channels & ASGI  
- 📧 **Email Verification** (via Gmail SMTP)  
- 💬 **Self-Chat Support** (like WhatsApp notes to self)  
- 📦 **Media File Handling** with Cloudinary  
- 🔐 **User Authentication** with Django AllAuth (no social logins)  
- 📄 **Static Files Served via WhiteNoise**  
- 🌐 **Deployed on Render**  
- 💅 **Tailwind CSS** for styling  
- 🧹 **Automatic File Cleanup** using `django-cleanup`  
- 🔁 **Redis-backed Channel Layers** for production  
- ⚡ Minimal HTMX Integration (dynamic interactivity)  

---

## 🛠️ Tech Stack

- **Backend**: Django, Django Channels, Daphne (ASGI server)  
- **Frontend**: HTML + Tailwind CSS + HTMX  
- **Real-Time**: WebSockets, Redis, Consumers  
- **Storage**: Cloudinary (media), WhiteNoise (static)  
- **Email**: Gmail SMTP  
- **Deployment**: Render  
- **Extras**: `django-environ`, `dj-database-url`, `django-cleanup`  

---

## 🌍 Deployment

This app is deployed on **Render** and uses:
- **PostgreSQL** as the production database  
- **Redis** for WebSocket channel layers  
- **Cloudinary** for media file hosting  
- **WhiteNoise** to serve static files  

---

## 📚 What I Learned

- Django ASGI structure and use of `consumers.py`, `routers.py`  
- Handling WebSocket connections with Channels  
- Working with HTMX for lightweight dynamic content  
- Email verification system using Django AllAuth  
- Using Cloudinary and Whitenoise in production  
- Deploying Django projects on Render with environment variables  

---

## 📬 Contact

For questions, ideas, or collaboration:
- GitHub: [@devdandekar24](https://github.com/devdandekar24)

---

> _Built with 💻 Django, ⚡ ASGI, and a lot of learning._
