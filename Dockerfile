# استخدم صورة بايثون الرسمية
FROM python:3.10-slim

# تثبيت الأدوات والمكتبات المطلوبة لتشغيل كروم وselenium
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
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# تحميل وتثبيت Google Chrome 139 (Chrome for Testing)
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/139.0.7258.66/linux64/chrome-linux.zip \
    && unzip chrome-linux.zip -d /usr/local/ \
    && rm chrome-linux.zip

# إضافة كروم للمسار
ENV PATH="/usr/local/chrome-linux:${PATH}"

# تحميل وتثبيت ChromeDriver 139 المتوافق مع كروم 139
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/139.0.7258.66/linux64/chromedriver-linux64.zip \
    && unzip chromedriver-linux64.zip -d /usr/local/bin/ \
    && rm chromedriver-linux64.zip \
    && chmod +x /usr/local/bin/chromedriver

# إعداد مجلد العمل
WORKDIR /app

# نسخ ملفات المشروع (مثل كود البوت وrequirements.txt)
COPY . /app

# تثبيت مكتبات بايثون المطلوبة
RUN pip install --no-cache-dir -r requirements.txt

# تعيين متغير البيئة لمسار chromedriver في كود البوت
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# تشغيل البوت (يفضل أن يتم تشغيل البوت عبر CMD أو ENTRYPOINT في المشروع)
CMD ["python", "main.py"]
