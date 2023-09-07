import asyncio
from vkbottle.api import ABCAPI, Token
from vkbottle.bot import Bot
from vkbottle.modules import logger
from vkbottle.callback import ABCCallback
from vkbottle.dispatch import ABCRouter, ABCStateDispenser
from vkbottle.exception_factory import ABCErrorHandler
from vkbottle.framework.labeler import ABCLabeler
from vkbottle.polling import ABCPolling
from vkbottle.tools import LoopWrapper


class MyLoopWrapper(LoopWrapper):
    pass
        


class MyBot(Bot):
    
    def __init__(self, 
                 token: Token | None = None,
                 api: ABCAPI | None = None,
                 polling: ABCPolling | None = None,
                 callback: ABCCallback | None = None,
                 loop: asyncio.AbstractEventLoop | None = None,
                 loop_wrapper: LoopWrapper | None = None,
                 router: ABCRouter | None = None,
                 labeler: ABCLabeler | None = None,
                 state_dispenser: ABCStateDispenser | None = None,
                 error_handler: ABCErrorHandler | None = None,
                 task_each_event: bool = True):
        super().__init__(token, api, polling, callback, loop,
                         loop_wrapper, router, labeler, state_dispenser,
                         error_handler, task_each_event)
        self.__running: bool = False
    
    def run_forever(self) -> NoReturn:  # type: ignore
        logger.info("Loop will be ran forever")
        self.loop_wrapper.add_task(self.run_polling())
        self.__running = True
        self.loop_wrapper.run_forever(self.loop)
    
    def stop(self):
        if self.__running:
            self.loop.close()
            self.__running = False
    
    @property
    def running(self):
        return self.__running
    
    
        
    
    
        
    