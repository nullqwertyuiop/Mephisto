from dataclasses import dataclass, field

from kayaku import config


@dataclass
class MephistoNetworkConfig:
    proxy: str = ""
    timeout: int = 30


@dataclass
class MephistoAdvancedConfig:
    debug: bool = False
    log_rotate: int = 7
    message_cache_size: int = 5000


@config("library.main")
class MephistoConfig:
    name: str = "Mephisto"
    description: str = "Yet another bot"
    network: MephistoNetworkConfig = field(default_factory=MephistoNetworkConfig)
    advanced: MephistoAdvancedConfig = field(default_factory=MephistoAdvancedConfig)
