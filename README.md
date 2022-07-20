# pontus

[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)

Telegram store bot. Based on the [CMS Moltin](https://www.elasticpath.com/). The bot will show a list of products, details of each product separately. From the selected products to form a shopping cart and place an order. Example: [store of fish](https://t.me/pontus_shopbot).

## Screenshots

![App Screenshot](https://dvmn.org/filer/canonical/1569215892/326/)

## Environment Variables

To run this project, you will need to add the following environment variables to your `.env` file

- `TELEGRAM_TOKEN` - token telegram bot. Get it from [@BotFather](https://telegram.me/BotFather).
- `TG_CHAT_ID` - Telegram id administrator for system alerts. You can find out by messaging a special bot in Telegram: [@userinfobot](https://t.me/userinfobot)

You'll need your [API keys](https://euwest.cm.elasticpath.com/) (Client ID and Client Secret) when making requests to the API.

- `MOLTIN_CLIENT_ID` - Client id of your store in cms moltin
- `MOLTIN_CLIENT_SECRET` - Client secret of your store in cms moltin

Register at [redis](https://redis.com/) for the database address, its port and password.

- `REDIS_HOST` - Redis database address Example: redis-13965.f18.us-east-4-9.wc1.cloud.redislabs.com
- `REDIS_PORT` - Redis database port
- `REDIS_PASSWORD` - Redis database password

## Run Locally

Clone the project

```bash
  git clone https://github.com/dad-siberian/pontus.git
```

Go to the project directory

```bash
  cd pontus
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  pytnon bot.py
```

## Deployment

To deploy this project run Heroku. [Manual](https://devcenter.heroku.com/articles/getting-started-with-python).

To set the config var on Heroku, execute the following:

```bash
heroku config:set TELEGRAM_TOKEN={telegram token}
```

## Project Objectives

The code is written for educational purposes on an online course for web developers [dvmn.org](https://dvmn.org/).
