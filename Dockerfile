FROM python:3.12

ENV APP_HOME /app

WORKDIR $APP_HOME

# Install Poetry
RUN pip install poetry

# Configure Poetry to not create virtual environments (not needed in Docker)
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

# Install dependencies first (better caching)
RUN poetry install --no-root --with dev

# Copy the rest of the application
COPY . .

# Install the project itself
RUN poetry install --no-root

EXPOSE 3000

WORKDIR $APP_HOME

CMD ["python", "main.py"]