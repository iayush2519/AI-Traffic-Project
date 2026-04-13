"""
SQLAlchemy Database Models (ORM)
"""
from datetime import datetime
from sqlalchemy import (Column, Integer, Float, String, DateTime,
                        Boolean, Text, Index)
from app.database import Base


class TrafficReading(Base):
    __tablename__ = "traffic_readings"

    id              = Column(Integer, primary_key=True, index=True)
    timestamp       = Column(DateTime, default=datetime.utcnow, index=True)
    intersection_id = Column(String(20), index=True)
    road_segment_id = Column(String(20))
    lat             = Column(Float)
    lon             = Column(Float)
    road_class      = Column(String(20))
    vehicle_count   = Column(Integer)
    average_speed   = Column(Float)
    occupancy       = Column(Float)
    flow            = Column(Float)
    queue_length    = Column(Float)
    waiting_time    = Column(Float)
    traffic_density = Column(Float)
    weather_condition = Column(String(20))
    day_of_week     = Column(Integer)
    hour_of_day     = Column(Integer)
    is_weekend      = Column(Boolean)
    congestion_label  = Column(String(10))
    congestion_score  = Column(Float)

    __table_args__ = (
        Index("ix_tr_ts_int", "timestamp", "intersection_id"),
    )


class CongestionPrediction(Base):
    __tablename__ = "congestion_predictions"

    id              = Column(Integer, primary_key=True, index=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    intersection_id = Column(String(20), index=True)
    model_name      = Column(String(20))  # xgboost | lstm
    horizon         = Column(String(10))  # 5min | 15min | 30min
    predicted_class = Column(String(10))
    predicted_score = Column(Float)
    confidence      = Column(Float)


class SignalTiming(Base):
    __tablename__ = "signal_timings"

    id              = Column(Integer, primary_key=True, index=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    intersection_id = Column(String(20), index=True)
    phase_ns_green  = Column(Integer)   # North-South green seconds
    phase_ew_green  = Column(Integer)   # East-West green seconds
    yellow_time     = Column(Integer, default=3)
    cycle_time      = Column(Integer)
    mode            = Column(String(20))  # adaptive | fixed | emergency
    reason          = Column(Text)


class ModelTrainingRun(Base):
    __tablename__ = "model_training_runs"

    id          = Column(Integer, primary_key=True, index=True)
    started_at  = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    status      = Column(String(20), default="running")  # running|done|failed
    model_type  = Column(String(20))
    metrics_json = Column(Text, nullable=True)
    error_msg   = Column(Text, nullable=True)
