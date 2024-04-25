import cv2  # type: ignore

from .config import Config
from .enum.ScreenEnum import ScreenEnum
from .image import Image
from .utils import do_with_timeout


class Screen:

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

    def wait_for_screen(
        bombScreenEnum, time_beteween: float = 0.5, timeout: float = 60
    ):
        def check_screen(self):
            screen = self.get_current_screen()
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
