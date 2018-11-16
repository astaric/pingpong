Pongpong
========

Application for management of table tennis competition.

Installation
============

1. Create a new python2 environment
  ```
  conda create -n p python=2
  ```
2. Install python requirements
  ```
  pip install -r requirements.txt
  ```
3. Install npm & bower
  ```
  brew install npm
  npm install -g bower
  ```
4. Download javascript requirements
  ```
  bower install
  ```
5. Create db
  ```
  python manage.py syncdb
  python manage.py migrate
  ```
6. Run server
  ```
  python manage.py runserver
  ```
