from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

class Base(AsyncAttrs, DeclarativeBase):
    pass


# Информация о чатах
class Chat(Base):
    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    username: Mapped[str]
    status: Mapped[bool] = mapped_column(default=False)
    work_mode: Mapped[str] = mapped_column(default='Не выбран')
    activity_interval_hours: Mapped[int] = mapped_column(default=2)  # Интервал активности в часах
    dialog_chance: Mapped[int] = mapped_column(default=50)
    question_chance: Mapped[int] = mapped_column(default=50)

    def format_info(self) -> str:
        """Возвращает отформатированную информацию о чате в виде строки"""
        status_icon = "🟢" if self.status else "🔴"

        return (
            f"{self.title} (@{self.username})\n"
            f"Статус: {status_icon} | Режим: {self.work_mode} | Интервал: {self.activity_interval_hours} час."
        )