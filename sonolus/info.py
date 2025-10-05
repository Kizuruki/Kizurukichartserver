donotload = False

from fastapi import APIRouter, Request

from helpers.data_compilers import compile_banner, compile_static_levels_list
from helpers.datastructs import ServerInfoButton

from typing import List

router = APIRouter()


def setup():
    @router.get("/")
    async def main(request: Request):
        # d = await request.app.run_blocking(compile_static_levels_list, request.app.base_url)
        # extended_description = f"\nCurrently archiving {len(d):,} charts!"  # generated
        extended_description = ""

        # XXX https://wiki.sonolus.com/custom-server-specs/endpoints/get-sonolus-info
        banner_srl = await request.app.run_blocking(compile_banner)
        button_list = [
            "post",
            "level",
            # "playlist",
            "skin",
            "background",
            "effect",
            "particle",
            "engine",
        ]
        buttons: List[ServerInfoButton] = [{"type": button} for button in button_list]
        data = {
            "title": request.app.config["name"],
            "description": f"{request.app.config['description']}\n{extended_description}",
            "buttons": buttons,
            "configuration": {"options": []},
        }
        if banner_srl:
            data["banner"] = banner_srl
        return data
