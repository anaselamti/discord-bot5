FROM python:3.10-slim

# تثبيت الأدوات اللازمة و كروم stable
RUN apt-get update && apt-get install -y \
    wget unzip xvfb libxi6 libgconf-2-4 libnss3 libxss1 libappindicator3-1 fonts-liberation \
    libatk-bridge2.0-0 libatk1.0-0 libgtk-3-0 libx11-xcb1 libxcb1 libxcomposite1 libxdamage1 libxrandr2 \
    libasound2 libpangocairo-1.0-0 libpango-1.0-0 libgbm1 libnspr4 libxshmfence1 libgl1-mesa-glx libgl1-mesa-dri \
    google-chrome-stable

# تثبيت chromedriver (تأكد من توافق النسخة مع كروم)
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

ENV PATH="/usr/local/bin:${PATH}"

CMD ["python", "main.py"]
