from sqlalchemy import String, DateTime, Text, Integer, Column, Boolean

from mephisto.library.util.orm.base import Base


class RecordTable(Base):
    __tablename__ = "record"

    id = Column(Integer(), primary_key=True)
    message_id = Column(String(length=64))

    scene = Column(String(length=64))
    client = Column(String(length=64), nullable=True)
    selector = Column(String(length=256))

    time = Column(DateTime(timezone=True), nullable=True)
    content = Column(Text(), nullable=True)
    attachments = Column(Text(), nullable=True)
    reply_to = Column(String(length=256), nullable=True)

    deleted = Column(Boolean(), default=False)
    delete_time = Column(DateTime(timezone=True), nullable=True)

    edited = Column(Boolean(), default=False)
    edit_time = Column(DateTime(timezone=True), nullable=True)


class AttachmentTable(Base):
    __tablename__ = "attachment"

    id = Column(Integer(), primary_key=True)
    pattern = Column(String(length=256))
    file_path = Column(Text())

    deleted = Column(Boolean(), default=False)
    delete_time = Column(DateTime(timezone=True), nullable=True)


class ConfigTable(Base):
    __tablename__ = "config"

    id = Column(Integer(), primary_key=True)
    key = Column(String(length=64))
    value = Column(Text())

    effective = Column(Boolean(), default=True)
    edit_time = Column(DateTime(timezone=True), nullable=True)


class StatisticsTable(Base):
    __tablename__ = "statistics"

    id = Column(Integer(), primary_key=True)
    scene = Column(String(length=64))
    client = Column(String(length=64))

    key = Column(String(length=64))
    value = Column(Integer())

    deleted = Column(Boolean(), default=False)
    delete_time = Column(DateTime(timezone=True), nullable=True)
