FROM python:3.9

RUN mkdir -p /usr/src/bot/
WORKDIR /usr/src/bot/

COPY . /usr/src/bot/

RUN pip install aiogram
RUN pip install requests
RUN pip install datetime


ENV BOT_TOKEN "1850254766:AAEmUPm1vWU1J_we3gj7i8F0iBnEYkyw1Go"

CMD ["python", "bot.py"]