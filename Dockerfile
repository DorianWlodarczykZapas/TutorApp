FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . /app/

CMD ["python", "TutorApp/manage.py", "runserver", "0.0.0.0:8000"]