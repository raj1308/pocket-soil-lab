from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SoilSample(Base):
    __tablename__ = "soil_samples"

    id: Mapped[int] = mapped_column(primary_key=True)
    farm_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    sampling_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sampling_depth_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    farm_area_ha: Mapped[float | None] = mapped_column(Float, nullable=True)
    crop_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    irrigation_availability: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(30), default="manually_entered")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    measurements: Mapped[list["SoilMeasurement"]] = relationship(
        back_populates="sample", cascade="all, delete-orphan"
    )


class SoilMeasurement(Base):
    __tablename__ = "soil_measurements"

    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[int] = mapped_column(ForeignKey("soil_samples.id"))
    property: Mapped[str] = mapped_column(String(50))
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(30))
    method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_type: Mapped[str] = mapped_column(String(30))
    uncertainty: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reliability: Mapped[str] = mapped_column(String(30), default="standard")
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    sample: Mapped["SoilSample"] = relationship(back_populates="measurements")
