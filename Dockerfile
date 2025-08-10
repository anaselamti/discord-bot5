FROM python:3.10-slim

# تثبيت الأدوات المطلوبة
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
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# إضافة مفتاح Google Chrome الرسمي ومستودع كروم
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# تحديث وتثبيت Google Chrome stable
RUN apt-get update && apt-get install -y google-chrome-stable

# تنزيل chromedriver المناسب لإصدار كروم المثبت (على سبيل المثال كروم 114 هنا، تحتاج تتأكد من إصدار كروم في بيئتك)
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm chromedriver_linux64.zip && \
    chmod +x /usr/local/bin/chromedriver

# مجلد العمل
WORKDIR /app

# نسخ المشروع
COPY . /app

# تثبيت مكتبات البايثون المطلوبة
RUN pip install --no-cache-dir -r requirements.txt

ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

CMD ["python", "main.py"]
