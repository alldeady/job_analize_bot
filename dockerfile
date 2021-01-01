FROM python:buster
RUN pip3 install pyTelegramBotAPI pandas SQLAlchemy matplotlib requests psycopg2
WORKDIR /bot
COPY ./ /bot
ENTRYPOINT ["python"]
CMD ["main.py"]
