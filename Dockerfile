FROM python:3.7-stretch
WORKDIR /code
COPY . /code
RUN pip install -r requirements.txt
ENV PORT=5000
EXPOSE 5000
CMD gunicorn -b 0.0.0.0:$PORT app:app --pythonpath .
