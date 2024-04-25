from enum import Enum

import cv2

from .config import Config
from .enum.ScreenEnum import ScreenEnum
from .image import Image
from .logger import LoggerEnum, logger, logger_translated
from .login import Login
from .mouse import *
from .utils import *


class BombScreen:

    def wait_for_screen(
        bombScreenEnum, time_beteween: float = 0.5, timeout: float = 60
    ):
        def check_screen():
            screen = BombScreen.get_current_screen()
            if screen == bombScreenEnum:
                return True
            else:
                return None

        res = do_with_timeout(
            check_screen, time_beteween=time_beteween, timeout=timeout
        )

        if res is None:
            raise Exception(
                f"Timeout waiting for screen {ScreenEnum(bombScreenEnum).name}."
            )

        return res

    def wait_for_leave_screen(
        bombScreenEnum, time_beteween: float = 0.5, timeout: float = 60
    ):
        def check_screen():
            screen = BombScreen.get_current_screen()
            if screen == bombScreenEnum:
                return None
            else:
                return True

        return do_with_timeout(
            check_screen, time_beteween=time_beteween, timeout=timeout
        )

    def get_current_screen(time_beteween: float = 0.5, timeout: float = 20):
        targets = {
            ScreenEnum.HOME.value: Image.TARGETS["identify_home"],
            ScreenEnum.HEROES.value: Image.TARGETS["identify_heroes"],
            ScreenEnum.LOGIN.value: Image.TARGETS["identify_login"],
            ScreenEnum.TREASURE_HUNT.value: Image.TARGETS["identify_treasure_hunt"],
            ScreenEnum.WALLET.value: Image.TARGETS["identify_wallet"],
            ScreenEnum.POPUP_ERROR.value: Image.TARGETS["popup_error"],
            ScreenEnum.SETTINGS.value: Image.TARGETS["identify_settings"],
        }
        max_value = 0
        img = Image.screen()
        screen_name = -1

        for name, target_img in targets.items():
            result = cv2.matchTemplate(img, target_img, cv2.TM_CCOEFF_NORMED)
            max_value_local = result.max()
            if max_value_local > max_value:
                max_value = max_value_local
                screen_name = name

        return screen_name if max_value > Config.get("threshold", "default") else -1

    def go_to_home(manager, current_screen=None):
        current_screen = (
            BombScreen.get_current_screen()
            if current_screen == None
            else current_screen
        )
        if current_screen == ScreenEnum.HOME.value:
            return
        elif current_screen == ScreenEnum.TREASURE_HUNT.value:
            click_when_target_appears("button_back")
        elif current_screen == ScreenEnum.HEROES.value:
            click_when_target_appears("button_x_close")
        elif current_screen == ScreenEnum.WALLET.value:
            click_when_target_appears("button_back")
            return BombScreen.go_to_home(manager)
        else:
            Login.do_login(manager)
            return

        BombScreen.wait_for_screen(ScreenEnum.HOME.value)

    def go_to_heroes(manager, current_screen=None):
        current_screen = (
            BombScreen.get_current_screen()
            if current_screen == None
            else current_screen
        )

        if current_screen == ScreenEnum.HOME.value:
            click_when_target_appears("button_heroes")
            BombScreen.wait_for_screen(ScreenEnum.HEROES.value)

        elif current_screen == ScreenEnum.HEROES.value:
            return

        elif (
            current_screen == ScreenEnum.WALLET.value
            or current_screen == ScreenEnum.SETTINGS.value
        ):
            click_when_target_appears("buttun_x_close")
            BombScreen.wait_for_leave_screen(ScreenEnum.WALLET.value)
            BombScreen.go_to_home(manager)
            return BombScreen.go_to_heroes(manager)

        else:
            Login.do_login(manager)
            BombScreen.go_to_heroes(manager)

    def go_to_treasure_hunt(manager):
        if BombScreen.get_current_screen() == ScreenEnum.TREASURE_HUNT.value:
            return
        else:
            BombScreen.go_to_home(manager)
            click_when_target_appears("identify_home")
            BombScreen.wait_for_screen(ScreenEnum.TREASURE_HUNT.value)

    def go_to_chest(manager):
        if BombScreen.get_current_screen() == ScreenEnum.WALLET.value:
            return
        else:
            BombScreen.go_to_treasure_hunt(manager)
            click_when_target_appears("button_hunt_chest")
            BombScreen.wait_for_screen(ScreenEnum.WALLET.value)

    # def do_print_chest(manager):
    #     logger_translated("print chest", LoggerEnum.ACTION)

    #     if BombScreen.get_current_screen() != ScreenEnum.TREASURE_HUNT.value:
    #         BombScreen.go_to_treasure_hunt(manager)

    #     click_when_target_appears("button_hunt_chest")
    #     BombScreen.wait_for_screen(ScreenEnum.WALLET.value)
    #     image = None
    #     try:
    #         if Config.get("screen", "print_full_screen"):
    #             image = Image.print_full_screen("chest", "chest_screen_for_geometry")
    #         else:
    #             image = Image.print_partial_screen("chest", "chest_screen_for_geometry")

    #         TelegramBot.send_message_with_image(
    #             image,
    #             "Se liga no BCOIN desse baú, não deixe de contribuir com a evolução do bot :D",
    #         )
    #     except Exception as e:
    #         logger(str(e))
    #         logger(
    #             "😬 Ohh no! We couldn't send your farm report to Telegram.",
    #             color="yellow",
    #             force_log_file=True,
    #         )

    #     BombScreen.go_to_treasure_hunt(manager)
    #     manager.set_refresh_timer("refresh_print_chest")


# def select_network_and_connect():
#     logger_translated("choose network", LoggerEnum.ACTION)

#     # Inject JavaScript to interact with MetaMask
#     pyautogui.hotkey("ctrl", "shift", "j")
#     time.sleep(1)
#     pyautogui.typewrite(
#         'window.ethereum.request({ method: "net_version" }).then(networkId => { alert(networkId); });',
#         interval=0.1,
#     )
#     pyautogui.press("enter")

#     # Wait for the network id to be logged in the console
#     time.sleep(2)

#     # Close the browser developer tools
#     pyautogui.hotkey("ctrl", "shift", "j")

#     pyautogui.press("esc")

#     # Get the network id from the clipboard
#     network_id = pyperclip.paste()

#     logger.log(f"Network id: {network_id}")
