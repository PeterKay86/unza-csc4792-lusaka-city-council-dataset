from pathlib import Path
import csv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "data" / "cleaned" / "cdf"

OUTPUT_FILE = (
    OUTPUT_DIR
    / "db-unza26-csc4792-lusaka_city_council_cdf_allocations.csv"
)

DATE_ACCESSED = "2026-09-14"
ALL_CONSTITUENCIES = "All seven Lusaka constituencies"

BUDGET_2024_TITLE = "Lusaka City Council 2024 Budget"
BUDGET_2024_URL = (
    "https://www.lcc.gov.zm/wp-content/uploads/2025/04/"
    "LUSAKA-CITY-COUNCIL-2024-BUDGET.pdf"
)

BUDGET_2025_TITLE = (
    "Lusaka City Council Approved 2025 Budget - Yellow Book"
)
BUDGET_2025_URL = (
    "https://www.lcc.gov.zm/wp-content/uploads/2025/04/"
    "LUSAKA-CITY-COUNCIL-APPROVED-2025-BUDGET-YELLOW-BOOK.pdf"
)

BUDGET_2026_TITLE = "Lusaka City Council 2026 Yellow Book"
BUDGET_2026_URL = "https://www.lcc.gov.zm/publications/"

FINANCIAL_STATEMENT_TITLE = (
    "Lusaka City Council 2024 Financial Statement"
)
FINANCIAL_STATEMENT_URL = (
    "https://www.lcc.gov.zm/wp-content/uploads/2025/11/"
    "Lusaka-City-Council-2024-Financial-statement-.pdf"
)


FIELDS = [
    "record_id",
    "financial_year",
    "constituency",
    "allocation_category",
    "approved_allocation_zmw",
    "amount_disbursed_zmw",
    "amount_spent_zmw",
    "unspent_balance_zmw",
    "source_title",
    "source_url",
    "date_accessed",
    "notes",
]


BUDGET_ALLOCATIONS = {
    2024: {
        "source_title": BUDGET_2024_TITLE,
        "source_url": BUDGET_2024_URL,
        "total": 214_449_494,
        "categories": {
            "Community Projects": 122_236_211,
            "Women and Youth Empowerment": 40_745_404,
            "CDF Administration": 10_722_475,
            (
                "Secondary School and Skills Development "
                "Bursaries"
            ): 40_745_404,
        },
    },
    2025: {
        "source_title": BUDGET_2025_TITLE,
        "source_url": BUDGET_2025_URL,
        "total": 252_407_054,
        "categories": {
            "Community Projects": 153_738_842,
            "Women and Youth Empowerment": 43_597_582,
            "CDF Administration": 11_473_048,
            (
                "Secondary School and Skills Development "
                "Bursaries"
            ): 43_597_582,
        },
    },
    2026: {
        "source_title": BUDGET_2026_TITLE,
        "source_url": BUDGET_2026_URL,
        "total": 280_227_850,
        "categories": {
            "Community Projects": 170_465_541,
            "Women and Youth Empowerment": 48_499_625,
            "CDF Administration": 12_763_059,
            (
                "Secondary School and Skills Development "
                "Bursaries"
            ): 48_499_625,
        },
    },
}


FUNDING_RECEIPTS = [
    {
        "financial_year": 2024,
        "allocation_category": "CDF funding received",
        "amount_disbursed_zmw": 53_781_268,
        "notes": (
            "Council-reported CDF funding receipt for 2024. "
            "This is a receipt, not the approved annual allocation."
        ),
    },
    {
        "financial_year": 2023,
        "allocation_category": "CDF funding received",
        "amount_disbursed_zmw": 190_589_326,
        "notes": (
            "Comparative 2023 CDF funding receipt reported in "
            "the 2024 financial statement. This is a receipt, "
            "not the approved annual allocation."
        ),
    },
]


REPORTED_ASSET_USAGE = [
    {
        "financial_year": 2024,
        "allocation_category": (
            "CDF Community projects - fixed asset acquisition"
        ),
        "amount_spent_zmw": 37_979_780,
        "notes": (
            "Reported under buildings and structures in the "
            "2024 financial statement. This represents reported "
            "fixed-asset acquisition, not necessarily total CDF "
            "project expenditure."
        ),
    },
    {
        "financial_year": 2024,
        "allocation_category": (
            "CDF School desks - fixed asset acquisition"
        ),
        "amount_spent_zmw": 4_426_946,
        "notes": (
            "Reported under other assets in the 2024 financial "
            "statement. This is a specific asset-acquisition "
            "figure and not total CDF expenditure."
        ),
    },
    {
        "financial_year": 2023,
        "allocation_category": (
            "CDF Community projects - fixed asset acquisition"
        ),
        "amount_spent_zmw": 6_867_103,
        "notes": (
            "Comparative 2023 amount reported under buildings "
            "and structures in the 2024 financial statement."
        ),
    },
    {
        "financial_year": 2023,
        "allocation_category": (
            "CDF Motor vehicles - fixed asset acquisition"
        ),
        "amount_spent_zmw": 13_720_624,
        "notes": (
            "Comparative 2023 CDF motor-vehicle acquisition "
            "reported in the 2024 financial statement."
        ),
    },
    {
        "financial_year": 2023,
        "allocation_category": (
            "CDF Specialised vehicles - fixed asset acquisition"
        ),
        "amount_spent_zmw": 3_910_440,
        "notes": (
            "Comparative 2023 CDF specialised-vehicle "
            "acquisition reported in the 2024 financial statement."
        ),
    },
]


def blank_row() -> dict:
    """Return an empty row using the required allocation schema."""
    return {field: "" for field in FIELDS}


def create_budget_rows() -> list[dict]:
    """Create one row per verified allocation category."""
    rows = []

    for year in sorted(BUDGET_ALLOCATIONS):
        budget = BUDGET_ALLOCATIONS[year]

        for category, amount in budget["categories"].items():
            row = blank_row()

            row.update({
                "financial_year": year,
                "constituency": ALL_CONSTITUENCIES,
                "allocation_category": category,
                "approved_allocation_zmw": amount,
                "source_title": budget["source_title"],
                "source_url": budget["source_url"],
                "date_accessed": DATE_ACCESSED,
                "notes": (
                    "Approved annual budget estimate covering "
                    "all seven Lusaka constituencies. "
                    "Disbursement, expenditure and unspent balance "
                    "were not reported in this budget table."
                ),
            })

            if year == 2024 and category == "Community Projects":
                row["notes"] += (
                    " The exact subprogramme table reports "
                    "ZMW 122,236,211. A nearby narrative mentions "
                    "approximately ZMW 128.3 million; the exact "
                    "table value was retained."
                )

            rows.append(row)

    return rows


def create_receipt_rows() -> list[dict]:
    """Create verified funding-receipt rows."""
    rows = []

    for receipt in FUNDING_RECEIPTS:
        row = blank_row()

        row.update({
            "financial_year": receipt["financial_year"],
            "constituency": ALL_CONSTITUENCIES,
            "allocation_category": (
                receipt["allocation_category"]
            ),
            "amount_disbursed_zmw": (
                receipt["amount_disbursed_zmw"]
            ),
            "source_title": FINANCIAL_STATEMENT_TITLE,
            "source_url": FINANCIAL_STATEMENT_URL,
            "date_accessed": DATE_ACCESSED,
            "notes": receipt["notes"],
        })

        rows.append(row)

    return rows


def create_usage_rows() -> list[dict]:
    """Create available fixed-asset usage records."""
    rows = []

    for usage in REPORTED_ASSET_USAGE:
        row = blank_row()

        row.update({
            "financial_year": usage["financial_year"],
            "constituency": ALL_CONSTITUENCIES,
            "allocation_category": (
                usage["allocation_category"]
            ),
            "amount_spent_zmw": usage["amount_spent_zmw"],
            "source_title": FINANCIAL_STATEMENT_TITLE,
            "source_url": FINANCIAL_STATEMENT_URL,
            "date_accessed": DATE_ACCESSED,
            "notes": usage["notes"],
        })

        rows.append(row)

    return rows


def assign_record_ids(rows: list[dict]) -> None:
    """Give every record a stable unique identifier."""
    for index, row in enumerate(rows, start=1):
        row["record_id"] = f"LCC-CDF-ALLOC-{index:03d}"


def validate_budget_totals() -> bool:
    """Confirm that category totals match official programme totals."""
    all_passed = True

    print("\nBudget validation:")

    for year in sorted(BUDGET_ALLOCATIONS):
        budget = BUDGET_ALLOCATIONS[year]
        calculated = sum(budget["categories"].values())
        expected = budget["total"]
        passed = calculated == expected

        if not passed:
            all_passed = False

        result = "PASS" if passed else "FAIL"

        print(
            f"{year}: calculated={calculated:,}, "
            f"official_total={expected:,} {result}"
        )

    return all_passed


def validate_rows(rows: list[dict]) -> bool:
    """Check record IDs, required fields and duplicate records."""
    record_ids = [row["record_id"] for row in rows]

    duplicate_ids = len(record_ids) - len(set(record_ids))

    duplicate_keys = set()
    seen_keys = set()

    for row in rows:
        key = (
            row["financial_year"],
            row["constituency"],
            row["allocation_category"],
            row["approved_allocation_zmw"],
            row["amount_disbursed_zmw"],
            row["amount_spent_zmw"],
        )

        if key in seen_keys:
            duplicate_keys.add(key)

        seen_keys.add(key)

    missing_sources = sum(
        1
        for row in rows
        if not row["source_title"] or not row["source_url"]
    )

    print("\nRecord validation:")
    print(f"Records: {len(rows)}")
    print(f"Columns: {len(FIELDS)}")
    print(f"Duplicate record IDs: {duplicate_ids}")
    print(f"Duplicate financial records: {len(duplicate_keys)}")
    print(f"Records missing sources: {missing_sources}")

    return (
        duplicate_ids == 0
        and len(duplicate_keys) == 0
        and missing_sources == 0
    )


def write_csv(rows: list[dict]) -> None:
    """Write the final pipe-separated allocation CSV."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as output:
        writer = csv.DictWriter(
            output,
            fieldnames=FIELDS,
            delimiter="|",
        )

        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = []

    rows.extend(create_budget_rows())
    rows.extend(create_receipt_rows())
    rows.extend(create_usage_rows())

    rows.sort(
        key=lambda row: (
            int(row["financial_year"]),
            row["allocation_category"],
        )
    )

    assign_record_ids(rows)

    totals_passed = validate_budget_totals()
    records_passed = validate_rows(rows)

    write_csv(rows)

    print(f"\nVerified allocation records saved: {len(rows)}")
    print(f"Output file: {OUTPUT_FILE}")

    if totals_passed and records_passed:
        print("Final allocation validation: PASS")
    else:
        print("Final allocation validation: FAIL")
        print("Do not commit until the errors are corrected.")


if __name__ == "__main__":
    main()