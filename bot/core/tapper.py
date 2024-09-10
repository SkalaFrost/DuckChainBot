import asyncio
import json
import random
from time import time
from urllib.parse import unquote, quote

import aiohttp
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.functions import account
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
from .agents import generate_random_user_agent
from bot.config import settings
from typing import Any, Callable
import functools
from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers
from pyrogram.raw.types import InputBotAppShortName, InputNotifyPeer, InputPeerNotifySettings

def error_handler(func: Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in function '{func.__name__}': {e}")
            await asyncio.sleep(1)
    return wrapper

class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.user_id = 0
        self.username = None
        self.first_name = None
        self.last_name = None
        self.fullname = None
        self.start_param = None
        self.peer = None
        self.first_run = None

        self.session_ug_dict = self.load_user_agents() or []

        headers['User-Agent'] = self.check_user_agent()

    async def generate_random_user_agent(self):
        return generate_random_user_agent(device_type='android', browser_type='chrome')

    def info(self, message):
        from bot.utils import info
        info(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def debug(self, message):
        from bot.utils import debug
        debug(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def warning(self, message):
        from bot.utils import warning
        warning(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def error(self, message):
        from bot.utils import error
        error(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def critical(self, message):
        from bot.utils import critical
        critical(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def success(self, message):
        from bot.utils import success
        success(f"<light-yellow>{self.session_name}</light-yellow> | {message}")

    def save_user_agent(self):
        user_agents_file_name = "user_agents.json"

        if not any(session['session_name'] == self.session_name for session in self.session_ug_dict):
            user_agent_str = generate_random_user_agent()

            self.session_ug_dict.append({
                'session_name': self.session_name,
                'user_agent': user_agent_str})

            with open(user_agents_file_name, 'w') as user_agents:
                json.dump(self.session_ug_dict, user_agents, indent=4)

            logger.success(f"<light-yellow>{self.session_name}</light-yellow> | User agent saved successfully")

            return user_agent_str

    def load_user_agents(self):
        user_agents_file_name = "user_agents.json"

        try:
            with open(user_agents_file_name, 'r') as user_agents:
                session_data = json.load(user_agents)
                if isinstance(session_data, list):
                    return session_data

        except FileNotFoundError:
            logger.warning("User agents file not found, creating...")

        except json.JSONDecodeError:
            logger.warning("User agents file is empty or corrupted.")

        return []

    def check_user_agent(self):
        load = next(
            (session['user_agent'] for session in self.session_ug_dict if session['session_name'] == self.session_name),
            None)

        if load is None:
            return self.save_user_agent()

        return load

    async def get_tg_web_data(self, proxy: str | None) -> str:
        
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()

                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)
            
            while True:
                try:
                    peer = await self.tg_client.resolve_peer('DuckChain_bot')
                    break
                except FloodWait as fl:
                    fls = fl.value

                    logger.warning(f"{self.session_name} | FloodWait {fl}")
                    logger.info(f"{self.session_name} | Sleep {fls}s")
                    await asyncio.sleep(fls + 3)
            
            ref_id = settings.REF_ID if random.randint(0, 100) <= 85 and settings.REF_ID != '' else "Zv3mQp8X"
            
            web_view = await self.tg_client.invoke(RequestAppWebView(
                peer=peer,
                app=InputBotAppShortName(bot_id=peer, short_name="quack"),
                platform='android',
                write_allowed=True,
                start_param=ref_id
            ))

            auth_url = web_view.url
            tg_web_data = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])

            me = await self.tg_client.get_me()
            self.tg_client_id = me.id
            
            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error: {error}")
            await asyncio.sleep(delay=3)
        
        
    async def join_and_mute_tg_channel(self, link: str):
        link = link.replace('https://t.me/', "")
        if not self.tg_client.is_connected:
            try:
                await self.tg_client.connect()
            except Exception as error:
                logger.error(f"{self.session_name} | (Task) Connect failed: {error}")
        try:
            chat = await self.tg_client.get_chat(link)
            chat_username = chat.username if chat.username else link
            chat_id = chat.id
            try:
                await self.tg_client.get_chat_member(chat_username, "me")
            except Exception as error:
                if error.ID == 'USER_NOT_PARTICIPANT':
                    await asyncio.sleep(delay=3)
                    response = await self.tg_client.join_chat(link)
                    logger.info(f"{self.session_name} | Joined to channel: <y>{response.username}</y>")
                    
                    try:
                        peer = await self.tg_client.resolve_peer(chat_id)
                        await self.tg_client.invoke(account.UpdateNotifySettings(
                            peer=InputNotifyPeer(peer=peer),
                            settings=InputPeerNotifySettings(mute_until=2147483647)
                        ))
                        logger.info(f"{self.session_name} | Successfully muted chat <y>{chat_username}</y>")
                    except Exception as e:
                        logger.info(f"{self.session_name} | (Task) Failed to mute chat <y>{chat_username}</y>: {str(e)}")
                    
                    
                else:
                    logger.error(f"{self.session_name} | (Task) Error while checking TG group: <y>{chat_username}</y>")

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()
        except Exception as error:
            logger.error(f"{self.session_name} | (Task) Error while join tg channel: {error}")

    @error_handler
    async def make_request(self, http_client, method, endpoint=None, url=None, **kwargs):
        full_url = url or f"https://preapi.duckchain.io{endpoint or ''}"
        response = await http_client.request(method, full_url, **kwargs)
        response.raise_for_status()
        return await response.json()
    
    @error_handler
    async def userinfo(self, http_client):
       return await self.make_request(http_client, 'GET', endpoint="/user/info")
    
    @error_handler
    async def execute(self, http_client):
        return await self.make_request(http_client, 'GET', endpoint="/quack/execute")
    
    @error_handler
    async def get_tasks(self, http_client):
        return await self.make_request(http_client, 'GET', endpoint="/task/task_list")

    @error_handler
    async def do_task(self, http_client, path, taskId):
        return await self.make_request(http_client, 'GET', endpoint=f"/task/{path}", params = {"taskId" : taskId})
      
    @error_handler
    async def get_tasksinfo(self, http_client):
        return await self.make_request(http_client, 'GET', endpoint="/task/task_info")
    
    @error_handler
    async def check_in(self, http_client):
        return await self.make_request(http_client, 'GET', endpoint="/task/sign_in?")

    @error_handler
    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        response = await self.make_request(http_client, 'GET', url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
        ip = response.get('origin')
        logger.info(f"{self.session_name} | Proxy IP: {ip}")

    async def run(self, proxy: str | None) -> None:
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        http_client = CloudflareScraper(headers=headers, connector=proxy_conn)

        if proxy:
            await self.check_proxy(http_client=http_client, proxy=proxy)
        init_data = None
        init_data_live_time = random.randint(18000, 28800)
        init_data_created_time = 0
        while True:
            try: 
                if time() - init_data_created_time >= init_data_live_time or init_data is None:
                    init_data = await self.get_tg_web_data(proxy=proxy)
                    init_data_created_time = time()
                    http_client.headers['authorization'] = f'tma {init_data}'
                
                userinfo_res = await self.userinfo(http_client=http_client)
                if userinfo_res.get('code') == 200:
                    duck_name = userinfo_res.get('data', {}).get('duckName',None)
                    quackTimes = userinfo_res.get('data', {}).get('quackTimes',None)
                    decibels = userinfo_res.get('data', {}).get('decibels',None) 
                    self.info(f"Duck name: <green>{duck_name}</green> - Balance: <cyan>{decibels}</cyan> - Total Click: <cyan>{quackTimes}</cyan>")
                

                if settings.AUTO_TASK:
                    task_info_res = await self.get_tasksinfo(http_client=http_client)
                    done_task = []
                    twitterDaily = task_info_res.get("data",{}).get("twitterDaily","")
                    if task_info_res and (data := task_info_res.get("data", {})):
                        done_task = [task for tasks in data.values() if isinstance(tasks, list) for task in tasks]

                    task_res = await self.get_tasks(http_client=http_client)
      
                    paths = {"social_media": "follow_twitter", "daily": "twitter_interaction", "oneTime": "partner", "partner": "partner"}
                    if task_res and (tasks := task_res.get("data", {})):
                        for task_type, task_list in tasks.items():
                            for task in task_list:
                                if task['taskId'] in done_task:
                                    continue
                                
                                if task.get('action') and 't.me' in task.get('action'):
                                    await self.join_and_mute_tg_channel(task.get('action'))
                                    continue
                                
                                if task_type == "daily" and task["taskType"] == "daily_check_in":
                                    check_in_res = await self.check_in(http_client=http_client)
                                    if check_in_res.get("message") == "SUCCESS":
                                        self.success("Check in suceeded!")
                                        continue
                                elif task_type == "daily" and task["taskType"] == "twitter_interaction" and twitterDaily == "5":
                                    continue

                                path = paths.get(task_type, "")
                                if path:
                                    do_task_res = await self.do_task(http_client=http_client,path = path,taskId = task['taskId'])
                                    message = do_task_res.get("message")
                                    content = task.get('content')

                                    if message == "SUCCESS":
                                        self.success(f"Task <cyan>{content}</cyan> succeeded")
                                    elif message == "task was finished":
                                        self.info(f"Task <cyan>{content}</cyan> task was finished")
                                    else:
                                        self.info(f"Task <cyan>{content}</cyan> failed")
                                    await asyncio.sleep(random.randint(2,10))
                                else:
                                    self.info(f"Task <cyan>{content}</cyan> failed")
                            
                if settings.TAP: 
                    execute_res = await self.execute(http_client=http_client)
                    decibels = execute_res.get('data', {}).get('decibel')
                    quackTimes = execute_res.get('data', {}).get('quackTimes')
                    change = execute_res.get('data', {}).get('quackRecords')[-1]

                    if decibels and quackTimes:
                        self.info(f"Duck name: <green>{duck_name}</green> - Balance: <cyan>{decibels}</cyan>({'<red>' + change + '</red>' if int(change) < 0 else '<green>+' + change + '</green>'}) - Total Click: <cyan>{quackTimes}</cyan>")
                    else:
                        self.warning("Decibel or Quack Times not found in response.")
                else: 
                    sleep_time = random.randint(3600,4000)
                    self.info(f"Sleep <y>{sleep_time}s</y>")
                    await asyncio.sleep(delay=sleep_time)    

            except InvalidSession as error:
                raise error

            except Exception as error:
                self.error(f"Unknown error: {error}")
                await asyncio.sleep(delay=3)
                
            else:
                sleep_time = random.randint(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])
                self.info(f"Sleep <y>{sleep_time}s</y>")
                await asyncio.sleep(delay=sleep_time)    
            

async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
