from typing import TYPE_CHECKING, Annotated

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from database import HomeworkWeekModel

d0 = Annotated[bool, mapped_column(Boolean(), server_default='FALSE')]


class User(MappedAsDataclass, Base):
    __tablename__ = 'users'

    userid: Mapped[int] = mapped_column(primary_key=True)

    # settings contains flags for user settings
    # bit 0: dw
    # bit 1: notifications
    # bit 2: hide_link
    # bit 3: debug
    # bit 4: reserved
    _settings: Mapped[int] = mapped_column('settings', default=0b00110)

    token: Mapped[str | None] = mapped_column(default=None)
    student_id: Mapped[int | None] = mapped_column(default=None)
    homework_id: Mapped[int | None] = mapped_column(ForeignKey('homework_week.id'), default=None)

    homework: Mapped[HomeworkWeekModel] = relationship(back_populates='users', init=False)

    @property
    def setting_dw(self) -> bool:
        return self._settings & 0b00001 != 0

    @property
    def setting_notifications(self) -> bool:
        return self._settings & 0b00010 != 0

    @property
    def setting_hide_link(self) -> bool:
        return self._settings & 0b00100 != 0

    @property
    def debug(self) -> bool:
        return self._settings & 0b01000 != 0

    @property
    def parser(self):
        from bot.classes import Parser

        return Parser(self)
