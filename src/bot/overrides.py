import asyncio
from typing import Optional, NoReturn
from asyncio import get_event_loop, AbstractEventLoop
from vkbottle.api import ABCAPI, Token
from vkbottle.bot import Bot
from vkbottle.modules import logger
from vkbottle.callback import ABCCallback
from vkbottle.dispatch import ABCRouter, ABCStateDispenser
from vkbottle.exception_factory import ABCErrorHandler
from vkbottle.framework.labeler import ABCLabeler
from vkbottle.polling import ABCPolling
from vkbottle.tools.dev import LoopWrapper
from vkbottle.tools.dev.auto_reload import watch_to_reload


class MyLoopWrapper(LoopWrapper):
    
    def run_forever(self, running: bool, loop: Optional[AbstractEventLoop] = None) -> NoReturn:  # type: ignore
        """Runs startup tasks and makes the loop running forever"""

        if not self.tasks:
            logger.warning("You ran loop with 0 tasks. Is it ok?")

        loop = loop or get_event_loop()

        try:
            [loop.run_until_complete(startup_task) for startup_task in self.on_startup]

            if self.auto_reload:
                loop.create_task(watch_to_reload(self.auto_reload_dir))

            for task in self.tasks:
                loop.create_task(task)

            loop.run_forever()
        except KeyboardInterrupt:
            logger.info("Keyboard Interrupt")
        finally:
            [loop.run_until_complete(shutdown_task) for shutdown_task in self.on_shutdown]
            if loop.is_running():
                running = False    
                loop.close()


class MyBot(Bot):
    
    def __init__(self, 
                 token: Token | None = None,
                 api: ABCAPI | None = None,
                 polling: ABCPolling | None = None,
                 callback: ABCCallback | None = None,
                 loop: AbstractEventLoop | None = None,
                 loop_wrapper: MyLoopWrapper | None = MyLoopWrapper(),
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
        self.loop_wrapper.run_forever(self.running, self.loop)
    
    def stop(self):
        if self.__running and self.loop.is_running():
            self.loop.close()
            self.__running = False
    
    @property
    def running(self):
        return self.__running
    
    @running.setter
    def running(self, new_running: bool):
        self.__running = new_running
    