from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from database import StudyDayModel, User


class HomeworkWeekModel(Base):
    __tablename__ = 'homework_week'

    id: Mapped[int] = mapped_column(primary_key=True)
    begin: Mapped[str]
    end: Mapped[str]
    timestamp: Mapped[str]

    users: Mapped[list[User]] = relationship(back_populates='homework')
    study_days: Mapped[list[StudyDayModel]] = relationship(
        back_populates='homework', cascade='all, delete-orphan'
    )
