from dataclasses import dataclass
from typing import Any, List, Optional, Tuple


@dataclass
class Collection():
    collection: str
    fields: Any = ()
    translation: Any = ()
    note: Optional[str] = ''
    hidden: Optional[int] = 0
    single: Optional[int] = 0
    managed: Optional[int] = 0
    icon: Optional[str] = ''
