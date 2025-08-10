FROM python:3.10-slim

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
    && rm -rf /var/lib/apt/lists/*

# تثبيت جوجل كروم النسخة 139 (Chrome for Testing)
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/139.0.7258.66/linux64/chrome-linux.zip
RUN unzip chrome-linux.zip -d /usr/local/
RUN rm chrome-linux.zip

# إضافة كروم إلى PATH
ENV PATH="/usr/local/chrome-linux:${PATH}"
ENV CHROME_BIN="/usr/local/chrome-linux/chrome"

# تثبيت ChromeDriver المتوافق مع Chrome 139
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/139.0.7258.66/linux64/chromedriver-linux64.zip
RUN unzip chromedriver-linux64.zip -d /usr/local/bin/
RUN chmod +x /usr/local/bin/chromedriver
RUN rm chromedriver-linux64.zip

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["xvfb-run", "-a", "python", "main.py"]
