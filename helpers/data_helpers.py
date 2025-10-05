from typing import Union, List, Optional

from helpers.sonolus_typings import Text, ItemType, Icon
from helpers.datastructs import (
    ServerItemSection,
    ServerItem,
    ServerForm,
    ServerOption,
    ServerCollectionItemOption,
    ServerFileOption,
    ServerMultiOption,
    ServerSelectOption,
    ServerSliderOption,
    ServerServerItemsOption,
    ServerServerItemOption,
    ServerTextAreaOption,
    ServerTextOption,
    ServerToggleOption,
    SIL,
)


def create_section(
    title: Union[Text, str],
    item_type: ItemType,
    items: List[ServerItem],
    description: Optional[str] = None,
    icon: Optional[Union[Icon, str]] = None,
    search: Optional[ServerForm] = None,
    search_values: Optional[str] = None,
    help: Optional[str] = None,
) -> ServerItemSection:
    section_dict = {
        "title": title,
        "itemType": item_type.removesuffix("s"),
        "items": items,
    }

    if description:
        section_dict["description"] = description

    if icon:
        section_dict["icon"] = icon

    if search:
        section_dict["search"] = search

    if search_values:
        section_dict["searchValues"] = search_values

    if help:
        section_dict["help"] = help

    return section_dict


def create_server_form(
    type: str,
    title: Union[Text, str],
    require_confirmation: bool,
    options: List[ServerOption],
    description: Optional[str] = None,
    icon: Optional[Union[Icon, str]] = None,
    help: Optional[str] = None,
) -> ServerForm:
    server_form_dict = {
        "type": type,
        "title": title,
        "requireConfirmation": require_confirmation,
        "options": options,
    }

    if description:
        server_form_dict["description"] = description
    if icon:
        server_form_dict["icon"] = icon
    if help:
        server_form_dict["help"] = help

    return server_form_dict


class ServerFormOptionsFactory:
    @staticmethod
    def server_text_option(
        query: str,
        name: Union[Text, str],
        required: bool,
        default: str,
        placeholder: Union[Text, str],
        limit: int,
        shortcuts: List[str],
        description: Optional[str] = None,
    ) -> ServerTextOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "text",
            "def": default,
            "placeholder": placeholder,
            "limit": limit,
            "shortcuts": shortcuts,
        }
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_text_area_option(
        query: str,
        name: Union[Text, str],
        required: bool,
        default: str,
        placeholder: Union[Text, str],
        limit: int,
        shortcuts: List[str],
        description: Optional[str] = None,
    ) -> ServerTextAreaOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "textArea",
            "def": default,
            "placeholder": placeholder,
            "limit": limit,
            "shortcuts": shortcuts,
        }
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_slider_option(
        query: str,
        name: Union[Text, str],
        required: bool,
        default: int,
        min_value: int,
        max_value: int,
        step: int,
        unit: Optional[Union[Text, str]] = None,
        description: Optional[str] = None,
    ) -> ServerSliderOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "slider",
            "def": default,
            "min": min_value,
            "max": max_value,
            "step": step,
        }
        if unit:
            option["unit"] = unit
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_toggle_option(
        query: str,
        name: Union[Text, str],
        required: bool,
        default: bool,
        description: Optional[str] = None,
    ) -> ServerToggleOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "toggle",
            "def": default,
        }
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_select_option(
        query: str,
        name: Union[Text, str],
        required: bool,
        default: str,
        values: List[dict],  # [{"name": str, "title": Text | str}]
        description: Optional[str] = None,
    ) -> ServerSelectOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "select",
            "def": default,
            "values": values,
        }
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_multi_option(
        query: str,
        name: Union[Text, str],
        required: bool,
        default: List[bool],
        values: List[dict],  # [{"name": str, "title": Text | str}]
        description: Optional[str] = None,
    ) -> ServerMultiOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "multi",
            "def": default,
            "values": values,
        }
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_server_item_option(
        query: str,
        name: Union[Text, str],
        required: bool,
        item_type: ItemType,
        allow_other_servers: bool,
        default: Optional[SIL] = None,
        description: Optional[str] = None,
    ) -> ServerServerItemOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "serverItem",
            "itemType": item_type,
            "allowOtherServers": allow_other_servers,
        }
        if default is not None:
            option["def"] = default
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_server_items_option(
        query: str,
        name: Union[Text, str],
        required: bool,
        item_type: ItemType,
        allow_other_servers: bool,
        limit: int,
        default: List[SIL] = None,
        description: Optional[str] = None,
    ) -> ServerServerItemsOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "serverItems",
            "itemType": item_type,
            "allowOtherServers": allow_other_servers,
            "limit": limit,
        }
        if default is not None:
            option["def"] = default
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_collection_item_option(
        query: str,
        name: Union[Text, str],
        required: bool,
        item_type: ItemType,
        description: Optional[str] = None,
    ) -> ServerCollectionItemOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "collectionItem",
            "itemType": item_type,
        }
        if description:
            option["description"] = description
        return option

    @staticmethod
    def server_file_option(
        query: str,
        name: Union[Text, str],
        required: bool,
        default: str,
        description: Optional[str] = None,
    ) -> ServerFileOption:
        option = {
            "query": query,
            "name": name,
            "required": required,
            "type": "file",
            "def": default,
        }
        if description:
            option["description"] = description
        return option
