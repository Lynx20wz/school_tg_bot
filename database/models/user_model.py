# pyright: reportUndefinedVariable=false
from typing import Annotated

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

d0 = Annotated[bool, mapped_column(Boolean(), server_default='FALSE')]


class UserModel(Base):
    __tablename__ = 'users'

    userid: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]

    debug: Mapped[d0]
    setting_dw: Mapped[d0]
    setting_notification: Mapped[d0]
    setting_hide_link: Mapped[d0]

    token: Mapped[str]
    student_id: Mapped[int]
    homework_id: Mapped[int | None] = mapped_column(ForeignKey('homework_week.id'))

    homework: Mapped['HomeworkWeekModel'] = relationship(back_populates='users')
