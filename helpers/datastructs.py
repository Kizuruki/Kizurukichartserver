from typing import TypedDict, List, Optional, Union, Literal, TypeVar

from helpers.sonolus_typings import Grade, ServerInfoButtonType, Text, Icon, ItemType

TPostItem = TypeVar("TPostItem", bound="PostItem")
TPlaylistItem = TypeVar("TPlaylistItem", bound="PlaylistItem")
TLevelItem = TypeVar("TLevelItem", bound="LevelItem")
TSkinItem = TypeVar("TSkinItem", bound="SkinItem")
TBackgroundItem = TypeVar("TBackgroundItem", bound="BackgroundItem")
TEffectItem = TypeVar("TEffectItem", bound="EffectItem")
TParticleItem = TypeVar("TParticleItem", bound="ParticleItem")
TEngineItem = TypeVar("TEngineItem", bound="EngineItem")
TReplayItem = TypeVar("TReplayItem", bound="ReplayItem")
TRoomItem = TypeVar("TRoomItem", bound="RoomItem")

T = TypeVar("T")


class Tag(TypedDict):
    title: str
    icon: Optional[str]


class SRL(TypedDict):
    hash: str
    url: str


class SIL(TypedDict):
    address: str
    name: str


# region Items


class BackgroundItem(TypedDict):
    name: str
    source: Optional[str]
    version: int
    title: str
    subtitle: str
    author: str
    tags: List[Tag]
    thumbnail: SRL
    data: SRL
    image: SRL
    configuration: SRL


class ParticleItem(TypedDict):
    name: str
    source: Optional[str]
    version: int
    title: str
    subtitle: str
    author: str
    tags: List[Tag]
    thumbnail: SRL
    data: SRL
    texture: SRL


class EffectItem(TypedDict):
    name: str
    source: Optional[str]
    version: int
    title: str
    subtitle: str
    author: str
    tags: List[Tag]
    thumbnail: SRL
    data: SRL
    audio: SRL


class SkinItem(TypedDict):
    name: str
    source: Optional[str]
    version: int
    title: str
    subtitle: str
    author: str
    tags: List[Tag]
    thumbnail: SRL
    data: SRL
    texture: SRL


class EngineItem(TypedDict):
    name: str
    version: int
    title: str
    subtitle: str
    source: Optional[str]
    author: str
    tags: List[Tag]
    description: Optional[str]

    skin: SkinItem
    background: BackgroundItem
    effect: EffectItem
    particle: ParticleItem

    thumbnail: SRL
    playData: SRL
    watchData: SRL
    previewData: SRL
    tutorialData: SRL
    rom: Optional[SRL]
    configuration: SRL


class PostItem(TypedDict):
    name: str
    source: Optional[str]
    version: int
    title: str
    time: int
    author: str
    tags: List[Tag]
    thumbnail: Optional[SRL]


class UseItem(TypedDict, total=False):
    useDefault: bool
    item: Optional[Union[SkinItem, BackgroundItem, EffectItem, ParticleItem]]


class LevelItem(TypedDict):
    name: str
    source: Optional[str]
    version: int
    rating: int
    title: str
    artists: str
    author: str
    tags: List[Tag]
    engine: EngineItem
    useSkin: UseItem[SkinItem]
    useBackground: UseItem[BackgroundItem]
    useEffect: UseItem[EffectItem]
    useParticle: UseItem[ParticleItem]
    cover: SRL
    bgm: SRL
    preview: Optional[SRL]
    data: SRL


class PlaylistItem(TypedDict):
    name: str
    source: Optional[str]
    version: int
    title: str
    subtitle: str
    author: str
    tags: List[Tag]
    levels: List[LevelItem]
    thumbnail: Optional[SRL]


class RoomItem(TypedDict):
    name: str
    title: str
    subtitle: str
    master: str
    tags: List[Tag]
    cover: Optional[SRL]
    bgm: Optional[SRL]
    preview: Optional[SRL]


class ReplayItem(TypedDict):
    name: str
    source: Optional[str]
    version: int
    title: str
    subtitle: str
    author: str
    tags: List[Tag]
    level: LevelItem
    data: SRL
    configuration: SRL


ServerItem = Union[
    PostItem,
    RoomItem,
    SkinItem,
    BackgroundItem,
    ParticleItem,
    EffectItem,
    RoomItem,
    PlaylistItem,
    ReplayItem,
    LevelItem,
    EngineItem,
]


def get_item_type(type: ItemType) -> ServerItem:
    if type == "posts":
        return PostItem()
    elif type == "playlists":
        return PlaylistItem()
    elif type == "levels":
        return LevelItem()
    elif type == "skins":
        return SkinItem()
    elif type == "backgrounds":
        return BackgroundItem()
    elif type == "effects":
        return EffectItem()
    elif type == "particles":
        return ParticleItem()
    elif type == "engines":
        return EngineItem()
    elif type == "replays":
        return ReplayItem()
    elif type == "rooms":
        return RoomItem()
    else:
        raise ValueError(f"Unknown item type: {type}")


# endregion

# region Server


class ServerInfoButton(TypedDict):
    type: ServerInfoButtonType


class ServerCollectionItemOption(TypedDict):
    query: str
    name: Union[Text, str]
    description: Optional[str]
    required: bool
    type: Literal["collectionItem"]
    itemType: ItemType


ServerTextOption = TypedDict(
    "ServerTextOption",
    {
        "query": str,
        "name": Union[Text, str],
        "description": Optional[str],
        "required": bool,
        "type": Literal["text"],
        "def": str,
        "placeholder": Union[Text, str],
        "limit": int,
        "shortcuts": List[str],
    },
)

ServerTextAreaOption = TypedDict(
    "ServerTextAreaOption",
    {
        "query": str,
        "name": Union[Text, str],
        "description": Optional[str],
        "required": bool,
        "type": Literal["textArea"],
        "def": str,
        "placeholder": Union[Text, str],
        "limit": int,
        "shortcuts": List[str],
    },
)

ServerSliderOption = TypedDict(
    "ServerSliderOption",
    {
        "query": str,
        "name": Union[Text, str],
        "description": Optional[str],
        "required": bool,
        "type": Literal["slider"],
        "def": Union[int, float],
        "min": Union[int, float],
        "max": Union[int, float],
        "step": Union[int, float],
        "unit": Optional[Union[Text, str]],
    },
)

ServerToggleOption = TypedDict(
    "ServerToggleOption",
    {
        "query": str,
        "name": Union[Text, str],
        "description": Optional[str],
        "required": bool,
        "type": Literal["toggle"],
        "def": bool,
    },
)


class _ServerOption_Values(TypedDict):
    name: str
    title: Union[Text, str]


ServerSelectOption = TypedDict(
    "ServerSelectOption",
    {
        "query": str,
        "name": Union[Text, str],
        "description": Optional[str],
        "required": bool,
        "type": Literal["select"],
        "def": str,
        "values": List[_ServerOption_Values],
    },
)

ServerMultiOption = TypedDict(
    "ServerMultiOption",
    {
        "query": str,
        "name": Union[Text, str],
        "description": Optional[str],
        "required": bool,
        "type": Literal["multi"],
        "def": List[bool],
        "values": List[_ServerOption_Values],
    },
)

ServerServerItemOption = TypedDict(
    "ServerServerItemOption",
    {
        "query": str,
        "name": Union[Text, str],
        "description": Optional[str],
        "required": bool,
        "type": Literal["serverItem"],
        "itemType": ItemType,
        "def": Optional[SIL],
        "allowOtherServers": bool,
    },
)

ServerServerItemsOption = TypedDict(
    "ServerServerItemsOption",
    {
        "query": str,
        "name": Union[Text, str],
        "description": Optional[str],
        "required": bool,
        "type": Literal["serverItems"],
        "itemType": ItemType,
        "def": List[SIL],
        "allowOtherServers": bool,
        "limit": int,
    },
)

ServerCollectionItemOption = TypedDict(
    "ServerCollectionItemOption",
    {
        "query": str,
        "name": Union[Text, str],
        "description": Optional[str],
        "required": bool,
        "type": Literal["collectionItem"],
        "itemType": ItemType,
    },
)

ServerFileOption = TypedDict(
    "ServerFileOption",
    {
        "query": str,
        "name": Union[Text, str],
        "description": Optional[str],
        "required": bool,
        "type": Literal["file"],
        "def": str,
    },
)

ServerOption = Union[
    ServerTextOption,
    ServerTextAreaOption,
    ServerSliderOption,
    ServerToggleOption,
    ServerSelectOption,
    ServerMultiOption,
    ServerServerItemOption,
    ServerServerItemsOption,
    ServerCollectionItemOption,
    ServerFileOption,
]


class ServerForm(TypedDict):
    type: str
    title: Union[Text, str]
    icon: Optional[Union[Icon, str]]
    description: Optional[str]
    help: Optional[str]
    requireConfirmation: bool
    options: list[ServerOption]


class ServerMessage(TypedDict):
    message: str


class ServerItemSectionTyped(TypedDict, total=False):
    title: Union[str, "Text"]
    icon: Optional[Union["Icon", str]]
    description: Optional[str]
    help: Optional[str]
    itemType: ItemType
    items: List[
        Union[
            TPostItem,
            TPlaylistItem,
            TLevelItem,
            TSkinItem,
            TBackgroundItem,
            TEffectItem,
            TParticleItem,
            TEngineItem,
            TReplayItem,
            TRoomItem,
        ]
    ]
    search: Optional["ServerForm"]
    searchValues: Optional[str]


class PostItemSection(ServerItemSectionTyped):
    itemType: Literal["post"]
    items: List[TPostItem]


class PlaylistItemSection(ServerItemSectionTyped):
    itemType: Literal["playlist"]
    items: List[TPlaylistItem]


class LevelItemSection(ServerItemSectionTyped):
    itemType: Literal["level"]
    items: List[TLevelItem]


class SkinItemSection(ServerItemSectionTyped):
    itemType: Literal["skin"]
    items: List[TSkinItem]


class BackgroundItemSection(ServerItemSectionTyped):
    itemType: Literal["background"]
    items: List[TBackgroundItem]


class EffectItemSection(ServerItemSectionTyped):
    itemType: Literal["effect"]
    items: List[TEffectItem]


class ParticleItemSection(ServerItemSectionTyped):
    itemType: Literal["particle"]
    items: List[TParticleItem]


class EngineItemSection(ServerItemSectionTyped):
    itemType: Literal["engine"]
    items: List[TEngineItem]


class ReplayItemSection(ServerItemSectionTyped):
    itemType: Literal["replay"]
    items: List[TReplayItem]


class RoomItemSection(ServerItemSectionTyped):
    itemType: Literal["room"]
    items: List[TRoomItem]


ServerItemSection = Union[
    PostItemSection,
    PlaylistItemSection,
    LevelItemSection,
    SkinItemSection,
    BackgroundItemSection,
    EffectItemSection,
    ParticleItemSection,
    EngineItemSection,
    ReplayItemSection,
    RoomItemSection,
]


class ServerItemLeaderboard(TypedDict):
    name: str
    title: Union[str, Text]
    description: Optional[str]


class ServerItemDetails(TypedDict):
    item: T
    description: Optional[str]
    actions: List[ServerForm]
    hasCommunity: bool
    leaderboards: List[ServerItemLeaderboard]
    sections: List[ServerItemSection]


class ServerItemInfo(TypedDict):
    creates: Optional[List[ServerForm]]
    searches: Optional[List[ServerForm]]
    sections: List[ServerItemSection]
    banner: Optional[SRL]


# endregion


class GameplayResult(TypedDict):
    grade: Grade
    arcadeScore: int
    accuracyScore: int
    combo: int
    perfect: int
    great: int
    good: int
    miss: int
    totalCount: int
