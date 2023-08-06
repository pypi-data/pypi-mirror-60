![vkbee](https://raw.githubusercontent.com/asyncvk/vkbee/master/bg.png)
# vkbee
Simple Async VKLibrary faster than vk_api
```python
import aiohttp
import asyncio
import longpoll
import api
import time



async def main(loop):
    token = "paste your token here"

    vk = api.VkApi(token, loop=loop)
    vk_poll = longpoll.BotLongpoll(vk, "group id paste here")

    start_time = time.time()
    event_count = 0
    async for event in vk_poll.events():
            
        data = {
            'random_id': 0,
            'peer_id': event['object']['message']['peer_id'],
            'message': 'Pre-alpha check longpoll'
        }
        

        if event['object']['message']['peer_id'] < 2000000000:
            if event['type'] == 'message_new':
                asyncio.create_task(game.enter(event))

            print('user')
            print(event['object']['message']['peer_id'])
            asyncio.create_task(vk.call('messages.send', data=data))
        else:
            print('chat')
        
        event_count += 1
        work_time = time.time() - start_time
        print(f'All Events - {event_count}')
        print(f'Work Time - {work_time}')
        avr_time = work_time / event_count
        speed = event_count / work_time
        print(f'Events in Second - {speed}')
        print(f'Average Time - {avr_time}')

loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))

```
