class RequirementResolveFailed(Exception):
    pass


class MessageRecordNotFound(Exception):
    pass


class AttachmentRecordNotFound(Exception):
    pass


class MessageDeserializationFailed(Exception):
    _TEXT_PATTERN = "Failed to deserialize {element} ({raw_type}) Element: {raw}"

    def __init__(
        self, raw: str, *, element: str | None = None, raw_type: str | None = None
    ):
        self.element = element
        self.raw_type = raw_type
        self.raw = raw
        self.text = self._TEXT_PATTERN.format(
            element="Unparsed" if element is None else element,
            raw_type="unknown" if raw_type is None else raw_type,
            raw=raw,
        )
        super().__init__(self.text)
