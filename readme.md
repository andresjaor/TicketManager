## Installation

Install python packages.
```sh
pip install - requirements.txt
```

## Settings

set the following setting data in `ticket_manager/settings.py`
```sh
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "tickets",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "5432",
    }
}

CELERY_BROKER_URL = ""

CLOUDINARY_NAME = ""
CLOUDINARY_API_KEY = ""
CLOUDINARY_API_SECRET = ""

```

## Run migrations

Create the Database `tickets` and run the command `python manage.py migrate`

## Run celery

` celery -A ticket_manager worker -l INFO`

## Run server

`python maange.py runserver


## Api manage

- Create a user

```commandline
curl --location 'http://localhost:8000/api/manage/user/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email": "test@email.co",
    "password": "TestPassowrd2024*"
}'
```
- Login with your `username` and `password` you will received  and `access` Token and `refresh` Token. Use `Bearer <access_token` as `Authorization` Header.
```commandline
curl --location 'http://localhost:8000/api/token/' \
--header 'Content-Type: application/json' \
--data '{
    "username": "test",
    "password": "TestPassowrd2024*"
}'
```
- Create a ticket
```commandline
curl --location 'http://localhost:8000/api/manage/ticket/' \
--header 'Content-Type: application/json' \
--header 'Authorization: ••••••' \
--data '{
    "name": "My Ticket Name",
    "num_of_images": 3
}'
```

- Query Tickets
```commandline
curl --location 'http://localhost:8000/api/manage/ticket?ticket_id=edf765b3-ea9f-4eb9-891c-691619f36ead' \
--header 'Authorization: ••••••'
```
Available filters: 
- `ticket_id` 
- `from_date` (isoformat)
- `to_date` (isoformat)
- `status` [CREATED, IN_PROGRESS, DONE]


- Upload an image
```commandline
curl --location --request PUT 'http://localhost:8000/api/manage/ticket/edf765b3-ea9f-4eb9-891c-691619f36ead/upload/' \
--header 'Content-Type: application/json' \
--header 'Authorization: ••••••' \
--data '{
    "b64_image": "<b64_image>",
    "image_name": "test.png"
}'
```




