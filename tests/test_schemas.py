import pytest
from pydantic import ValidationError

from app.schemas import (
    LaundryType,
    ParsedRentalListing,
    ParkingType,
    RawListingInput,
)


def valid_listing_data() -> dict[str, object]:
    return {
        "title": "Sunny rental",
        "state": "wa",
        "zip_code": "98101",
        "price_monthly": "$2,500/mo",
        "bedrooms": 2,
        "bathrooms": "2+",
        "dogs_allowed": True,
        "llm_summary": "Bright two-bedroom home near transit.",
    }


def test_raw_listing_input_requires_nonblank_source_and_text() -> None:
    listing = RawListingInput(
        source_url=" https://example.com/listing ",
        source_platform=" Zillow ",
        raw_text="  Two-bedroom home  ",
    )

    assert listing.source_url == "https://example.com/listing"
    assert listing.raw_text == "Two-bedroom home"
    with pytest.raises(ValidationError):
        RawListingInput(
            source_url=" ",
            source_platform="Zillow",
            raw_text="Two-bedroom home",
        )


def test_parsed_listing_normalizes_fields_and_uses_enum_defaults() -> None:
    listing = ParsedRentalListing.model_validate(valid_listing_data())

    assert listing.state == "WA"
    assert listing.price_monthly == 2500.0
    assert listing.bathrooms == 2.0
    assert listing.laundry is LaundryType.UNKNOWN
    assert listing.parking is ParkingType.UNKNOWN
    assert listing.llm_pros == []


def test_parsed_listing_accepts_enum_values() -> None:
    data = valid_listing_data()
    data["laundry"] = "IN_UNIT"
    data["parking"] = "GARAGE"

    listing = ParsedRentalListing.model_validate(data)

    assert listing.laundry is LaundryType.IN_UNIT
    assert listing.parking is ParkingType.GARAGE


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("price_monthly", "$2,5x0/mo"),
        ("price_monthly", "$25,00/mo"),
        ("price_monthly", 0),
        ("bedrooms", -1),
        ("bathrooms", 0),
        ("state", "Washington"),
        ("zip_code", "9810"),
        ("laundry", "WASHER_DRYER"),
        ("unexpected", "not part of the contract"),
    ],
)
def test_parsed_listing_rejects_invalid_contract_values(
    field: str,
    value: object,
) -> None:
    data = valid_listing_data()
    data[field] = value

    with pytest.raises(ValidationError):
        ParsedRentalListing.model_validate(data)
