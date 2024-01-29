import kayaku
from creart import it
from launart import Launart


def launch():
    kayaku.initialize({"{**}": "./config/{**}"})

    from mephisto.library.model.config import MephistoConfig
    from mephisto.library.service import (
        ConfigService,
        MephistoService,
        ProtocolService,
        SessionService,
    )

    kayaku.create(MephistoConfig)

    mgr = it(Launart)
    mgr.add_component(ConfigService())
    mgr.add_component(ProtocolService())
    mgr.add_component(SessionService())
    mgr.add_component(MephistoService())
    mgr.launch_blocking()
