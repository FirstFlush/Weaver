from dataclasses import dataclass, field

@dataclass
class PageConfigOptions:
    
    viewport: tuple[int, int] # width, height
    window_history: int = field(default=10)
    languages: list[str] = field(default=[ "en-US", "en" ])
    language: str = field(default="en-US")
    platform: str = field(default="Win32")
    webdriver: bool = False