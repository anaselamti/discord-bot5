# استخدم صورة Python الأساسية
FROM python:3.10-slim

# تثبيت الأدوات الأساسية ومكتبات كروم
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    xvfb \
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
    gnupg2 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# إضافة مفتاح GPG الرسمي لجوجل
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -

# إضافة مستودع كروم الرسمي
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# تحديث المصادر وتثبيت كروم stable
RUN apt-get update && apt-get install -y google-chrome-stable

# تحميل chromedriver المناسب لنسخة كروم (يفضل التأكد من التوافق)
ENV CHROME_DRIVER_VERSION=114.0.5735.90
RUN wget -O /tmp/chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver_linux64.zip \
    && chmod +x /usr/local/bin/chromedriver

# إعداد المسار للكروم
ENV PATH="/usr/local/bin/chrome-linux:${PATH}"

# تعيين مجلد العمل
WORKDIR /app

# نسخ ملفات البوت إلى الحاوية
COPY . /app

# تثبيت بايثون الحزم المطلوبة
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل البوت
CMD ["python", "main.py"]
