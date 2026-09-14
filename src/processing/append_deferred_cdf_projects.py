
from pathlib import Path
import csv
import re


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "cdf"
    / "ocr_text"
    / "lusaka_city_council_defered_projects_ocr.txt"
)

PROJECTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "cdf"
    / "db-unza26-csc4792-lusaka_city_council_cdf_projects.csv"
)

SOURCE_TITLE = (
    "Lusaka City Council List of Proposed Projects "
    "and Simple Justification for Defering"
)
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
    4: "Kanyama",
    5: "Lusaka Central",
    6: "Mandevu",
    7: "Mandevu",
    8: "Matero",
    9: "Matero",
    10: "Munali",
}


EXPECTED_COUNTS = {
    "Chawama": 8,
    "Kabwata": 11,
    "Kanyama": 22,
    "Lusaka Central": 10,
    "Mandevu": 23,
    "Matero": 25,
    "Munali": 13,
}


WARD_ALIASES = {
    "Chawama": {
        "chawama ward 3": "Chawama Ward 3",
        "chawama ward 2": "Chawama Ward 2",
        "john howard": "John Howard Ward",
        "nkoloma ward": "Nkoloma Ward",
        "lilayi ward": "Lilayi Ward",
    },
    "Kabwata": {
        "kamwala ward": "Kamwala Ward",
        "chilenje ward": "Chilenje Ward",
        "libala ward": "Libala Ward",
    },
    "Kanyama": {
        "harry mwaanga nkumbula ward": (
            "Harry Mwaanga Nkumbula Ward"
        ),
        "harry mwanga nkumbula ward": (
            "Harry Mwaanga Nkumbula Ward"
        ),
        "makeni villa ward": "Makeni Villa Ward",
        "garden park": "Garden Park Ward",
        "munkolo ward": "Munkolo Ward",
        "chinika ward": "Chinika Ward",
    },
    "Lusaka Central": {
        "silwizya ward": "Silwizya Ward",
        "lubwa ward": "Lubwa Ward",
        "kabulonga ward": "Kabulonga Ward",
    },
    "Mandevu": {
        "justine kabwe ward": "Justin Kabwe Ward",
        "justin kabwe ward": "Justin Kabwe Ward",
        "raphael chota": "Raphael Chota Ward",
        "mulungushi ward": "Mulungushi Ward",
        "mpulungu ward": "Mpulungu Ward",
        "kabanana ward": "Kabanana Ward",
        "ngwerere ward": "Ngwerere Ward",
        "chaisa ward": "Chaisa Ward",
        "roma ward": "Roma Ward",
    },
    "Matero": {
        "matero ward 32": "Matero Ward 32",
        "mwembeshi ward": "Mwembeshi Ward",
        "kapwepwe ward": "Kapwepwe Ward",
        "muchinga ward": "Muchinga Ward",
        "lima ward": "Lima Ward",
    },
    "Munali": {
        "kalingalinga ward": "Kalingalinga Ward",
        "chankunkula ward": "Chankunkula Ward",
        "chakunkula": "Chankunkula Ward",
        "chainda ward": "Chainda Ward",
        "munali ward": "Munali Ward",
    },
}


def clean_text(value: str) -> str:
    """Remove OCR encoding errors and unnecessary spacing."""
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

    return value.strip(" |_-:")


def clean_project_name(value: str) -> str:
    """Correct obvious OCR spelling errors."""
    value = clean_text(value)

    replacements = {
        r"\bConsruction\b": "Construction",
        r"\bConstrution\b": "Construction",
        r"\bcontruction\b": "construction",
        r"\bExpsnsion\b": "Expansion",
        r"\bschoool\b": "school",
        r"\bmordern\b": "modern",
        r"\bequiping\b": "equipping",
        r"\bphsics\b": "physics",
        r"\bdevelopmenmt\b": "development",
        r"\bcumpus cornner\b": "Campus Corner",
        r"\brefugue\b": "Refuge",
        r"\bjustine kabwe\b": "Justin Kabwe",
    }

    for pattern, replacement in replacements.items():
        value = re.sub(
            pattern,
            replacement,
            value,
            flags=re.IGNORECASE,
        )

    if value:
        value = value[0].upper() + value[1:]

    return value


def classify_project(project_name: str) -> str:
    """Classify the project from words in its official name."""
    name = project_name.lower()

    if any(word in name for word in [
        "road", "paving", "street", "drainage",
        "bridge", "walkway", "gravelling", "grading",
    ]):
        return "Roads and drainage"

    if any(word in name for word in [
        "school", "classroom", "crb", "desk",
        "laboratory", "library",
    ]):
        return "Education"

    if any(word in name for word in [
        "clinic", "hospital", "maternity", "mortuary",
        "health", "medicine", "mourners shelter",
    ]):
        return "Health"

    if "police" in name:
        return "Public safety"

    if any(word in name for word in [
        "market", "trader",
    ]):
        return "Markets and commerce"

    if any(word in name for word in [
        "water", "borehole", "reticulation",
    ]):
        return "Water and sanitation"

    if any(word in name for word in [
        "solar", "street light", "streetlight",
    ]):
        return "Energy and lighting"

    if any(word in name for word in [
        "ground", "recreation", "community hall",
        "football", "youth park",
    ]):
        return "Community and recreation"

    return "Other community infrastructure"


def split_pages(text: str) -> dict[int, str]:
    """Split the OCR document into numbered pages."""
    parts = re.split(
        r"===== PAGE\s+(\d+)\s+=====",
        text,
    )

    pages = {}

    for index in range(1, len(parts), 2):
        page_number = int(parts[index])
        page_text = parts[index + 1]
        pages[page_number] = page_text

    return pages


def remove_comment(value: str) -> str:
    """Remove the repeated reason for deferral."""
    patterns = [
        r"\bNo Enough Funds\b",
        r"\bNo enough Funds\b",
        r"\bNo enough funds\b",
        r"\bNo Funds\b",
        r"\bNo funds\b",
    ]

    for pattern in patterns:
        value = re.sub(
            pattern,
            "",
            value,
            flags=re.IGNORECASE,
        )

    return clean_text(value)


def split_records(page_text: str) -> list[tuple[int, str]]:
    """
    Split page text into numbered records.

    This accepts:
    1 Project name
    1 | Project name
    1. Project name
    or a number appearing on its own line.
    """
    lines = [
        clean_text(line)
        for line in page_text.splitlines()
        if clean_text(line)
    ]

    record_pattern = re.compile(
        r"^\s*(\d{1,2})\s*(?:[|.)-]\s*)?(.*)$"
    )

    records = []
    current_number = None
    current_lines = []

    for line in lines:
        lower_line = line.lower()

        if lower_line.startswith("extraction method"):
            continue

        if lower_line in {
            "s/n",
            "project name and description",
            "constituency",
            "constittuency",
            "ward",
            "comment",
            "comment - justification for non approval",
            "justification for non approval",
        }:
            continue

        match = record_pattern.match(line)

        candidate_number = None
        first_text = ""

        if match:
            candidate_number = int(match.group(1))
            first_text = clean_text(match.group(2))

        starts_new_record = False

        if candidate_number is not None:
            if current_number is None:
                starts_new_record = True
            elif candidate_number == current_number + 1:
                starts_new_record = True

        if starts_new_record:
            if current_number is not None and current_lines:
                records.append((
                    current_number,
                    clean_text(" ".join(current_lines)),
                ))

            current_number = candidate_number
            current_lines = []

            if first_text:
                current_lines.append(first_text)

            continue

        if current_number is not None:
            current_lines.append(line)

    if current_number is not None and current_lines:
        records.append((
            current_number,
            clean_text(" ".join(current_lines)),
        ))

    return records


def find_ward(
    constituency: str,
    location_text: str,
) -> str:
    """Convert extracted ward text into a standard ward name."""
    lowered = location_text.lower()
    aliases = WARD_ALIASES[constituency]

    best_position = -1
    best_ward = ""

    for alias, official_ward in sorted(
        aliases.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        position = lowered.rfind(alias)

        if position > best_position:
            best_position = position
            best_ward = official_ward

    return best_ward


def split_project_and_ward(
    constituency: str,
    record_text: str,
) -> tuple[str, str]:
    """Separate project name, constituency and ward fields."""
    value = remove_comment(record_text)
    lowered = value.lower()
    constituency_name = constituency.lower()

    positions = [
        match.start()
        for match in re.finditer(
            re.escape(constituency_name),
            lowered,
        )
    ]

    if not positions:
        return clean_project_name(value), ""

    split_position = positions[-1]

    project_text = value[:split_position]

    location_text = value[
        split_position + len(constituency_name):
    ]

    ward = find_ward(
        constituency,
        location_text,
    )

    if (
        not ward
        and constituency == "Munali"
        and "constituency" in location_text.lower()
    ):
        ward = "Constituency-wide"

    return clean_project_name(project_text), ward


def parse_projects(text: str) -> list[dict]:
    pages = split_pages(text)
    projects = []

    for page_number, constituency in PAGE_CONSTITUENCIES.items():
        if page_number not in pages:
            print(f"WARNING: Page {page_number} was not found.")
            continue

        records = split_records(pages[page_number])

        for source_number, record_text in records:
            project_name, ward = split_project_and_ward(
                constituency,
                record_text,
            )

            if not project_name:
                continue

            projects.append({
                "page_number": page_number,
                "source_number": source_number,
                "constituency": constituency,
                "ward": ward,
                "project_name": project_name,
            })

    return projects


def make_final_rows(projects: list[dict]) -> list[dict]:
    rows = []

    for index, project in enumerate(projects, start=1):
        notes = (
            "The official LCC source lists this proposed "
            "project as deferred because sufficient funding "
            "was not available. The source does not state the "
            "financial year, approved budget, disbursement, "
            "expenditure, contractor, beneficiaries or "
            "completion date. "
            f"Source page: {project['page_number']}."
        )

        if not project["ward"]:
            notes += (
                " The ward was unclear and was left blank."
            )

        row = {field: "" for field in FIELDS}

        row.update({
            "record_id": f"LCC-CDF-DEFER-{index:03d}",
            "financial_year": "",
            "constituency": project["constituency"],
            "ward": project["ward"],
            "project_name": project["project_name"],
            "project_category": classify_project(
                project["project_name"]
            ),
            "project_description": project["project_name"],
            "approved_budget_zmw": "",
            "amount_disbursed_zmw": "",
            "amount_spent_zmw": "",
            "project_status": "Deferred",
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

        rows.append(row)

    return rows


def read_existing_projects() -> list[dict]:
    """Read the 2025 records and remove old generated deferred rows."""
    if not PROJECTS_FILE.exists():
        raise FileNotFoundError(
            f"Project CSV was not found: {PROJECTS_FILE}"
        )

    with PROJECTS_FILE.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as source:
        reader = csv.DictReader(
            source,
            delimiter="|",
        )

        return [
            row
            for row in reader
            if not row["record_id"].startswith(
                "LCC-CDF-DEFER-"
            )
        ]


def validate_deferred(rows: list[dict]) -> bool:
    print("\nDeferred-project validation:")

    passed_everything = True

    for constituency, expected in EXPECTED_COUNTS.items():
        found = sum(
            1
            for row in rows
            if row["constituency"] == constituency
        )

        passed = found == expected

        if not passed:
            passed_everything = False

        result = "PASS" if passed else "CHECK"

        print(
            f"{constituency}: "
            f"records={found}, expected={expected} {result}"
        )

    missing_names = sum(
        1 for row in rows if not row["project_name"]
    )

    missing_wards = sum(
        1 for row in rows if not row["ward"]
    )

    print(f"Missing project names: {missing_names}")
    print(f"Missing or unclear wards: {missing_wards}")

    return passed_everything and missing_names == 0


def write_projects(rows: list[dict]) -> None:
    with PROJECTS_FILE.open(
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
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Deferred source file was not found: "
            f"{SOURCE_FILE}"
        )

    text = SOURCE_FILE.read_text(
        encoding="utf-8",
        errors="replace",
    )

    parsed_projects = parse_projects(text)
    deferred_rows = make_final_rows(parsed_projects)
    existing_rows = read_existing_projects()

    validation_passed = validate_deferred(
        deferred_rows
    )

    final_rows = existing_rows + deferred_rows
    write_projects(final_rows)

    print(f"\nExisting verified projects: {len(existing_rows)}")
    print(f"Deferred projects added: {len(deferred_rows)}")
    print(f"Total project records: {len(final_rows)}")
    print(f"Output file: {PROJECTS_FILE}")

    if validation_passed:
        print("Deferred-project validation: PASS")
    else:
        print(
            "Deferred-project validation requires review. "
            "Do not commit yet."
        )


if __name__ == "__main__":
    main()