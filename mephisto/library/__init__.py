from creart import it
from launart import Launart

from mephisto.library.service import MephistoService, SessionService


def launch():
    mgr = it(Launart)
    mgr.add_component(SessionService())
    mgr.add_component(MephistoService())
    mgr.launch_blocking()
