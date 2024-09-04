[![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/airdropfactorycn)       [![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/DuckChain_bot/quack?startapp=Zv3mQp8X)

⚠️ **Warning: Using this tool may result in your account being banned. Please consider carefully before using!** ⚠️


#### Support our team by clicking on the referral link below. Your contribution helps us continue improving and developing our bot. Thank you!
[Click here](https://t.me/DuckChain_bot/quack?startapp=Zv3mQp8X)
## Recommendation before use

# 🔥🔥 PYTHON version must be 3.10 🔥🔥

## Features  
|                         Feature                          | Supported |
|:--------------------------------------------------------:|:---------:|
|                      Multithreading                      |     ✅     |
|                 Proxy binding to session                 |     ✅     |
|                      Auto Referral                       |     ✅     |
|                    Auto  Task                       |     ✅     |
|                     Auto Tap                        |     ✅     |
|              Support for pyrogram .session               |     ✅     |


## [Settings](https://github.com/SkalaFrost/DuckChainBot/blob/master/.env-example)
|        Settings         |                                      Description                                       |
|:-----------------------:|:--------------------------------------------------------------------------------------:|
|  **API_ID / API_HASH**  |        Platform data from which to run the Telegram session (default - android)        |
| **REF_ID**           |                   Your referral id after startapp= (Your telegram ID)                  |
| **TAP**      | Tap or not (default False)                                                |   
| **AUTO_TASK**      | Do task or not (default True)                                                |   
| **SLEEP_TIME**          |                   Delay before the next tap (e.g. [300, 600])                         |
| **USE_PROXY_FROM_FILE** |      Whether to use a proxy from the `bot/config/proxies.txt` file (True / False)      |

## Quick Start 📚

To fast install libraries and run bot - open run.bat on Windows or run.sh on Linux

## Prerequisites
Before you begin, make sure you have the following installed:
- [Python](https://www.python.org/downloads/) **version 3.10**

## Obtaining API Keys
1. Go to my.telegram.org and log in using your phone number.
2. Select "API development tools" and fill out the form to register a new application.
3. Record the API_ID and API_HASH provided after registering your application in the .env file.

## Installation
You can download the [**repository**](https://github.com/SkalaFrost/DuckChainBot) by cloning it to your system and installing the necessary dependencies:
```shell
git clone https://github.com/SkalaFrost/DuckChainBot.git
cd DuckChainBot
```

Then you can do automatic installation by typing:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux manual installation
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Here you must specify your API_ID and API_HASH, the rest is taken by default
python3 main.py
```

You can also use arguments for quick start, for example:
```shell
~/DuckChainBot >>> python3 main.py --action (1/2)
# Or
~/DuckChainBot >>> python3 main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```

# Windows manual installation
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Here you must specify your API_ID and API_HASH, the rest is taken by default
python main.py
```

You can also use arguments for quick start, for example:
```shell
~/DuckChainBot >>> python main.py --action (1/2)
# Or
~/DuckChainBot >>> python main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```