# استخدم صورة بايثون الأساسية
FROM python:3.10-slim

# تثبيت الحزم الأساسية المطلوبة لتشغيل كروم وسيلينيوم
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
    xauth \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# تحميل وتثبيت Chrome (Chrome for Testing) المناسب
ENV CHROME_VERSION=114.0.5735.90

RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chrome-linux.zip \
    && unzip chrome-linux.zip -d /usr/local/ \
    && rm chrome-linux.zip

# إضافة كروم إلى PATH
ENV PATH="/usr/local/chrome-linux:${PATH}"

# تحميل ChromeDriver بنفس نسخة كروم
RUN wget https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm chromedriver_linux64.zip \
    && chmod +x /usr/local/bin/chromedriver

# تحديد مسار chromedriver في متغير بيئة ليستخدم في الكود
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# تعيين مجلد العمل
WORKDIR /app

# نسخ ملفات البوت
COPY . /app

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# أمر تشغيل البوت
CMD ["python", "main.py"]
