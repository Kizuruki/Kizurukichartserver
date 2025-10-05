from typing import List, Any


def list_to_pages(data: List[Any], items_per_page: int) -> List[List[Any]]:
    return [data[i : i + items_per_page] for i in range(0, len(data), items_per_page)]
