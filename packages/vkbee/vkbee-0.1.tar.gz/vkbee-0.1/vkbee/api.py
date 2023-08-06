import aiohttp
import json
import requests
import time
import asyncio


class VkApi:
    def __init__(self, token, loop, api_version="5.103"):
        self.token = token
        self.api_version = api_version

        self.base_url = "https://api.vk.com/method/"
        self.s = aiohttp.ClientSession()

        self.last_request_time = 0
        self.start_time = time.time()
        self.request_count = 0

    async def call(self, method_name, data):
        data["access_token"] = self.token
        data["v"] = self.api_version

        url = self.base_url + method_name
        self.request_count += 1

        delay = time.time() - self.last_request_time
        # if delay < 0.05:
        #     print(f"SLEEP - {self.request_count}")
        #     await asyncio.sleep(1)
        
        self.last_request_time = time.time()
        r = await self.s.post(url, data=data)
        

        work_time = time.time() - self.start_time
        avr_time = work_time / self.request_count
        speed = self.request_count / work_time
        print(f"All - {self.request_count}")
        print(f"Work Time - {work_time}")
        print(f"Requests in Second - {speed}")
        print(f"Average Time - {avr_time}")
        return await r.json()

    def sync_call(self, method_name, data):
        data["access_token"] = self.token
        data["v"] = self.api_version

        url = self.base_url + method_name
        r = requests.post(url, data=data).json()
        return r
