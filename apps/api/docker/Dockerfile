FROM python:3.14-slim

# جلوگیری از ساخت فایل‌های .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# نمایش مستقیم خروجی Python
ENV PYTHONUNBUFFERED=1

# مسیر کاری داخل container
WORKDIR /app

# انتقال requirements
COPY ../requirements.txt /app/requirements.txt

# نصب dependency ها
RUN pip install --no-cache-dir -r requirements.txt

# انتقال سورس پروژه
COPY ../ /app/

# اجرای Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]