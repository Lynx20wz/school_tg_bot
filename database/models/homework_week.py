from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from database import StudyDayModel, UserModel


class HomeworkWeekModel(Base):
    __tablename__ = 'homework_week'

    id: Mapped[int] = mapped_column(primary_key=True)
    begin: Mapped[str]
    end: Mapped[str]
    timestamp: Mapped[str]

    users: Mapped[list[UserModel]] = relationship(back_populates='homework')
    study_days: Mapped[list[StudyDayModel]] = relationship(
        back_populates='homework', cascade='all, delete-orphan'
    )
