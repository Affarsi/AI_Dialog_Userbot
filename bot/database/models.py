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
    status: Mapped[bool]
    work_mode: Mapped[str]
    activity_interval_minutes: Mapped[int]  # Интервал активности в минутах

    def format_info(self) -> str:
        """Возвращает отформатированную информацию о чате в виде строки"""
        status_icon = "🟢" if self.status else "🔴"
        hours = self.activity_interval_minutes // 60
        minutes = self.activity_interval_minutes % 60
        interval_str = f"{hours} час." if hours else f"{minutes} мин."

        return (
            f"{self.title} (@{self.username})\n"
            f"Статус: {status_icon} | Режим: {self.work_mode} | Интервал: {interval_str}"
        )