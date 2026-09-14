from pathlib import Path
import csv
import re


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OCR_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "cdf"
    / "ocr_text"
    / "lcc_community_projects_2025_1_ocr.txt"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "cleaned" / "cdf"

OUTPUT_FILE = (
    OUTPUT_DIR
    / "db-unza26-csc4792-lusaka_city_council_cdf_projects.csv"
)

SOURCE_TITLE = "Lusaka City Council CDF Projects for the Year 2025"
SOURCE_URL = "https://www.lcc.gov.zm/publications/"
DATE_ACCESSED = "2026-09-14"


FIELDS = [
    "record_id",
    "financial_year",
    "constituency",
    "ward",
    "project_name",
    "project_category",
    "project_description",
    "approved_budget_zmw",
    "amount_disbursed_zmw",
    "amount_spent_zmw",
    "project_status",
    "completion_percentage",
    "approval_date",
    "completion_date",
    "beneficiaries",
    "contractor",
    "source_title",
    "source_url",
    "date_accessed",
    "notes",
]


PAGE_CONSTITUENCIES = {
    1: "Chawama",
    2: "Kabwata",
    3: "Kanyama",
    4: "Lusaka Central",
    5: "Mandevu",
    6: "Matero",
    7: "Munali",
}


WARD_ALIASES = {
    "Chawama": {
        "lilayi ward 4": "Lilayi Ward 4",
        "chawama ward 2": "Chawama Ward 2",
        "john howard ward": "John Howard Ward",
        "nkoloma ward 1": "Nkoloma Ward 1",
        "nkoloma ward": "Nkoloma Ward",
    },
    "Kabwata": {
        "kamwala": "Kamwala Ward",
        "kabwata": "Kabwata Ward",
        "libala": "Libala Ward",
        "chilenje": "Chilenje Ward",
        "kamulanga": "Kamulanga Ward",
    },
    "Kanyama": {
        "harry mwaanga nkumbula": "Harry Mwaanga Nkumbula Ward",
        "harry mwanga nkumbula": "Harry Mwaanga Nkumbula Ward",
        "kanyama ward 13": "Kanyama Ward 13",
        "kayama ward 13": "Kanyama Ward 13",
        "makeni villa": "Makeni Villa Ward",
        "garden park": "Garden Park Ward",
        "munkolo": "Munkolo Ward",
        "chinika": "Chinika Ward",
        "chinka": "Chinika Ward",
    },
    "Lusaka Central": {
        "independence": "Independence Ward",
        "kabulonga": "Kabulonga Ward",
        "silwizya": "Silwizya Ward",
        "silwzya": "Silwizya Ward",
        "lubwa": "Lubwa Ward",
    },
    "Mandevu": {
        "justin kabwe ward": "Justin Kabwe Ward",
        "mulungushi ward": "Mulungushi Ward",
        "mpulungu ward": "Mpulungu Ward",
        "ngwerere ward": "Ngwerere Ward",
        "kabanana ward": "Kabanana Ward",
        "roma ward": "Roma Ward",
    },
    "Matero": {
        "matero 32": "Matero Ward 32",
        "muchinga": "Muchinga Ward",
        "mwembeshi": "Mwembeshi Ward",
        "kapwepwe": "Kapwepwe Ward",
        "lima": "Lima Ward",
    },
    "Munali": {
        "chankunkula": "Chankunkula Ward",
        "chakunkula": "Chankunkula Ward",
        "kalingalinga": "Kalingalinga Ward",
        "kaliklikiliki": "Kalikiliki Ward",
        "kalikiliki": "Kalikiliki Ward",
        "mtendere": "Mtendere Ward",
        "chainda": "Chainda Ward",
        "munali": "Munali Ward",
    },
}


EXPECTED_TOTALS = {
    "Chawama": 17_748_505,
    "Kabwata": 16_789_271,
    "Kanyama": 17_001_859,
    "Lusaka Central": 17_750_444,
    "Mandevu": 17_750_444,
    "Matero": 17_621_958,
    "Munali": 17_656_232,
}


def clean_text(value: str) -> str:
    """Clean common OCR characters and unnecessary spacing."""
    replacements = {
        "â€“": "-",
        "â€”": "-",
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
        "\u00a0": " ",
    }

    for incorrect, correct in replacements.items():
        value = value.replace(incorrect, correct)

    value = re.sub(r"\s+", " ", value)
    return value.strip(" |-")


def normalise_project_name(value: str) -> str:
    """Correct obvious OCR spelling errors without changing meaning."""
    value = clean_text(value)

    replacements = {
        r"\bContruction\b": "Construction",
        r"\bcontruction\b": "construction",
        r"\bMartenity\b": "Maternity",
        r"\bmartenity\b": "maternity",
        r"\bRebabilition\b": "Rehabilitation",
        r"\bRehabitation\b": "Rehabilitation",
        r"\bRehabiliation\b": "Rehabilitation",
        r"\bMortury\b": "Mortuary",
        r"\bmortury\b": "mortuary",
        r"\bKayama\b": "Kanyama",
        r"\bChruch\b": "Church",
        r"\bTrafic\b": "Traffic",
        r"\bEquipments\b": "Equipment",
        r"\bReformed Churchh\b": "Reformed Church",
    }

    for pattern, replacement in replacements.items():
        value = re.sub(pattern, replacement, value)

    return value.strip()


def classify_project(project_name: str) -> str:
    """Assign a broad category using only words in the project name."""
    name = project_name.lower()

    if any(word in name for word in [
        "road", "paving", "street", "drainage", "bridge",
        "walkway", "gravelling", "grading"
    ]):
        return "Roads and drainage"

    if any(word in name for word in [
        "school", "classroom", "crb", "desk", "laboratory",
        "library", "education"
    ]):
        return "Education"

    if any(word in name for word in [
        "clinic", "hospital", "maternity", "mortuary",
        "incinerator", "medicine", "health"
    ]):
        return "Health"

    if any(word in name for word in [
        "police", "security"
    ]):
        return "Public safety"

    if any(word in name for word in [
        "market", "trader"
    ]):
        return "Markets and commerce"

    if any(word in name for word in [
        "water", "borehole", "reticulation"
    ]):
        return "Water and sanitation"

    if any(word in name for word in [
        "street light", "streetlight", "solar light", "solar panel"
    ]):
        return "Energy and lighting"

    if any(word in name for word in [
        "ground", "recreation", "community hall", "gym"
    ]):
        return "Community and recreation"

    if any(word in name for word in [
        "ambulance", "tractor", "vehicle", "tipper"
    ]):
        return "Equipment and vehicles"

    return "Other community infrastructure"


def extract_page(text: str, page_number: int) -> str:
    """Return the text belonging to one numbered page."""
    pattern = (
        rf"===== PAGE {page_number} ====="
        rf"(.*?)"
        rf"(?====== PAGE {page_number + 1} =====|\Z)"
    )

    match = re.search(pattern, text, flags=re.DOTALL)

    if not match:
        raise ValueError(f"Page {page_number} was not found.")

    return match.group(1)


def locate_ward(
    constituency: str,
    combined_text: str,
) -> tuple[str, str]:
    """
    Separate the project name from the ward appearing at the end
    of a record.
    """
    aliases = WARD_ALIASES[constituency]

    lowered = combined_text.lower()
    best_position = -1
    best_alias = None
    best_ward = None

    # Match longer ward names first.
    for alias, official_ward in sorted(
        aliases.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        position = lowered.rfind(alias)

        if position > best_position:
            best_position = position
            best_alias = alias
            best_ward = official_ward

    if best_position == -1:
        return clean_text(combined_text), ""

    project_name = combined_text[:best_position]
    trailing_text = combined_text[
        best_position + len(best_alias):
    ]

    # Ward should be near the end. If substantial text follows,
    # avoid making an unsafe split.
    if len(clean_text(trailing_text)) > 25:
        return clean_text(combined_text), ""

    return clean_text(project_name), best_ward


def parse_page(page_text: str, constituency: str) -> list[dict]:
    """Parse project rows from one 2025 constituency page."""
    lines = [
        clean_text(line)
        for line in page_text.splitlines()
        if clean_text(line)
    ]

    # Start below the table heading.
    start_index = 0

    for index, line in enumerate(lines):
        if line.upper() in {"AMOUNT", "ESTIMATED AMOUNT"}:
            start_index = index + 1
            break

    lines = lines[start_index:]

    records = []
    current_number = None
    current_parts = []

    record_number_pattern = re.compile(r"^\d{1,2}$")
    amount_pattern = re.compile(r"^\d{1,3}(?:,\d{3})+$")

    for line in lines:
        if line.upper() == "TOTAL":
            continue

        if record_number_pattern.fullmatch(line):
            if current_number is None:
                current_number = int(line)
                current_parts = []
            continue

        if (
            current_number is not None
            and amount_pattern.fullmatch(line)
        ):
            amount = int(line.replace(",", ""))

            combined = clean_text(" ".join(current_parts))
            project_name, ward = locate_ward(
                constituency,
                combined,
            )

            if project_name:
                records.append({
                    "source_number": current_number,
                    "constituency": constituency,
                    "ward": ward,
                    "project_name": normalise_project_name(
                        project_name
                    ),
                    "approved_budget_zmw": amount,
                })

            current_number = None
            current_parts = []
            continue

        if current_number is not None:
            current_parts.append(line)

    return records


def add_missing_munali_record(records: list[dict]) -> None:
    """
    The source omitted a visible serial number before the Kaunda
    Square Community Ground record. Add it explicitly from the
    official source text.
    """
    already_present = any(
        "kaunda square community ground"
        in row["project_name"].lower()
        for row in records
    )

    if not already_present:
        records.append({
            "source_number": "Not shown",
            "constituency": "Munali",
            "ward": "Munali Ward",
            "project_name": "Kaunda Square Community Ground",
            "approved_budget_zmw": 1_650_000,
        })


def create_final_rows(parsed_records: list[dict]) -> list[dict]:
    """Convert parsed records into the required 20-column schema."""
    final_rows = []

    for index, item in enumerate(parsed_records, start=1):
        project_name = item["project_name"]
        constituency = item["constituency"]
        ward = item["ward"]

        notes = (
            "Listed in the official LCC 2025 CDF community-project "
            "schedule with an approved project amount. "
            "Implementation progress, disbursement, expenditure, "
            "contractor, beneficiaries and completion dates were "
            "not reported in this source."
        )

        if not ward:
            notes += " Ward could not be verified from the extracted text."

        final_rows.append({
            "record_id": f"LCC-CDF-PROJ-2025-{index:03d}",
            "financial_year": "2025",
            "constituency": constituency,
            "ward": ward,
            "project_name": project_name,
            "project_category": classify_project(project_name),
            "project_description": project_name,
            "approved_budget_zmw": item["approved_budget_zmw"],
            "amount_disbursed_zmw": "",
            "amount_spent_zmw": "",
            "project_status": "Planned",
            "completion_percentage": "",
            "approval_date": "",
            "completion_date": "",
            "beneficiaries": "",
            "contractor": "",
            "source_title": SOURCE_TITLE,
            "source_url": SOURCE_URL,
            "date_accessed": DATE_ACCESSED,
            "notes": notes,
        })

    return final_rows


def validate_records(records: list[dict]) -> bool:
    """Compare extracted constituency totals with source totals."""
    print("\nValidation by constituency:")
    all_passed = True

    for constituency, expected_total in EXPECTED_TOTALS.items():
        constituency_records = [
            row
            for row in records
            if row["constituency"] == constituency
        ]

        extracted_total = sum(
            int(row["approved_budget_zmw"])
            for row in constituency_records
        )

        passed = extracted_total == expected_total

        if not passed:
            all_passed = False

        result = "PASS" if passed else "CHECK"

        print(
            f"{constituency}: "
            f"records={len(constituency_records)}, "
            f"extracted={extracted_total:,}, "
            f"expected={expected_total:,} "
            f"{result}"
        )

    return all_passed


def main() -> None:
    if not OCR_FILE.exists():
        raise FileNotFoundError(
            f"Required OCR file was not found: {OCR_FILE}"
        )

    text = OCR_FILE.read_text(
        encoding="utf-8",
        errors="replace",
    )

    parsed_records = []

    for page_number, constituency in PAGE_CONSTITUENCIES.items():
        page_text = extract_page(text, page_number)
        page_records = parse_page(page_text, constituency)
        parsed_records.extend(page_records)

    add_missing_munali_record(parsed_records)

    # Give records a stable constituency/source order.
    constituency_order = {
        name: page
        for page, name in PAGE_CONSTITUENCIES.items()
    }

    parsed_records.sort(
        key=lambda row: (
            constituency_order[row["constituency"]],
            (
                row["source_number"]
                if isinstance(row["source_number"], int)
                else 999
            ),
        )
    )

    final_rows = create_final_rows(parsed_records)

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
        writer.writerows(final_rows)

    validation_passed = validate_records(final_rows)

    print(f"\nVerified project records saved: {len(final_rows)}")
    print(f"Output file: {OUTPUT_FILE}")

    if validation_passed:
        print("All constituency financial totals: PASS")
    else:
        print(
            "Some totals require checking. "
            "Do not commit the output yet."
        )


if __name__ == "__main__":
    main()