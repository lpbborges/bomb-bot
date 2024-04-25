from .enum.ScreenEnum import ScreenEnum
from .bombScreen import BombScreen
from .image import Image
from .logger import LoggerEnum, logger, logger_translated
from .login import Login
from .mouse import *


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
            "hero_rarity_Common",
            "hero_rarity_Rare",
            "hero_rarity_SuperRare",
            "hero_rarity_Epic",
            "hero_rarity_Legend",
            "hero_rarity_SuperLegend",
        ]

        scale_factor = 10

        current_screen = BombScreen.get_current_screen()
        BombScreen.go_to_home(manager, current_screen)
        current_screen = ScreenEnum.HOME.value
        BombScreen.go_to_heroes(manager, current_screen)

        def click_available_heroes():
            n_clicks = 0
            screen_img = Image.screen()

            buttons_position = Image.get_target_positions(
                "button_work_unchecked",
                not_target="button_work_checked",
                screen_image=screen_img,
            )
            logger(f"👁️  Found {len(buttons_position)} Heroes resting:")

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
                search_img = screen_img[y : y + height, :, :]

                rarity_max_values = [
                    Image.get_compare_result(search_img, Image.TARGETS[rarity]).max()
                    for rarity in heroes_rarity
                ]
                rarity_index, rarity_max_value = 0, 0
                for i, value in enumerate(rarity_max_values):
                    rarity_index, rarity_max_value = (
                        (i, value)
                        if value > rarity_max_value
                        else (rarity_index, rarity_max_value)
                    )

                hero_rarity = heroes_rarity[rarity_index].split("_")[-1]
                logger(f"{hero_rarity}:", end=" ", datetime=False)

                life_max_values = [
                    Image.get_compare_result(search_img, Image.TARGETS[bar]).max()
                    for bar in heroes_bar
                ]
                life_index, life_max_value = 0, 0
                for i, value in enumerate(life_max_values):
                    life_index, life_max_value = (
                        (i, value)
                        if value >= life_max_value
                        else (life_index, life_max_value)
                    )

                logger(f"{life_index*scale_factor}%", end=" ", datetime=False)
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

        BombScreen.go_to_home(manager)
        BombScreen.go_to_treasure_hunt(manager)

        manager.set_refresh_timer("refresh_hunt")
        return True

    def do_check_error(manager):
        current_screen = BombScreen.get_current_screen()

        if (
            current_screen == ScreenEnum.POPUP_ERROR.value
            or current_screen == ScreenEnum.NOT_FOUND.value
        ):
            logger_translated(
                "Check screen error found, restarting...", LoggerEnum.ERROR
            )
            Login.do_login(manager)
            BombScreen.go_to_heroes(manager)
            BombScreen.go_to_treasure_hunt(manager)

        manager.set_refresh_timer("refresh_check_error")
