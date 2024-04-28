from .bomb_screen import BombScreen, BombScreenEnum
from .config import Config
from .logger import logger_translated, LoggerEnum, logger
from .mouse import click_when_target_appears
from .utils import refresh_page


class Auth:
    is_authenticated = False

    @classmethod
    def login(cls, manager):
        cls.is_authenticated = BombScreen.get_current_screen() not in [
            BombScreenEnum.LOGIN.value,
            BombScreenEnum.NOT_FOUND.value,
            BombScreenEnum.POPUP_ERROR.value,
        ]
        if not cls.is_authenticated:
            logger_translated("login", LoggerEnum.ACTION)
            login_attempts = Config.PROPERTIES["screen"]["number_login_attempts"]
            for current_attempt in range(login_attempts):
                try:
                    logger(f"Login attempt {current_attempt + 1} of {login_attempts}")
                    if BombScreen.get_current_screen() != BombScreenEnum.LOGIN.value:
                        cls.logout()

                    logger_translated("Login", LoggerEnum.PAGE_FOUND)

                    logger_translated("connect wallet", LoggerEnum.BUTTON_CLICK)
                    if not click_when_target_appears("button_connect_wallet"):
                        cls.logout()
                        continue

                    preferred_network = Config.get("auth", "preferred_network")
                    logger_translated(
                        "select network",
                        LoggerEnum.BUTTON_CLICK,
                    )
                    if not click_when_target_appears(
                        f"button_select_network_{preferred_network}"
                    ):
                        cls.logout()
                        continue

                    logger_translated("play", LoggerEnum.BUTTON_CLICK)
                    if not click_when_target_appears(f"button_play"):
                        cls.logout()
                        continue

                    logger_translated("select metamask", LoggerEnum.BUTTON_CLICK)
                    if not click_when_target_appears(f"button_metamask"):
                        cls.logout()
                        continue

                    logger_translated("sign metamask", LoggerEnum.BUTTON_CLICK)
                    if not click_when_target_appears("button_sign"):
                        cls.logout()
                        continue

                    if BombScreen.wait_for_screen(BombScreenEnum.HOME.value):
                        logger("🎉 Logged in successfully!")
                        cls.is_authenticated = True
                        manager.set_refresh_timer("refresh_login")
                        break

                    raise Exception()
                except Exception as e:
                    if current_attempt == login_attempts - 1:
                        logger("It's not possible to login at the moment.")
                        raise e

                    logger(f"Failed to login. Retrying...")

    @classmethod
    def logout(cls):
        logger_translated("logout", LoggerEnum.ACTION)
        cls.is_authenticated = False
        refresh_page()
        BombScreen.wait_for_screen(BombScreenEnum.LOGIN.value)
