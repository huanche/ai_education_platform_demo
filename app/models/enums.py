"""Enumerations used by database models."""

from enum import StrEnum


class UserRole(StrEnum):
    """Supported roles in the education demo."""

    TEACHER = "teacher"
    STUDENT = "student"
