donotload = False

from fastapi import APIRouter, Request
from fastapi import HTTPException, status

from helpers.data_compilers import (
    compile_engines_list,
    compile_backgrounds_list,
    compile_effects_list,
    compile_particles_list,
    compile_skins_list,
    compile_static_posts_list,
    # compile_playlists_list,
    compile_static_levels_list,
    # compile_replays_list,
    # compile_rooms_list
)
from helpers.sonolus_typings import ItemType
from helpers.datastructs import ServerItemDetails, get_item_type

router = APIRouter()


def setup():
    @router.get("/")
    async def main(request: Request, item_type: ItemType, item_name: str):
        if item_type == "engines":
            data = await request.app.run_blocking(
                compile_engines_list, request.app.base_url
            )
        elif item_type == "skins":
            data = await request.app.run_blocking(
                compile_skins_list, request.app.base_url
            )
        elif item_type == "backgrounds":
            if item_name.startswith("levelbg-"):
                level_data = await request.app.run_blocking(
                    compile_static_levels_list, request.app.base_url
                )
                level_item = next(
                    item
                    for item in level_data
                    if item["name"] == item_name.removeprefix("levelbg-")
                )
                data = [level_item["useBackground"]["item"]]
            else:
                data = await request.app.run_blocking(
                    compile_backgrounds_list, request.app.base_url
                )
        elif item_type == "effects":
            data = await request.app.run_blocking(
                compile_effects_list, request.app.base_url
            )
        elif item_type == "particles":
            data = await request.app.run_blocking(
                compile_particles_list, request.app.base_url
            )
        elif item_type == "posts":
            data = await request.app.run_blocking(
                compile_static_posts_list, request.app.base_url
            )
            # maybe also grab non-static posts lol
        # elif item_type == "playlists":
        #     data = await request.app.run_blocking(compile_playlists_list, request.app.base_url)
        elif item_type == "levels":
            data = await request.app.run_blocking(
                compile_static_levels_list, request.app.base_url
            )
        # elif item_type == "replays":
        #     data = await request.app.run_blocking(compile_replays_list, request.app.base_url)
        # elif item_type == "rooms":
        #     data = await request.app.run_blocking(compile_rooms_list, request.app.base_url)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Item "{item_type}" not found.',
            )
        item_data = next((i for i in data if i["name"] == item_name), None)
        if not item_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{item_type.capitalize().removesuffix('s')} item \"{item_name}\" not found.",
            )

        T = get_item_type(item_type)
        detail: ServerItemDetails[T] = {
            "item": item_data,
            "actions": [],
            "hasCommunity": False,
            "leaderboards": [],
            "sections": [],
        }
        if item_data.get("description"):
            detail["description"] = item_data["description"]
        return detail
