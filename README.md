# eCommerce website for a Gym using django

This project involves the creation of a website that provides the user with a wide range of classes to which they can attend. 

Steps to use this project:

1. Pull this repository
2. Create a virtualenv and install dependencies with `pip install -r requirements.txt`
3. Configure your .env variables
4. Run the website using `python manage.py runserver`


This project includes:

1. The Django Debug Toolbar already setup
2. Multiple settings modules setup for easily deploying
3. Python-decouple for securely referencing keys, passwords and other settings.
4. A custom Django command for renaming the project

This project is also available in docker hub: https://hub.docker.com/r/sc186/jymbud
The version available currently is jymbud:test
To download and run the doker image in linux:
- `sudo docker pull sc186/jymbud:test`
- `sudo docker run -i -t --network host sc186/jymbud:test`
- the website will be available at http://127.0.0.1:8000/


The original project is taken from: https://github.com/justdjango/django-ecommerce , whom I thank for his tutorials, videos and all the materials that made this project possible.


