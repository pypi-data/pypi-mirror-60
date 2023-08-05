#!/usr/local/bin/python

import asyncio
import aiohttp
import threading
from .websocket_event import Websocket_Event
import xml.etree.ElementTree as ET
import logging
import time
logger = logging.getLogger(__name__)

ws_headers = {
    "Sec-WebSocket-Protocol": "ISYSUB",
    "Origin" : "com.universal-devices.websockets.isy",
}


class Async_Session(object):

    def __init__(self,controller,address,port,username,password,https=False,loop=False, **kwargs):
        self._address = address
        self._port = port
        self.controller = controller
        self._https = https
        self.loop=loop
        self.auth = aiohttp.BasicAuth('admin','admin')
        
        # set some default values
        self.reply_timeout = kwargs.get('heartbeat') or 30
        self.sleep_time = kwargs.get('sleep_time') or 10

        self._connected = False
        self.session = None
        
    @property
    def connected(self):
        return self._connected

    @connected.setter
    def connected(self,connected):
        if self._connected != connected:
            self._connected = connected
            logger.warning ('Websocket Connected {}'.format(connected))
            if self.controller:
                self.controller.websocket_connected(connected)

    async def create_session(self):
        if self.session is not None and self.session.closed is False:
            await self.session.close()
        
        self.session = aiohttp.ClientSession(auth=self.auth,raise_for_status=True)

    async def request_async(self,path,timeout=10):
        if self.session is None:
            await self.create_session()

        logger.warning ('HTTP Get to {}'.format ('http://'+self._address+'/rest/'+path))

        try:
            async with self.session.get(
                    'http://'+self._address+'/rest/'+path,chunked=True,timeout=timeout) as response:
                #print(response.status)
                body = await response.text()
                #print(body)        
                return True,body

        except Exception as ex:
            self.connected = False
            logger.error('HTTP Get Error {}'.format(ex))
            return False

    def request (self,path,timeout):
        return asyncio.run_coroutine_threadsafe(self.request_async(path,timeout),self.loop)

    async def start_websocket(self,loop=None):
        await asyncio.gather(self.listen_forever(),loop=loop)

    async def listen_forever(self):
        URL = "ws://"+self._address+"/rest/subscribe"
        session = None

        while True:
            # outter loop restarted every time the connection fails
            logger.warning('Outter loop...')

            try:
                async with self.session.ws_connect(URL,headers=ws_headers,auth=self.auth,heartbeat=30) as ws:
                    logger.warning ('Waiting for messages. WS Closed {} {} Info  {}'.format(ws.closed,ws.exception(),ws.protocol))

                    async for msg in ws:
                        self.connected = True
                        #print('Message received from server:', msg)
                        logger.warning('Websocket Message: {}'.format(msg))
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            try:
                                event_node = ET.fromstring (msg.data)        
                                
                                if event_node.tag == 'Event':
                                    event = Websocket_Event(event_node)

                                    if event.valid:
                                        print (event)
                                        if self.controller:
                                            self.controller.websocket_event(event)
                            
                            except Exception as ex:
                                logger.error('Websocket Message Error {}'.format(ex))

                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            logger.warning ('Websocket Binary: {}'.format(msg.data))

                        elif msg.type == aiohttp.WSMsgType.PING:
                            ws.pong()

                        elif msg.type == aiohttp.WSMsgType.PONG:
                            logger.warning('Pong received')
                        
                        elif msg.type == aiohttp.WSMsgType.CLOSE:
                            logger.warning('Close received')
                            await ws.close()

                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logger.error ('Error during receive {}'.format(ws.exception()))

                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            logger.warning ('Close {}'.format(ws.exception()))
                            await ws.close()
                
                self.connected = False

                logger.warning('Aysnc loop completed. Session closed {}'.format(session.closed))
                await asyncio.sleep(self.sleep_time)
                logger.warning('Aysnc timeout finished. Session closed {}'.format(session.closed))

            except Exception as ex:
                self.connected = False
                logger.error('Websocket Error {}'.format(ex))
                await asyncio.sleep(self.sleep_time)
                continue

            await self.create_session()


