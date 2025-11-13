# pyright: reportUndefinedVariable=false
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class StudyDayModel(Base):
    __tablename__ = 'study_days'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    homework_id: Mapped[int] = mapped_column(ForeignKey('homework_week.id', ondelete='CASCADE'))
    name: Mapped[str]
    date: Mapped[str]

    homework: Mapped['HomeworkWeekModel'] = relationship(back_populates='study_days')
    lessons: Mapped[list['LessonModel']] = relationship(
        back_populates='study_day', cascade='all, delete-orphan'
    )
