"""Pydantic data contracts for rental listing input and extraction."""

import re
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LaundryType(str, Enum):
    IN_UNIT = "IN_UNIT"
    IN_BUILDING = "IN_BUILDING"
    HOOKUPS = "HOOKUPS"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"


class ParkingType(str, Enum):
    GARAGE = "GARAGE"
    DRIVEWAY = "DRIVEWAY"
    DEDICATED_SURFACE = "DEDICATED_SURFACE"
    STREET = "STREET"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"


class RawListingInput(BaseModel):
    """Unprocessed listing content and its source."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source_url: str = Field(min_length=1, description="Original listing URL")
    source_platform: str = Field(
        min_length=1,
        description="Origin platform, such as Zillow or Apartments.com",
    )
    raw_text: str = Field(
        min_length=1,
        description="Unstructured rental listing text",
    )


class ParsedRentalListing(BaseModel):
    """Validated, structured facts extracted from a rental listing."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, description="Clean listing title")
    address: Optional[str] = Field(
        default=None,
        description="Street address, if available",
    )
    city: Optional[str] = Field(default=None, description="City name")
    state: Optional[str] = Field(
        default=None,
        pattern=r"^[A-Z]{2}$",
        description="Two-letter state code",
    )
    zip_code: Optional[str] = Field(
        default=None,
        pattern=r"^\d{5}$",
        description="Five-digit US ZIP code",
    )
    price_monthly: float = Field(
        gt=0,
        description="Monthly rental price in USD",
    )
    bedrooms: int = Field(ge=0, description="Number of bedrooms")
    bathrooms: float = Field(gt=0, description="Number of bathrooms")
    square_feet: Optional[int] = Field(
        default=None,
        gt=0,
        description="Interior square footage, if listed",
    )
    dogs_allowed: bool = Field(
        description="Whether dogs are explicitly allowed",
    )
    dog_restrictions: Optional[str] = Field(
        default=None,
        description="Notes on dog restrictions",
    )
    has_fenced_yard: bool = Field(
        default=False,
        description="Whether the property has a private fenced yard",
    )
    laundry: LaundryType = Field(
        default=LaundryType.UNKNOWN,
        description="Laundry facilities available",
    )
    parking: ParkingType = Field(
        default=ParkingType.UNKNOWN,
        description="Primary parking configuration",
    )
    llm_summary: str = Field(
        min_length=1,
        description="Concise summary of property highlights",
    )
    llm_pros: list[str] = Field(
        default_factory=list,
        description="Positive features extracted from the listing",
    )
    llm_cons_and_red_flags: list[str] = Field(
        default_factory=list,
        description="Potential concerns, extra costs, or red flags",
    )

    @field_validator("price_monthly", mode="before")
    @classmethod
    def parse_monthly_price(cls, value: object) -> object:
        if not isinstance(value, str):
            return value

        normalized = value.strip().lower()
        normalized = re.sub(r"\s*(/month|/mo|monthly|per month)$", "", normalized)
        normalized = normalized.strip()
        if not re.fullmatch(
            r"\$?\s*(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d{1,2})?",
            normalized,
        ):
            raise ValueError("price_monthly must be a numeric amount")
        normalized = normalized.replace("$", "").replace(",", "").strip()
        try:
            return Decimal(normalized)
        except InvalidOperation as error:
            raise ValueError("price_monthly must be a numeric amount") from error

    @field_validator("bathrooms", mode="before")
    @classmethod
    def parse_bathrooms(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().removesuffix("+")
            try:
                return float(normalized)
            except ValueError as error:
                raise ValueError("bathrooms must be a numeric amount") from error
        return value

    @field_validator("state", mode="before")
    @classmethod
    def normalize_state(cls, value: object) -> object:
        return value.strip().upper() if isinstance(value, str) else value
