import json
import os
from pathlib import Path
from typing import Final

from avilla.console.protocol import ConsoleProtocol
from avilla.core import BaseProtocol
from launart import Launart, Service
from loguru import logger

from mephisto.library.model.protocol import ProtocolConfig
from mephisto.library.service import MephistoService
from mephisto.shared import MEPHISTO_ROOT

_PROTOCOL_CREDENTIAL_PATH: Final[Path] = Path(
    MEPHISTO_ROOT, "config", "library", "credentials"
)


class ProtocolService(Service):
    id = "mephisto.service/protocol"

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing"}

    def _check_console(self):
        if os.environ.get("MEPHISTO_NO_CONSOLE") != "1":
            self.apply_protocols(ConsoleProtocol())
        else:
            logger.warning("[ProtocolService] Console protocol disabled")

    def apply_protocols(self, *protocols: BaseProtocol):
        self.manager.get_component(MephistoService).avilla.apply_protocols(*protocols)

    def _load_protocols(self):
        configs: list[ProtocolConfig] = []
        for file in _PROTOCOL_CREDENTIAL_PATH.rglob("*.json"):
            with file.open("r") as f:
                configs.append(ProtocolConfig.resolve(json.load(f)))
        if not configs:
            return
        logger.success(f"[ProtocolService] Loaded {len(configs)} registered protocols")
        self.apply_protocols(*(config.to_protocol() for config in configs))

    def register_protocol(self, config: ProtocolConfig):
        protocol_dir = _PROTOCOL_CREDENTIAL_PATH / config.protocol
        if not protocol_dir.exists():
            protocol_dir.mkdir(parents=True)
        with (protocol_dir / f"{config.id}.json").open("w") as f:
            f.write(config.model_dump_json(indent=4))
        self.apply_protocols(config.to_protocol())

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            self._check_console()
            self._load_protocols()
