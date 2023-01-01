FROM python:3.9

RUN apt-get update && apt-get install -y gettext 

WORKDIR /code
ENV DOCKER_ENV=true

# Install third party packages
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./ .

# Generate .mo files
RUN ./scripts/generate_locales.sh

CMD ["uvicorn", "--port", "80", "--host", "0.0.0.0", "app.main:app"]
