import contextlib
import kayaku
from creart import it
from launart import Launart


def launch():
    kayaku.initialize({"{**}": "./config/{**}"})

    from mephisto.library.model.config import MephistoConfig
    from mephisto.library.service import (
        DataService,
        MephistoService,
        MessageCacheService,
        ModuleService,
        ProtocolService,
        SessionService,
        StandardService,
        UvicornService,
    )

    kayaku.create(MephistoConfig)

    mgr = it(Launart)
    mgr.add_component(MessageCacheService())
    mgr.add_component(DataService())
    mgr.add_component(ModuleService())
    mgr.add_component(ProtocolService())
    mgr.add_component(SessionService())
    mgr.add_component(StandardService())
    mgr.add_component(MephistoService())
    mgr.add_component(UvicornService())

    # Optional components
    with contextlib.suppress(ImportError):
        from graiax.playwright import PlaywrightService

        mgr.add_component(PlaywrightService())

    mgr.launch_blocking()
