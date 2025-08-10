FROM python:3.10-slim

RUN apt-get update && apt-get install -y wget unzip

# تثبيت جوجل كروم
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt install -y ./google-chrome-stable_current_amd64.deb
RUN rm google-chrome-stable_current_amd64.deb

# تثبيت chromedriver نسخة مطابقة مع كروم
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip -d /usr/local/bin/
RUN chmod +x /usr/local/bin/chromedriver
RUN rm chromedriver_linux64.zip

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
