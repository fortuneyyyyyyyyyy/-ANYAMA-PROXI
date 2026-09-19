from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column


db = SQLAlchemy()


class Artisan(db.Model):
    __tablename__ = "artisans"
    __table_args__ = (
        CheckConstraint("length(name) BETWEEN 2 AND 80", name="ck_artisan_name_length"),
        CheckConstraint("length(job) BETWEEN 2 AND 60", name="ck_artisan_job_length"),
        CheckConstraint("length(neighborhood) BETWEEN 2 AND 80", name="ck_artisan_neighborhood_length"),
        CheckConstraint("length(phone) BETWEEN 8 AND 32", name="ck_artisan_phone_length"),
        Index("ix_artisans_job", "job"),
        Index("ix_artisans_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    job: Mapped[str] = mapped_column(String(60), nullable=False)
    neighborhood: Mapped[str] = mapped_column(String(80), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "job": self.job,
            "neighborhood": self.neighborhood,
            "phone": self.phone,
        }
