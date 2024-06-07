from pydantic import BaseModel


class CommandHandler(BaseModel):
    handler: str
    description: str | None = None


_handlers: dict[str, list[CommandHandler]] = {}


def _is_duplicate(handler: CommandHandler):
    return bool(
        [h for hs in _handlers.values() for h in hs if h.handler == handler.handler]
    )


def register_handler(scope: str, *handlers: CommandHandler):
    for handler in handlers:
        if _is_duplicate(handler):
            raise ValueError(f"Duplicate handler: {handler.handler}")
    if scope not in _handlers:
        _handlers[scope] = []
    _handlers[scope].extend(handlers)


def get_handler(
    *, scope: str | None = None, handler: str | None = None
) -> list[CommandHandler]:
    if scope is not None:
        return _handlers.get(scope, [])
    if handler is not None:
        return [h for hs in _handlers.values() for h in hs if h.handler == handler]
    return [h for hs in _handlers.values() for h in hs]


def remove_handler(scope: str, handler: str):
    handlers = _handlers.get(scope, [])
    _handlers[scope] = [h for h in handlers if h.handler != handler]


def remove_scope(scope: str):
    _handlers.pop(scope, None)
