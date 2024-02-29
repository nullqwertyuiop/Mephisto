from enum import Enum


class LandType(str, Enum):
    """Land 类型枚举"""

    # TODO: deprecate LandType

    QQ = "qq"
    TELEGRAM = "telegram"
    CONSOLE = "console"
