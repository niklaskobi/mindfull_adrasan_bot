# mindfull_adrasan_bot
This application, named "Mindfull Adrasan Bot", is a dedicated tool designed to track and manage meditation times for individuals and groups. It serves as a personal meditation assistant, diligently recording each meditation session's duration and providing insightful statistics to users.

For group meditation sessions, the bot notifies all members about the cumulative meditation time for the day, fostering a sense of collective achievement and encouraging consistent practice. It also provides individual statistics to users, offering a detailed view of their personal meditation journey. This includes data such as total meditation time, average session duration, and frequency of sessions.

The application is built with a focus on simplicity and ease of use, making it accessible for both beginners and experienced meditators. It's a perfect tool for anyone looking to track their meditation progress and stay motivated in their mindfulness journey.


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