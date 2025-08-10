FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    wget unzip xvfb libxi6 libgconf-2-4 libnss3 libxss1 libappindicator3-1 fonts-liberation \
    libatk-bridge2.0-0 libatk1.0-0 libgtk-3-0 libx11-xcb1 libxcb1 libxcomposite1 libxdamage1 libxrandr2 \
    libasound2 libpangocairo-1.0-0 libpango-1.0-0 libgbm1 libnspr4 libxshmfence1 libgl1-mesa-glx libgl1-mesa-dri \
    curl gnupg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# تثبيت كروم stable عبر مستودع google الرسمي (أو يمكنك تحميل ملف deb)
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable

# تحميل chromedriver الإصدار 139 المتوافق مع كروم 139
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/139.0.7258.66/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip -d /usr/local/bin/ && \
    rm chromedriver-linux64.zip && \
    chmod +x /usr/local/bin/chromedriver

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

CMD ["python", "main.py"]
