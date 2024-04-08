# mindfull_adrasan_bot
Bot for meditation group


## Alembic
To apply migrations:
```
alembic upgrade head
```

To create a new migration:
```
alembic revision -m "<message>"
```


## Heroku
To deploy to heroku:
```
git push heroku main
```


## Postgres
To connect to the postgres database:
```
psql -h mindfull-adrasan-bot.cehjzdx1uxcf.eu-central-1.rds.amazonaws.com -U postgres
```