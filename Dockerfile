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

# تحميل وتثبيت Chrome for Testing (نسخة 139.0.7258.97)
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/139.0.7258.97/linux64/chrome-linux.zip
RUN unzip chrome-linux.zip -d /usr/local/
RUN rm chrome-linux.zip

# تحميل وتثبيت chromedriver المناسب (نسخة 139)
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/139.0.7258.97/linux64/chromedriver-linux64.zip
RUN unzip chromedriver-linux64.zip -d /usr/local/bin/
RUN chmod +x /usr/local/bin/chromedriver
RUN rm chromedriver-linux64.zip

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["xvfb-run", "-a", "python", "main.py"]
