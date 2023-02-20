# AWS-YouTube-Scrapper

Youtube Scrapper is used to scrap channel data and videos data.

## Features

- Scrap data from Youtube using Beautiful Soup
- Store data in MySql
- Used flask framework as backend

## Tech

- Python
- Flask
- Beautiful Soup
- Bootstrap 5
- Youtube Data Api
- MySql
- Flask SqlAlchemy
- AWS BeanStalk
- AWS Code Pipeline

## Requirements
- Python-3.8 or above 
- GCP access key with Youtube data api enabled

## Installation

```sh
git clone https://github.com/rahulGarg003/AWS-YouTube-Scrapper.git
```

Install the dependencies

```sh
pip install -r requirements.txt
```

Create a .env file in root folder of your project and provide below details
```sh
GCP_YOUTUBE_API_KEY='<>'
SQL_DB_ENGINE='mysql'
SQL_DB_HOSTNAME='<>'
SQL_DB_PORT='<>'
SQL_DB_USERNAME='<>'
SQL_DB_PASSWORD='<>'
SQL_DB_NAME='<>'
```

start flask server
go to root directory of project and  open terminal

```sh
python application.py
```


