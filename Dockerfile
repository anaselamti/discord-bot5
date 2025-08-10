# استخدم صورة بايثون خفيفة
FROM python:3.10-slim

# تحديد إصدار كروم وكروم درايفر المناسب (غير الرقم حسب الحاجة)
ENV CHROME_VERSION=114.0.5735.90

# تحديث النظام وتثبيت الأدوات اللازمة
RUN apt-get update && apt-get install -y \
    wget unzip xvfb libxi6 libgconf-2-4 libnss3 libxss1 libappindicator3-1 fonts-liberation \
    libatk-bridge2.0-0 libatk1.0-0 libgtk-3-0 libx11-xcb1 libxcb1 libxcomposite1 libxdamage1 libxrandr2 \
    libasound2 libpangocairo-1.0-0 libpango-1.0-0 libgbm1 libnspr4 libxshmfence1 libgl1-mesa-glx libgl1-mesa-dri \
    && rm -rf /var/lib/apt/lists/*

# تحميل وتثبيت Google Chrome for Testing
RUN wget https://storage.googleapis.com/chrome-for-testing-public/114.0.5735.90/linux64/chrome-linux64.zip \
    && unzip chrome-linux64.zip -d /usr/local/chrome-linux \
    && rm chrome-linux64.zip

# تحديث PATH ليشمل مجلد كروم
ENV PATH="/usr/local/chrome-linux:${PATH}"

# تحميل وتثبيت ChromeDriver المتوافق مع نفس الإصدار
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm chromedriver_linux64.zip \
    && chmod +x /usr/local/bin/chromedriver

# إنشاء مجلد العمل ونقل ملفات المشروع
WORKDIR /app
COPY . /app

# تثبيت متطلبات البايثون
RUN pip install --no-cache-dir -r requirements.txt

# تعريف متغير البيئة لمسار كروم لتستخدمه في الكود
ENV CHROME_BINARY="/usr/local/chrome-linux/chrome"

# أمر تشغيل البوت
CMD ["python", "main.py"]
