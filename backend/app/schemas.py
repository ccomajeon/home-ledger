from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class ApiMessage(BaseModel):
    message: str


class AuthConfig(BaseModel):
    google_enabled: bool
    local_admin_enabled: bool


class LocalLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: SecretStr


class AccountPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: str
    enabled: bool
    created_at: datetime


class AccountCreate(BaseModel):
    email: str
    role: Literal["USER", "OWNER"] = "USER"


class AccountUpdate(BaseModel):
    role: Literal["USER", "OWNER"] | None = None
    enabled: bool | None = None


class NamedItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class NamedItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    enabled: bool | None = None


class NamedItemPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    enabled: bool


class TransactionCreate(BaseModel):
    tx_date: date
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    tx_type: Literal["INCOME", "EXPENSE"]
    description: str = Field(default="", max_length=500)
    category_id: int
    payment_method_id: int


class TransactionUpdate(BaseModel):
    tx_date: date | None = None
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    tx_type: Literal["INCOME", "EXPENSE"] | None = None
    description: str | None = Field(default=None, max_length=500)
    category_id: int | None = None
    payment_method_id: int | None = None


class TransactionPublic(BaseModel):
    id: int
    tx_date: date
    amount: Decimal
    tx_type: str
    description: str
    category_id: int
    category_name: str
    payment_method_id: int
    payment_method_name: str
    created_at: datetime


class TransactionSummary(BaseModel):
    income: Decimal
    expense: Decimal
    balance: Decimal


class BackupPublic(BaseModel):
    name: str
    size: int
    created_at: datetime


class RestoreRequest(BaseModel):
    name: str


class AuditLogPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_email: str
    action: str
    payload: str
    created_at: datetime
