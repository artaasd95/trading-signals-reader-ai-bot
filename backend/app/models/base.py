#!/usr/bin/env python3
"""
Base Model Module

Contains the base SQLAlchemy model class with common fields and functionality.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.sql import func


@as_declarative()
class Base:
    """
    Base class for all database models.
    
    Provides common fields and functionality:
    - UUID primary key
    - Created and updated timestamps
    - Table name generation
    """
    
    id: Any
    __name__: str
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Common fields for all models
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique identifier for the record"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the record was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp when the record was last updated"
    )
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self) -> dict:
        """Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, uuid.UUID):
                value = str(value)
            result[column.name] = value
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "Base":
        """Create model instance from dictionary."""
        # Filter out keys that don't correspond to model columns
        valid_keys = {column.name for column in cls.__table__.columns}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)