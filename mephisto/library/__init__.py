import kayaku
from creart import it
from graiax.playwright import PlaywrightService
from launart import Launart


def launch():
    kayaku.initialize({"{**}": "./config/{**}"})

    from mephisto.library.model.config import MephistoConfig
    from mephisto.library.service import (
        ConfigService,
        MephistoService,
        ModuleService,
        ProtocolService,
        SessionService,
        StandardService,
    )

    kayaku.create(MephistoConfig)

    mgr = it(Launart)
    mgr.add_component(ConfigService())
    mgr.add_component(ModuleService())
    mgr.add_component(ProtocolService())
    mgr.add_component(SessionService())
    mgr.add_component(StandardService())
    mgr.add_component(MephistoService())
    mgr.add_component(PlaywrightService())
    mgr.launch_blocking()
