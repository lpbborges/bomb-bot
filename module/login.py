from .config import Config
from .enum import ScreenEnum
from .logger import LoggerEnum, logger, logger_translated
from .mouse import *
from .utils import *
from .screen import Screen


NETWORKS = {
    0: "Binance",
    1: "Polygon",
}


class Login:
    def do_login(manager, network=0):
        current_screen = Screen.get_current_screen()
        logged = False

        if (
            current_screen != ScreenEnum.LOGIN.value
            and current_screen != ScreenEnum.NOT_FOUND.value
            and current_screen != ScreenEnum.POPUP_ERROR.value
        ):
            logged = True

        if not logged:
            logger_translated("login", LoggerEnum.ACTION)

            login_attempts = Config.PROPERTIES["screen"]["number_login_attempts"]

            for _ in range(login_attempts):

                if Screen.get_current_screen() != ScreenEnum.LOGIN.value:
                    refresh_page()
                    Screen.wait_for_screen(ScreenEnum.LOGIN.value)

                logger_translated("Login", LoggerEnum.PAGE_FOUND)

                logger_translated("wallet", LoggerEnum.BUTTON_CLICK)
                if not click_when_target_appears("button_connect_wallet"):
                    refresh_page()
                    continue

                logger_translated(
                    f"select {NETWORKS[network]} network", LoggerEnum.BUTTON_CLICK
                )
                if not click_when_target_appears(f"button_select_network_{network}"):
                    refresh_page()
                    continue

                if not click_when_target_appears(f"button_play"):
                    refresh_page()
                    continue

                logger_translated("select metamask", LoggerEnum.BUTTON_CLICK)
                if not click_when_target_appears(f"button_metamask"):
                    refresh_page()
                    continue

                logger_translated("sign metamask", LoggerEnum.BUTTON_CLICK)
                if not click_when_target_appears("button_sign") and network < 1:
                    Login.do_login(manager, network + 1)
                    break

                if (
                    Screen.wait_for_screen(ScreenEnum.HOME.value)
                    != ScreenEnum.HOME.value
                ):
                    logger("🚫 Failed to login, restart proccess...")
                    continue
                else:
                    logger("🎉 Login successfully!")
                    logged = True
                    break

        manager.set_refresh_timer("refresh_login")
        return logged
