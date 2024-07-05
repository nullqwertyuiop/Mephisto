from typing import cast

from creart import it
from fastapi import FastAPI
from graia.amnesia.builtins.asgi import UvicornASGIService
from graia.amnesia.builtins.asgi.asgitypes import ASGI3Application
from graia.saya import Saya
from graiax.fastapi import FastAPIService, FastAPIBehaviour
from kayaku import create
from launart import Launart, Service
from launart.status import Phase
from starlette.middleware.cors import CORSMiddleware

from mephisto.library.model.config import MephistoConfig


class UvicornService(Service):
    id = "mephisto.service/uvicorn"
    fastapi: FastAPI

    def __init__(self):
        self.fastapi = FastAPI()
        super().__init__()

        it(Saya).install_behaviours(FastAPIBehaviour(self.fastapi))
        self.fastapi.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        manager = it(Launart)
        manager.add_component(
            UvicornASGIService(
                "127.0.0.1",
                create(MephistoConfig).advanced.uvicorn_port,
                {"": cast(ASGI3Application, self.fastapi)},
            )
        )
        manager.add_component(FastAPIService(self.fastapi))

    @property
    def required(self) -> set[str]:
        return {"mephisto.service/data"}

    @property
    def stages(self) -> set[Phase]:
        return set()

    async def launch(self, manager: Launart):
        pass
