# telegramCarsBot
 Telegram-bot app which parses avito.ru/auto.ru

###Quick start for Debian 10:
apt-get update\
apt install python3\
apt install python3-pip python3-venv\
apt install postgresql postgresql-contrib\
apt install git\
apt install supervisor

cd /home/{home_dircetory}\
mkdir telegramApp\
cd telegramApp\
python3 -m venv env\
git clone https://github.com/KajimaSoys/telegramCarsBot.git

source env/bin/activate\
cd telegramCarsBot\
pip install -r requirements.txt

su -l postgres\
psql
CREATE DATABASE cars_bot;\
ALTER USER postgres PASSWORD '<new_pass_for_postgres>';\
\q

cd /home/{user}/telegramApp/telegramCarsBot\
pg_restore -d cars_bot cars_bot.sql\
psql -U postgres --password\

create extension pg_trgm;\
CREATE INDEX autoru_trgm_idx ON autoru USING GIN (search_string gin_trgm_ops);\
CREATE INDEX avito_trgm_idx ON avito USING GIN (search_string gin_trgm_ops);
CREATE TABLE words AS SELECT word\
FROM ts_stat('SELECT to_tsvector(''simple'', search_string) FROM autoru');\
CREATE INDEX words_idx ON words USING GIN (word gin_trgm_ops);

nano /etc/supervisor/conf.d/telegramApp.conf\
put in:\
[program:telegramApp]\
autorestart = False\
autostart = False\
startsecs = 0\
command = /home/{user}/telegramApp/env/bin/python /home/{user}/telegramApp/telegram>\
environment = PATH="/home/{user}/telegramApp/env/bin"\
directory= /home/{user}/telegramApp/telegramCarsBot/engine

systemctl restart supervisor
supervisorctl start telegramApp
