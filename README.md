# The Kirafiki Library 
This code is for creating a free crowd-sourced website for leanring the Swahili language. The website is built using the python-based Django framework. 

## GitHub Libraries Used 
1. [kamusi](https://github.com/Kalebu/kamusi) - To source words to be used on the website

## Prerequisites 
1. PostgreSQL Database - [postgreSQL Tutorial](https://www.w3schools.com/postgresql/)
2. This website uses the django framework, a helpful tutorial can be found here: [Django Tutorial](https://docs.djangoproject.com/en/6.1/intro/tutorial01/)
3. The translation tool on the website uses DeepL for translation. If you want to use the website with your own API key, one can be made for free here: [Deepl API](https://www.deepl.com/en/products/api)

## Running the website
Once the postgreSQL database is installed, follow the follow steps to start the website: 

1. If you are using a DeepL API key, create a '''.env''' file using the '''.env.template'''. The API should then be pasted into the 'API_KEY' variable. This '''.env''' file is ignored by github and will not be uploaded to the repository. 
2. Activate the virtual environment in '''.\kirafiki_django\Scripts\Activate.ps1'''.
3. The website itself is in a seperate file that can be accessed by '''cd .\django_folders\kirafiki_website''' in the command line. 
4. Once there, running '''python manage.py runserver''' should host the server locally if everything is set up correctly. If that doesn't work, some changes may need to be made to the '''settings.py''' file depending on your local database. 

