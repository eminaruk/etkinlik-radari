from dataclasses import asdict, dataclass, field


@dataclass
class Event:
    source: str
    key: str                    # stable id within the source
    title: str
    url: str
    start: str | None           # 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SSZ'
    end: str | None = None
    description: str = ""
    city: str = ""
    country: str = ""
    venue: str = ""
    online: bool = False
    image: str = ""
    is_free: bool | None = None
    organizer: str = ""
    guest_count: int | None = None
    tags: list = field(default_factory=list)   # raw tags from the source
    kind_hint: str = ""                         # source's own idea of the event type
    importance: int = 40                        # 0-100 baseline set by the source
    extra: dict = field(default_factory=dict)

    @property
    def id(self) -> str:
        return f"{self.source}:{self.key}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["id"] = self.id
        return d


@dataclass
class NewsItem:
    source: str
    title: str
    url: str
    published: str | None
    summary: str = ""
    image: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["id"] = f"{self.source}:{self.url}"
        return d
