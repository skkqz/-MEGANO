FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production
WORKDIR /code
RUN mkdir requirements
COPY requirements/base.txt requirements/production.txt /code/requirements/
RUN pip install -r requirements/production.txt
COPY . /code/

RUN sed -i 's/\r$//g' /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh
ENTRYPOINT ["/code/entrypoint.sh"]