from enum import Enum

import cv2

from .config import Config
from .image import Image
from .logger import LoggerEnum, logger, logger_translated
from .mouse import *
from .utils import *

NETWORKS = {
    0: "Binance",
    1: "Polygon",
}


class BombScreenEnum(Enum):
    NOT_FOUND = -1
    LOGIN = 0
    HOME = 1
    TREASURE_HUNT = 2
    HEROES = 3
    WALLET = 4
    SETTINGS = 5
    POPUP_ERROR = 6


class BombScreen:

    def wait_for_screen(bombScreenEnum, time_between: float = 0.5, timeout: float = 30):
        logger(
            f"🕑 Waiting for {BombScreenEnum(bombScreenEnum).name} screen...",
            end="",
        )

        def check_screen():
            logger("...", end="", datetime=False)
            screen = BombScreen.get_current_screen()
            if screen == bombScreenEnum:
                return True
            else:
                return None

        res = do_with_timeout(check_screen, time_between=time_between, timeout=timeout)

        logger("", datetime=False)
        if res is None:
            raise Exception(
                f"Timeout waiting for screen {BombScreenEnum(bombScreenEnum).name}."
            )

        return res

    def wait_for_leave_screen(
        bombScreenEnum, time_between: float = 0.5, timeout: float = 60
    ):
        logger(
            f"🕑 Waiting for leaving {BombScreenEnum(bombScreenEnum).name} screen...",
            end="",
        )

        def check_screen():
            logger("...", end="", datetime=False)
            screen = BombScreen.get_current_screen()
            if screen == bombScreenEnum:
                return None
            else:
                return True

        res = do_with_timeout(check_screen, time_between=time_between, timeout=timeout)

        if res:
            logger("", datetime=False)
            return res

    def get_current_screen(time_between: float = 0.5, timeout: float = 20):
        targets = {
            BombScreenEnum.LOGIN.value: Image.TARGETS["identify_login"],
            BombScreenEnum.HOME.value: Image.TARGETS["identify_home"],
            BombScreenEnum.TREASURE_HUNT.value: Image.TARGETS["identify_treasure_hunt"],
            BombScreenEnum.HEROES.value: Image.TARGETS["identify_heroes"],
            BombScreenEnum.WALLET.value: Image.TARGETS["identify_wallet"],
            BombScreenEnum.SETTINGS.value: Image.TARGETS["identify_settings"],
            BombScreenEnum.POPUP_ERROR.value: Image.TARGETS["popup_error"],
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
        if current_screen == BombScreenEnum.HOME.value:
            return
        elif current_screen == BombScreenEnum.TREASURE_HUNT.value:
            click_when_target_appears("button_back")
        elif current_screen == BombScreenEnum.HEROES.value:
            click_when_target_appears("button_x_close")
        elif current_screen == BombScreenEnum.WALLET.value:
            click_when_target_appears("button_back")
            return BombScreen.go_to_home(manager)
        else:
            Auth.login(manager)
            return

        BombScreen.wait_for_screen(BombScreenEnum.HOME.value)

    def go_to_heroes(manager, current_screen=None):
        if not Auth.is_authenticated:
            Auth.login(manager)
            return BombScreen.go_to_heroes(manager)

        current_screen = (
            BombScreen.get_current_screen()
            if current_screen == None
            else current_screen
        )

        if current_screen == BombScreenEnum.HEROES.value:
            return
        elif current_screen == BombScreenEnum.TREASURE_HUNT.value:
            click_when_target_appears("button_open_menu")
            time.sleep(1)
            click_when_target_appears("button_hero")
            BombScreen.wait_for_screen(BombScreenEnum.HEROES.value)
        elif current_screen == BombScreenEnum.HOME.value:
            click_when_target_appears("button_farming")
            BombScreen.wait_for_screen(BombScreenEnum.TREASURE_HUNT.value)
            return BombScreen.go_to_heroes(manager)
        elif current_screen == BombScreenEnum.WALLET.value:
            click_when_target_appears("button_back")
            BombScreen.wait_for_leave_screen(BombScreenEnum.WALLET.value)
            return BombScreen.go_to_heroes(manager)
        elif current_screen == BombScreenEnum.SETTINGS.value:
            click_when_target_appears("button_x_close")
            BombScreen.wait_for_leave_screen(BombScreenEnum.SETTINGS.value)
            return BombScreen.go_to_heroes(manager)
        else:
            BombScreen.go_to_home(manager)
            BombScreen.wait_for_screen(BombScreenEnum.HOME.value)
            return BombScreen.go_to_heroes(manager)

    def go_to_farming(manager):
        if not Auth.is_authenticated:
            Auth.login(manager)
            return BombScreen.go_to_farming(manager)

        current_screen = BombScreen.get_current_screen()

        def close_menu():
            if not click_when_target_appears("button_close_menu", timeout=1.5):
                click_in_the_middle_of_the_screen()

        if current_screen == BombScreenEnum.TREASURE_HUNT.value:
            # Sometimes the menu could be open, so we close it
            close_menu()
            return
        elif current_screen == BombScreenEnum.HOME.value:
            click_when_target_appears("button_farming")
            BombScreen.wait_for_screen(BombScreenEnum.TREASURE_HUNT.value)
        elif current_screen == BombScreenEnum.HEROES.value:
            click_when_target_appears("button_x_close")
            close_menu()
        elif current_screen == BombScreenEnum.WALLET.value:
            click_when_target_appears("button_back")
        elif current_screen == BombScreenEnum.SETTINGS.value:
            click_when_target_appears("button_x_close")
            click_when_target_appears("button_farming")
            BombScreen.wait_for_screen(BombScreenEnum.TREASURE_HUNT.value)
        else:
            BombScreen.go_to_home(manager)
            click_when_target_appears("button_farming")
            BombScreen.wait_for_screen(BombScreenEnum.TREASURE_HUNT.value)

    def go_to_wallet(manager):
        if BombScreen.get_current_screen() == BombScreenEnum.WALLET.value:
            return
        else:
            BombScreen.go_to_farming(manager)
            click_when_target_appears("button_wallet")
            BombScreen.wait_for_screen(BombScreenEnum.WALLET.value)


class Login:
    def do_login(manager, network=0):
        current_screen = BombScreen.get_current_screen()
        logged = False

        if (
            current_screen != BombScreenEnum.LOGIN.value
            and current_screen != BombScreenEnum.NOT_FOUND.value
            and current_screen != BombScreenEnum.POPUP_ERROR.value
        ):
            logged = True

        if not logged:
            logger_translated("login", LoggerEnum.ACTION)

            login_attempts = Config.PROPERTIES["screen"]["number_login_attempts"]

            for current_attempt in range(login_attempts):

                if BombScreen.get_current_screen() != BombScreenEnum.LOGIN.value:
                    refresh_page()
                    BombScreen.wait_for_screen(BombScreenEnum.LOGIN.value)

                logger_translated("Login", LoggerEnum.PAGE_FOUND)

                logger_translated("connect wallet", LoggerEnum.BUTTON_CLICK)
                if not click_when_target_appears("button_connect_wallet"):
                    refresh_page()
                    continue

                logger_translated(
                    f"select {NETWORKS[network]} network", LoggerEnum.BUTTON_CLICK
                )
                if not click_when_target_appears(f"button_select_network_{network}"):
                    refresh_page()
                    continue

                logger_translated("play", LoggerEnum.BUTTON_CLICK)
                if not click_when_target_appears(f"button_play"):
                    refresh_page()
                    continue

                logger_translated("select metamask", LoggerEnum.BUTTON_CLICK)
                if not click_when_target_appears(f"button_metamask"):
                    refresh_page()
                    continue

                logger_translated("sign metamask", LoggerEnum.BUTTON_CLICK)
                if not click_when_target_appears("button_sign") and network < 1:
                    logger_translated(
                        f"login network {NETWORKS[network]}", LoggerEnum.ACTION
                    )
                    Auth.login(manager, network + 1)
                    break

                if (
                    BombScreen.wait_for_screen(BombScreenEnum.HOME.value)
                    != BombScreenEnum.HOME.value
                ):
                    logger("🚫 Failed to login, restart proccess...")
                    continue
                else:
                    logger("🎉 Login successfully!")
                    logged = True
                    break

        manager.set_refresh_timer("refresh_login")
        return logged


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


class Hero:
    def who_needs_work(manager):
        logger_translated(f"Heroes to work", LoggerEnum.ACTION)

        heroes_bar = [
            "hero_bar_0",
            "hero_bar_10",
            "hero_bar_20",
            "hero_bar_30",
            "hero_bar_40",
            "hero_bar_50",
            "hero_bar_60",
            "hero_bar_70",
            "hero_bar_80",
            "hero_bar_90",
            "hero_bar_100",
        ]
        heroes_rarity = [
            "hero_rarity_Common_full",
            "hero_rarity_Common_min",
            "hero_rarity_Common_mid",
            "hero_rarity_Rare_full",
            "hero_rarity_Rare_min",
            "hero_rarity_Rare_mid",
            "hero_rarity_SuperRare_full",
            "hero_rarity_SuperRare_min",
            "hero_rarity_SuperRare_mid",
            "hero_rarity_Epic_full",
            "hero_rarity_Epic_min",
            "hero_rarity_Epic_mid",
            "hero_rarity_Legend_full",
            "hero_rarity_Legend_min",
            "hero_rarity_Legend_mid",
            "hero_rarity_SuperLegend_full",
            "hero_rarity_SuperLegend_min",
            "hero_rarity_SuperLegend_mid",
        ]

        scale_factor = 10

        BombScreen.go_to_heroes(manager)

        def click_available_heroes():
            n_clicks = 0
            screen_img = Image.screen()
            buttons_position = Image.get_target_positions(
                "button_work",
                screen_image=screen_img,
            )

            logger(f"👁️ Found {len(buttons_position)} Heroes resting...")

            if not buttons_position:
                return 0

            x_buttons = buttons_position[0][0]
            height, width = Image.TARGETS["hero_search_area"].shape[:2]
            screen_img = screen_img[
                :,
                x_buttons - width - Image.MONITOR_LEFT : x_buttons - Image.MONITOR_LEFT,
                :,
            ]
            logger("↳", end=" ", datetime=False)
            for button_position in buttons_position:
                x, y, w, h = button_position
                offset = int((height - h) / 2)
                search_img = screen_img[y - offset : y + height - offset, :, :]

                rarity_max_values = [
                    Image.get_compare_result(search_img, Image.TARGETS[rarity]).max()
                    for rarity in heroes_rarity
                ]

                rarity_index = find_highest_index_max(rarity_max_values)

                hero_rarity = heroes_rarity[rarity_index].split("_")[2]
                logger(f"{hero_rarity}:", end=" ", datetime=False)

                life_max_values = [
                    Image.get_compare_result(search_img, Image.TARGETS[bar]).max()
                    for bar in heroes_bar
                ]
                life_index = find_highest_index_max(life_max_values)
                logger(f"{life_index * scale_factor}%", end=" ", datetime=False)

                if life_index * scale_factor >= Config.get(
                    "heroes_work_mod", hero_rarity
                ):
                    click_randomly_in_position(x, y, w, h)
                    n_clicks += 1
                    logger("💪;", end=" ", datetime=False)
                else:
                    logger("💤;", end=" ", datetime=False)

            logger("", datetime=False)
            return n_clicks

        n_clicks_per_scrool = scroll_and_click_on_targets(
            safe_scroll_target="hero_bar_vertical",
            repeat=Config.get("screen", "scroll_heroes", "repeat"),
            distance=Config.get("screen", "scroll_heroes", "distance"),
            duration=Config.get("screen", "scroll_heroes", "duration"),
            wait=Config.get("screen", "scroll_heroes", "wait"),
            function_between=click_available_heroes,
        )

        logger(
            f"🏃 {sum(n_clicks_per_scrool)} new heros sent to explode everything 💣💣💣."
        )
        Hero.refresh_hunt(manager)
        manager.set_refresh_timer("refresh_heroes")
        return True

    def refresh_hunt(manager):
        logger_translated("hunting positions", LoggerEnum.TIMER_REFRESH)

        BombScreen.go_to_farming(manager)
        BombScreen.go_to_home(manager)
        BombScreen.go_to_farming(manager)

        manager.set_refresh_timer("refresh_hunt")
        return True

    def do_check_error(manager):
        current_screen = BombScreen.get_current_screen()

        if (
            current_screen == BombScreenEnum.POPUP_ERROR.value
            or current_screen == BombScreenEnum.NOT_FOUND.value
        ):
            logger_translated(
                "Check screen error found, restarting...", LoggerEnum.ERROR
            )
            Auth.login(manager)
            BombScreen.go_to_heroes(manager)
            BombScreen.go_to_farming(manager)

        manager.set_refresh_timer("refresh_check_error")


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
