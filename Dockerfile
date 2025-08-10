FROM python:3.10-slim

# تحديث النظام وتثبيت الأدوات اللازمة
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    xvfb \
    xauth \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    fonts-liberation \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libgbm1 \
    libnspr4 \
    libxshmfence1 \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    && rm -rf /var/lib/apt/lists/*

# تحميل وتثبيت جوجل كروم (نسخة مستقرة متوافقة مع ChromeDriver)
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt install -y ./google-chrome-stable_current_amd64.deb
RUN rm google-chrome-stable_current_amd64.deb

# تحميل وتثبيت ChromeDriver المناسب للنسخة أعلاه (هنا استخدم النسخة 114 كمثال، عدّل حسب نسخة كروم)
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip -d /usr/local/bin/
RUN chmod +x /usr/local/bin/chromedriver
RUN rm chromedriver_linux64.zip

# إعداد مجلد العمل ونسخ الملفات
WORKDIR /app
COPY . /app

# تثبيت مكتبات بايثون
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل البوت داخل xvfb لتشغيل chrome بدون واجهة GUI
CMD ["xvfb-run", "-a", "python", "main.py"]
