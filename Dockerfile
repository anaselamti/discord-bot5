FROM python:3.10-slim

# تثبيت الحزم اللازمة
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget unzip xvfb libxi6 libgconf-2-4 libnss3 libxss1 libappindicator3-1 \
    fonts-liberation libatk-bridge2.0-0 libatk1.0-0 libgtk-3-0 libx11-xcb1 libxcb1 \
    libxcomposite1 libxdamage1 libxrandr2 libasound2 libpangocairo-1.0-0 libpango-1.0-0 \
    libgbm1 libnspr4 libxshmfence1 libgl1-mesa-glx libgl1-mesa-dri \
    ca-certificates gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# إضافة مستودع جوجل وتثبيت كروم الرسمي
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
 && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
 && apt-get update \
 && apt-get install -y google-chrome-stable \
 && rm -rf /var/lib/apt/lists/*

# تحميل وتثبيت chromedriver 114
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
 && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
 && chmod +x /usr/local/bin/chromedriver \
 && rm chromedriver_linux64.zip

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["xvfb-run", "-a", "python", "main.py"]
