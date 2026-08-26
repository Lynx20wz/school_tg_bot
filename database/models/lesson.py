from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from database import StudyDayModel


class LessonModel(Base):
    __tablename__ = 'lessons'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    study_day_id: Mapped[int] = mapped_column(ForeignKey('study_days.id', ondelete='CASCADE'))
    name: Mapped[str]
    homework: Mapped[str | None]
    links: Mapped[str | None]

    study_day: Mapped[StudyDayModel] = relationship(back_populates='lessons')
