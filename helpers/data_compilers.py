import json, os
from zipfile import ZipFile
from io import BytesIO

from typing import Optional, List, Union, Dict
from helpers.datastructs import (
    EngineItem,
    SRL,
    SkinItem,
    BackgroundItem,
    EffectItem,
    ParticleItem,
    PostItem,
    LevelItem,
)

from helpers.repository_map import repo
from helpers.thumbnail import create_square_thumbnail

import pjsk_background_gen_PIL as pjsk_bg
from PIL import Image

cached = {
    "engines": None,
    "skins": None,
    "effects": None,
    "particles": None,
    "backgrounds": None,
    "banner": None,
    "static_posts": None,
    "static_levels": [],
}
cached_static_level_resource_paths = {}
if os.path.exists("levels/compiled_static_levels.json"):
    with open("levels/compiled_static_levels.json", "r", encoding="utf8") as f:
        static_levels_startup = json.load(f)
else:
    static_levels_startup = {"levels": [], "resources": {}}
alr_compiled = set()


def clear_compile_cache(specific: str = None):
    global cached
    if specific:
        cached[specific] = None
    else:
        new_cached = {}
        for k in cached.keys():
            new_cached[k] = None
        cached = new_cached.copy()


def compile_banner() -> Optional[SRL]:
    if cached["banner"]:
        return cached["banner"]
    path = "files/banner/banner.png"
    if os.path.exists(path):
        hash = repo.add_file(path)
        return repo.get_srl(hash)
    return None


def compile_static_posts_list(source: str = None) -> List[PostItem]:
    if cached["static_posts"]:
        return cached["static_posts"]
    compiled_data_list = []
    for post in os.listdir("files/posts"):
        if not os.path.isdir(os.path.join("files", "posts", post)):
            continue
        compiled_data: PostItem = {"tags": []}
        compiled_data["name"] = post
        if source:
            compiled_data["source"] = source
        with open(f"files/posts/{post}/post.json", "r", encoding="utf8") as f:
            post_data: dict = json.load(f)
        if not post_data.get("enabled", True):
            continue
        item_keys = ["version", "title", "time", "author", "description"]
        for key in item_keys:
            compiled_data[key] = post_data[key]
        data_files = {"thumbnail": "thumbnail.png"}
        for key, file in data_files.items():
            hash = repo.add_file(
                f"files/posts/{post}/{file}", error_on_file_nonexistent=False
            )
            if hash:
                compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    cached["static_posts"] = compiled_data_list
    return compiled_data_list


def sort_posts_by_newest(posts: List[PostItem]) -> List[PostItem]:
    return sorted(posts, key=lambda post: post["time"], reverse=True)


def compile_static_levels_list(source: str = None) -> List[LevelItem]:
    global alr_compiled
    if len(alr_compiled) == 0:
        cached["static_levels"] = static_levels_startup["levels"]
        alr_compiled = set([item["name"] for item in cached["static_levels"]])
        cached_static_level_resource_paths = static_levels_startup["resources"]
        for hash, file_path in cached_static_level_resource_paths.items():
            repo._map[hash] = {"hash": hash, "file": file_path}

    levels_root = "levels"
    engines = compile_engines_list(source)
    modified = False
    with os.scandir(levels_root) as entries:
        for entry in entries:
            if entry.is_dir():
                engine_name = entry.name
                engine_path = entry.path
                engine_data: Optional[EngineItem] = next(
                    (engine for engine in engines if engine["name"] == engine_name),
                    None,
                )
                if not engine_data:
                    continue
                for level_file in os.listdir(engine_path):
                    try:
                        invalid_chart_flag = False
                        if not level_file.endswith(".zip"):
                            continue
                        level_path = os.path.join(engine_path, level_file)
                        levelname = os.path.splitext(level_file)[0]
                        if levelname in alr_compiled:
                            continue
                        # iterate all files, {levelname}.zip
                        compiled_data: LevelItem = {
                            "name": levelname,
                            "tags": [
                                {"title": f"Engine: {engine_name}", "icon": "engine"}
                            ],
                            "useSkin": {"useDefault": True},
                            "useEffect": {"useDefault": True},
                            "useParticle": {"useDefault": True},
                            "useBackground": {"useDefault": True},
                            "engine": engine_data,
                        }
                        if source:
                            compiled_data["source"] = source
                        with ZipFile(level_path, "a") as zip_file:
                            with zip_file.open("level.json") as f:
                                level_data = json.load(f)
                            item_keys = [
                                "version",
                                "title",
                                "rating",
                                "author",
                                "artists",
                            ]
                            for key in item_keys:
                                compiled_data[key] = level_data[key]
                            if level_data.get("description"):
                                compiled_data["description"] = level_data["description"]
                            data_files = {
                                "cover": "jacket.png",
                                "data": "level.data",
                                "bgm": "music.mp3",
                                "preview": "music_pre.mp3",
                            }
                            for key, filename in data_files.items():
                                if filename in zip_file.namelist():
                                    hash = repo.add_file(f"{level_path}|{filename}")
                                    if hash:
                                        compiled_data[key] = repo.get_srl(hash)
                                        level_path = level_path.replace("\\", "/")
                                        cached_static_level_resource_paths[hash] = (
                                            f"{level_path}|{filename}"
                                        )
                                else:
                                    if key == "preview":
                                        pass
                                    else:
                                        invalid_chart_flag = True
                                        break
                            if invalid_chart_flag:
                                continue
                            if not "stage.png" in zip_file.namelist():
                                if level_data.get("no_custom_stage"):
                                    pass
                                else:
                                    jacket = Image.open(
                                        BytesIO(zip_file.read("jacket.png"))
                                    )
                                    bg = pjsk_bg.render_v3(jacket)
                                    buf = BytesIO()
                                    bg.save(buf, format="PNG")
                                    stage_bytes = buf.getvalue()
                                    zip_file.writestr("stage.png", stage_bytes)
                            if "stage.png" in zip_file.namelist():
                                hash = repo.add_file(f"{level_path}|stage.png")
                                image = repo.get_srl(hash)
                                level_path = level_path.replace("\\", "/")
                                cached_static_level_resource_paths[hash] = (
                                    f"{level_path}|stage.png"
                                )
                                if "stage_thumbnail.png" not in zip_file.namelist():
                                    bg = Image.open(BytesIO(zip_file.read("stage.png")))
                                    tn = create_square_thumbnail(bg)
                                    buf = BytesIO()
                                    tn.save(buf, format="PNG")
                                    tn_bytes = buf.getvalue()
                                    zip_file.writestr("stage_thumbnail.png", tn_bytes)
                                hash2 = repo.add_file(
                                    f"{level_path}|stage_thumbnail.png"
                                )
                                thumbnail = repo.get_srl(hash2)
                                level_path = level_path.replace("\\", "/")
                                cached_static_level_resource_paths[hash2] = (
                                    f"{level_path}|stage_thumbnail.png"
                                )
                                compiled_data["useBackground"]["useDefault"] = False
                                stage_item: BackgroundItem = {
                                    "name": f"levelbg-{levelname}",
                                    "version": 2,
                                    "tags": [],
                                    "title": level_data["title"],
                                    "subtitle": "UntitledCharts Background",
                                    "author": "YumYummity",
                                    "thumbnail": thumbnail,
                                    "data": engine_data["background"]["data"],
                                    "image": image,
                                    "configuration": engine_data["background"][
                                        "configuration"
                                    ],
                                }
                                compiled_data["useBackground"]["item"] = stage_item
                    except Exception as e:
                        continue
                    modified = True
                    cached["static_levels"].append(compiled_data)
    if modified:
        with open("levels/compiled_static_levels.json", "w", encoding="utf8") as f:
            json.dump(
                {
                    "levels": cached["static_levels"],
                    "resources": cached_static_level_resource_paths,
                },
                f,
            )
    return cached["static_levels"]


def compile_effects_list(source: str = None) -> List[EffectItem]:
    if cached["effects"]:
        return cached["effects"]
    compiled_data_list = []
    for effect in os.listdir("files/effects"):
        if not os.path.isdir(os.path.join("files", "effects", effect)):
            continue
        compiled_data: EffectItem = {"tags": []}
        compiled_data["name"] = effect
        if source:
            compiled_data["source"] = source
        with open(f"files/effects/{effect}/effect.json", "r", encoding="utf8") as f:
            effect_data: dict = json.load(f)
        if not effect_data.get("enabled", True):
            continue
        item_keys = ["version", "title", "subtitle", "author"]
        for key in item_keys:
            compiled_data[key] = effect_data[key]
        data_files = {"thumbnail": "thumbnail.png", "data": "data", "audio": "audio"}
        for key, file in data_files.items():
            hash = repo.add_file(f"files/effects/{effect}/{file}")
            compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    cached["effects"] = compiled_data_list
    return compiled_data_list


def compile_backgrounds_list(source: str = None) -> List[BackgroundItem]:
    if cached["backgrounds"]:
        return cached["backgrounds"]
    compiled_data_list = []
    for background in os.listdir("files/backgrounds"):
        if not os.path.isdir(os.path.join("files", "backgrounds", background)):
            continue
        compiled_data: BackgroundItem = {"tags": []}
        compiled_data["name"] = background
        if source:
            compiled_data["source"] = source
        with open(
            f"files/backgrounds/{background}/background.json", "r", encoding="utf8"
        ) as f:
            background_data: dict = json.load(f)
        if not background_data.get("enabled", True):
            continue
        item_keys = ["version", "title", "subtitle", "author"]
        for key in item_keys:
            compiled_data[key] = background_data[key]
        data_files = {
            "thumbnail": "thumbnail.png",
            "data": "data",
            "image": "image.png",
            "configuration": "configuration.json.gz",
        }
        for key, file in data_files.items():
            hash = repo.add_file(f"files/backgrounds/{background}/{file}")
            compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    cached["backgrounds"] = compiled_data_list
    return compiled_data_list


def compile_particles_list(source: str = None) -> List[ParticleItem]:
    if cached["particles"]:
        return cached["particles"]
    compiled_data_list = []
    for particle in os.listdir("files/particles"):
        if not os.path.isdir(os.path.join("files", "particles", particle)):
            continue
        compiled_data: ParticleItem = {"tags": []}
        compiled_data["name"] = particle
        if source:
            compiled_data["source"] = source
        with open(
            f"files/particles/{particle}/particle.json", "r", encoding="utf8"
        ) as f:
            particle_data: dict = json.load(f)
        if not particle_data.get("enabled", True):
            continue
        item_keys = ["version", "title", "subtitle", "author"]
        for key in item_keys:
            compiled_data[key] = particle_data[key]
        data_files = {
            "thumbnail": "thumbnail.png",
            "data": "data",
            "texture": "texture",
        }
        for key, file in data_files.items():
            hash = repo.add_file(f"files/particles/{particle}/{file}")
            compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    cached["particles"] = compiled_data_list
    return compiled_data_list


def compile_skins_list(source: str = None) -> List[SkinItem]:
    if cached["skins"]:
        return cached["skins"]
    compiled_data_list = []
    for skin in os.listdir("files/skins"):
        if not os.path.isdir(os.path.join("files", "skins", skin)):
            continue
        compiled_data: SkinItem = {"tags": []}
        compiled_data["name"] = skin
        if source:
            compiled_data["source"] = source
        with open(f"files/skins/{skin}/skin.json", "r", encoding="utf8") as f:
            skin_data: dict = json.load(f)
        if not skin_data.get("enabled", True):
            continue
        item_keys = ["version", "title", "subtitle", "author"]
        for key in item_keys:
            compiled_data[key] = skin_data[key]
        data_files = {
            "thumbnail": "thumbnail.png",
            "data": "data",
            "texture": "texture",
        }
        for key, file in data_files.items():
            hash = repo.add_file(f"files/skins/{skin}/{file}")
            compiled_data[key] = repo.get_srl(hash)
        compiled_data_list.append(compiled_data)
    cached["skins"] = compiled_data_list
    return compiled_data_list


def compile_engines_list(source: str = None) -> List[EngineItem]:
    if cached["engines"]:
        return cached["engines"]
    compiled_data_list = []
    for engine in os.listdir("files/engines"):
        if not os.path.isdir(os.path.join("files", "engines", engine)):
            continue
        compiled_data: EngineItem = {
            "tags": [],
            "actions": [],
            "hasCommunity": False,
            "leaderboards": [],
            "sections": [],
        }
        with open(f"files/engines/{engine}/engine.json", "r", encoding="utf8") as f:
            engine_data: dict = json.load(f)
        if not engine_data.get("enabled", True):
            continue
        if engine_data.get("description"):
            compiled_data["description"] = engine_data["description"]
        compiled_data["name"] = engine
        if source:
            compiled_data["source"] = source
        item_keys = ["version", "title", "subtitle", "author"]
        for key in item_keys:
            compiled_data[key] = engine_data[key]
        data_files = {
            "thumbnail": "thumbnail.png",
            "configuration": "configuration.json.gz",
            "playData": "playData",
            "watchData": "watchData",
            "previewData": "previewData",
            "tutorialData": "tutorialData",
        }
        for key, file in data_files.items():
            hash = repo.add_file(f"files/engines/{engine}/{file}")
            compiled_data[key] = repo.get_srl(hash)
        skins = compile_skins_list(source)
        skin_data = next(
            skin for skin in skins if skin["name"] == engine_data["skin_name"]
        )
        compiled_data["skin"] = skin_data
        effects = compile_effects_list(source)
        effect_data = next(
            effect for effect in effects if effect["name"] == engine_data["effect_name"]
        )
        compiled_data["effect"] = effect_data
        particles = compile_particles_list(source)
        particle_data = next(
            particle
            for particle in particles
            if particle["name"] == engine_data["particle_name"]
        )
        compiled_data["particle"] = particle_data
        backgrounds = compile_backgrounds_list(source)
        background_data = next(
            background
            for background in backgrounds
            if background["name"] == engine_data["background_name"]
        )
        compiled_data["background"] = background_data
        compiled_data_list.append(compiled_data)
    cached["engines"] = compiled_data_list
    return compiled_data_list
