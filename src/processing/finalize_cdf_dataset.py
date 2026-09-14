from pathlib import Path
import csv
import re


ROOT = Path(__file__).resolve().parents[2]

PROJECTS_FILE = (
    ROOT / "data" / "cleaned" / "cdf"
    / "db-unza26-csc4792-lusaka_city_council_cdf_projects.csv"
)

ALLOCATIONS_FILE = (
    ROOT / "data" / "cleaned" / "cdf"
    / "db-unza26-csc4792-lusaka_city_council_cdf_allocations.csv"
)

NOTES_FILE = ROOT / "metadata" / "cdf_verification_notes.md"
QA_FILE = ROOT / "metadata" / "cdf_quality_report.txt"

PUBLICATIONS_URL = "https://www.lcc.gov.zm/publications/"
DATE_ACCESSED = "2026-09-14"


PROJECT_FIELDS = [
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


APPROVED_2024 = [
    # Chawama
    ("Chawama", "John Howard Ward 3",
     "John Patuka via Distinction School-Off Lime Road (1.10 km)",
     "2024-02-02"),
    ("Chawama", "Nkoloma Ward 1",
     "Katwishi Road (0.8 km)", "2024-02-02"),
    ("Chawama", "Nkoloma Ward 1",
     "Uweka Road (1 km)", "2024-02-02"),
    ("Chawama", "Chawama Ward 2",
     "Alex to Mount Meru Road (0.87 km)", "2024-02-02"),
    ("Chawama", "Lilayi Ward 4",
     "Lilayi Close Road (2.25 km)", "2024-02-02"),
    ("Chawama", "Constituency-wide",
     "Procurement of an ambulance", "2024-02-02"),

    # Kabwata — clearly readable records
    ("Kabwata", "Libala Ward",
     "Completion of a 1x3 classroom block at Lusakasa Primary School",
     "2024-04-19"),
    ("Kabwata", "Libala Ward",
     "Completion of a 1x2 laboratory block at Mkandawire Secondary School",
     "2024-04-19"),
    ("Kabwata", "Libala Ward",
     "Grading and gravelling of Katata Road", "2024-04-19"),
    ("Kabwata", "Libala Ward",
     "Grading and gravelling of Kalulu Street (0.155 km)",
     "2024-04-19"),
    ("Kabwata", "Libala Ward",
     "Grading and gravelling of Kabuzu Street (0.25 km)",
     "2024-04-19"),
    ("Kabwata", "Libala Ward",
     "Grading and gravelling of Kalabi Road (0.25 km)",
     "2024-04-19"),
    ("Kabwata", "Libala Ward",
     "Road works off Nationalist Road opposite shopping mall",
     "2024-04-19"),
    ("Kabwata", "Libala Ward",
     "Furniture for Katungu Police Post", "2024-04-19"),
    ("Kabwata", "Kabwata Ward 6",
     "Completion of a 1x3 classroom block at Kabwata Primary School",
     "2024-04-19"),
    ("Kabwata", "Kabwata Ward 6",
     "Completion of a 1x3 classroom block at St Patricks Primary School",
     "2024-04-19"),

    # Kanyama — clearly readable records
    ("Kanyama", "Constituency-wide",
     "Procurement of an ambulance", "2024-08-08"),
    ("Kanyama", "Chinika Ward",
     "Furnishing and paving at Chinika Community Hall",
     "2024-08-08"),
    ("Kanyama", "Kanyama Ward 13",
     "Construction of a dressing room at Twashuka",
     "2024-08-08"),
    ("Kanyama", "Harry Mwaanga Nkumbula Ward",
     "Extension of the mobile traders shelter at John Laing",
     "2024-08-08"),
    ("Kanyama", "Munkolo Ward",
     "Procurement of 638 desks for Bayuni, Linda, Munkolo and ZOCS",
     "2024-08-08"),
    ("Kanyama", "Kanyama Ward 13",
     "Procurement of 411 desks for Twashuka Combined School",
     "2024-08-08"),
    ("Kanyama", "Chinika Ward",
     "Procurement of 1,125 desks", "2024-08-08"),
    ("Kanyama", "Harry Mwaanga Nkumbula Ward",
     "Procurement of 626 desks for John Laing and Chibolya",
     "2024-08-08"),
    ("Kanyama", "Garden Park Ward",
     "Rehabilitation of Twin Palm and Garden Park roads",
     "2024-08-08"),
    ("Kanyama", "Makeni Villa Ward",
     "Rehabilitation of Transmitter Road", "2024-08-08"),
    ("Kanyama", "Harry Mwaanga Nkumbula Ward",
     "Rehabilitation of Kampasa Road", "2024-08-08"),
    ("Kanyama", "Chinika Ward",
     "Rehabilitation of selected roads in Chinika",
     "2024-08-08"),
    ("Kanyama", "Munkolo Ward",
     "Rehabilitation of Master Luu Road", "2024-08-08"),
    ("Kanyama", "Munkolo Ward",
     "Rehabilitation of Ross Breeders Road", "2024-08-08"),

    # Lusaka Central — clearly readable records
    ("Lusaka Central", "Independence Ward",
     "Construction of a 1x3 classroom block at Jacaranda Secondary School Phase 2",
     "2024-03-18"),
    ("Lusaka Central", "Kabulonga Ward",
     "Rehabilitation of sanitary installations at Bauleni Police Post",
     "2024-03-18"),
    ("Lusaka Central", "Kabulonga Ward",
     "Rehabilitation of the ceiling and floor at Kabulonga Boys Secondary School",
     "2024-03-18"),
    ("Lusaka Central", "Kabulonga Ward",
     "Construction of a mortuary at Bauleni Mini Hospital",
     "2024-03-18"),
    ("Lusaka Central", "Kabulonga Ward",
     "Construction of the road between ZAF and Bauleni Township Phase 1",
     "2024-03-18"),
    ("Lusaka Central", "Kabulonga Ward",
     "Procurement of ten tents", "2024-03-18"),
    ("Lusaka Central", "Kabulonga Ward",
     "Construction of a maternity wing at Malata Health Post Phase 1",
     "2024-03-18"),
    ("Lusaka Central", "Constituency-wide",
     "Purchase of a paving machine", "2024-03-18"),
    ("Lusaka Central", "Constituency-wide",
     "Procurement of an ambulance", "2024-03-18"),
    ("Lusaka Central", "Lubwa Ward",
     "Rehabilitation of Inonge Wina Road", "2024-03-18"),

    # Mandevu
    ("Mandevu", "Chaisa Ward",
     "Construction of a 1x3 classroom block at Chaisa Combined School Phase 1",
     "2024-02-02"),
    ("Mandevu", "Ngwerere Ward",
     "Construction of a 1x3 classroom block at Ngwelele Primary School Phase 1",
     "2024-02-02"),
    ("Mandevu", "Mpulungu Ward",
     "Levelling and fencing of Bwafwano Recreation Ground Phase 1",
     "2024-02-02"),
    ("Mandevu", "Roma Ward",
     "Construction of a maternity wing at Kasisi Health Post Phase 1",
     "2024-02-02"),
    ("Mandevu", "Raphael Chota Ward",
     "Construction of drainage from St Pauls to Chipata Primary School",
     "2024-02-02"),
    ("Mandevu", "Constituency-wide",
     "Rehabilitation of 2.8 km of gravel road",
     "2024-02-02"),
    ("Mandevu", "Justin Kabwe Ward",
     "Rehabilitation and construction of community drainage from Catholic Church to Kasangula Road",
     "2024-02-02"),
    ("Mandevu", "Kabanana Ward",
     "Top-up funding for Kabanana water projects",
     "2024-02-02"),
    ("Mandevu", "Constituency-wide",
     "Procurement of an ambulance", "2024-02-02"),
    ("Mandevu", "Constituency-wide",
     "Servicing of a grader and compactor", "2024-02-02"),
    ("Mandevu", "Constituency-wide",
     "Procurement of 3,000 desks", "2024-02-02"),

    # Matero — clearly readable records
    ("Matero", "Lima Ward",
     "Procurement of furniture and equipment for Chitikuko Skills Centre",
     "2024-08-08"),
    ("Matero", "Kapwepwe Ward",
     "Construction of drainages in Lilanda and Chitikuko",
     "2024-08-08"),
    ("Matero", "Kapwepwe Ward",
     "Completion of Kapwepwe Clinic", "2024-08-08"),
    ("Matero", "Muchinga Ward",
     "Construction of an ablution block at Edwin Mulongoti",
     "2024-08-08"),
    ("Matero", "",
     "Rehabilitation of Chunga Market facilities",
     "2024-08-08"),
    ("Matero", "Lima Ward",
     "Installation of street lighting from Children International Road to Katambalala Road junction",
     "2024-08-08"),
    ("Matero", "",
     "Erection of a wall fence at Matero Library",
     "2024-08-08"),
    ("Matero", "Mwembeshi Ward",
     "Construction of Kabole Bridge", "2024-08-08"),
    ("Matero", "Muchinga Ward",
     "Rehabilitation of T.C. and M.K. junctions",
     "2024-08-08"),
    ("Matero", "Constituency-wide",
     "Procurement of an ambulance", "2024-08-08"),
    ("Matero", "Constituency-wide",
     "Additional funding for procurement of a tipper truck",
     "2024-08-08"),
    ("Matero", "Mwembeshi Ward",
     "Construction of a classroom block at Namando Combined School",
     "2024-08-08"),
    ("Matero", "Constituency-wide",
     "Grading and road-bed preparation of selected roads",
     "2024-08-08"),

    # Munali
    ("Munali", "Chankunkula Ward",
     "Chelstone Bazaar and Muntanga roads", "2024-02-21"),
    ("Munali", "Chankunkula Ward",
     "Chelstone Green roads", "2024-02-21"),
    ("Munali", "Kalikiliki Ward",
     "Kalikiliki St Augustine Road", "2024-02-21"),
    ("Munali", "Kalikiliki Ward",
     "Kalikiliki Transmitter roads", "2024-02-21"),
    ("Munali", "Kalingalinga Ward",
     "Kalingalinga Second UNZA Last Road", "2024-02-21"),
    ("Munali", "Mtendere Ward",
     "Vera Chiluba Road to Jesus Army Road", "2024-02-21"),
    ("Munali", "Munali Ward",
     "Norwell to Amos Nachinga interconnector roads", "2024-02-21"),
    ("Munali", "Munali Ward",
     "Little Panda and Circuit roads", "2024-02-21"),
    ("Munali", "Mtendere Ward",
     "Mtendere Church Road", "2024-02-21"),
    ("Munali", "Chainda Ward",
     "Construction of a semi-detached house at Chainda Primary School",
     "2024-02-21"),
    ("Munali", "Chainda Ward",
     "Construction of an ablution block at Chainda Open School",
     "2024-02-21"),
    ("Munali", "Kalingalinga Ward",
     "Construction of a 1x3 classroom block at Kalingalinga Primary School",
     "2024-02-21"),
    ("Munali", "Kapwelyomba Ward",
     "Construction of a 1x3 classroom block at Kapwelyomba Primary School",
     "2024-02-21"),
    ("Munali", "Munali Ward",
     "Construction of a 2x3 classroom block at Kaunda Square Secondary School",
     "2024-02-21"),
    ("Munali", "Chankunkula Ward",
     "Procurement of an ambulance", "2024-02-21"),
]


def category(name):
    text = name.lower()

    if any(x in text for x in [
        "road", "paving", "drainage", "bridge",
        "grading", "gravelling", "junction"
    ]):
        return "Roads and drainage"

    if any(x in text for x in [
        "school", "classroom", "desk", "laboratory"
    ]):
        return "Education"

    if any(x in text for x in [
        "clinic", "hospital", "maternity",
        "mortuary", "health"
    ]):
        return "Health"

    if "police" in text:
        return "Public safety"

    if any(x in text for x in ["market", "trader"]):
        return "Markets and commerce"

    if any(x in text for x in [
        "water", "borehole", "reticulation"
    ]):
        return "Water and sanitation"

    if any(x in text for x in [
        "street light", "solar"
    ]):
        return "Energy and lighting"

    if any(x in text for x in [
        "ambulance", "grader", "compactor",
        "vehicle", "tipper", "paving machine"
    ]):
        return "Equipment and vehicles"

    return "Other community infrastructure"


def read_projects():
    with PROJECTS_FILE.open(
        encoding="utf-8-sig",
        newline="",
    ) as file:
        return list(csv.DictReader(file, delimiter="|"))


def add_approved_projects(rows):
    rows = [
        row for row in rows
        if not row["record_id"].startswith(
            "LCC-CDF-APPROVED-2024-"
        )
    ]

    for number, item in enumerate(APPROVED_2024, start=1):
        constituency, ward, name, approval_date = item

        row = {field: "" for field in PROJECT_FIELDS}

        notes = (
            "Verified from the official 2024 constituency "
            "approval document. The available source did not "
            "report a project-specific budget, disbursement, "
            "expenditure, contractor, beneficiaries, completion "
            "percentage or completion date."
        )

        if not ward:
            notes += (
                " The ward was unclear in the scanned source "
                "and was left blank."
            )

        row.update({
            "record_id": (
                f"LCC-CDF-APPROVED-2024-{number:03d}"
            ),
            "financial_year": "2024",
            "constituency": constituency,
            "ward": ward,
            "project_name": name,
            "project_category": category(name),
            "project_description": name,
            "project_status": "Approved",
            "approval_date": approval_date,
            "source_title": (
                f"{constituency} Constituency 2024 "
                "CDF Project Approval"
            ),
            "source_url": PUBLICATIONS_URL,
            "date_accessed": DATE_ACCESSED,
            "notes": notes,
        })

        rows.append(row)

    return rows


def write_projects(rows):
    with PROJECTS_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=PROJECT_FIELDS,
            delimiter="|",
        )
        writer.writeheader()
        writer.writerows(rows)


def write_notes():
    text = """# CDF Verification Notes

## Sources

The final datasets use official Lusaka City Council budget documents, financial statements, constituency approval documents, the 2025 community-project schedule, and the deferred-project schedule. Source documents, extracted text, OCR text, URLs and the source manifest are retained with the project.

## Project verification

The 2025 project schedule produced 110 planned project records covering all seven Lusaka constituencies. Project names, wards and approved amounts were taken from the official schedule.

The 2024 approved-project records include only projects whose names, constituencies and approval details were sufficiently readable in the available scanned documents. Project-specific financial and implementation fields remain blank where the sources did not report them.

The deferred-project schedule produced 112 records. Status is recorded as Deferred because the source states that the projects were not approved due to insufficient funding. Some ward cells remain blank because OCR did not preserve enough table structure to identify the ward confidently. No ward was guessed.

## Source discrepancies

The sum of the 2025 Kabwata project amounts is ZMW 16,789,272, while the printed source total is ZMW 16,789,271. Difference: ZMW 1.

The sum of the 2025 Kanyama project amounts is ZMW 17,001,860, while the printed source total is ZMW 17,001,859. Difference: ZMW 1.

The sum of the 2025 Munali project amounts is ZMW 17,656,230, while the printed source total is ZMW 17,656,232. Difference: ZMW 2.

The 2024 CDF subprogramme table reports Community Projects of ZMW 122,236,211 and a total CDF allocation of ZMW 214,449,494. A nearby narrative mentions approximately ZMW 128.3 million for community projects. The dataset retains the exact subprogramme table value.

## Missing financial values

Blank values mean the field was not reported in the available official source. A blank value does not mean zero.

Funding receipts and fixed-asset acquisition figures are recorded separately from approved budget allocations to avoid presenting receipts or specific asset expenditure as total programme expenditure.
"""

    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    NOTES_FILE.write_text(text, encoding="utf-8")


def run_qa(projects):
    with ALLOCATIONS_FILE.open(
        encoding="utf-8-sig",
        newline="",
    ) as file:
        allocations = list(
            csv.DictReader(file, delimiter="|")
        )

    valid_statuses = {
        "Planned",
        "Approved",
        "Deferred",
        "Under construction",
        "Near completion",
        "Completed",
        "Handed over",
    }

    duplicate_keys = set()
    seen = set()

    for row in projects:
        key = (
            row["financial_year"],
            row["constituency"].lower(),
            row["ward"].lower(),
            re.sub(
                r"\s+",
                " ",
                row["project_name"].lower(),
            ).strip(),
        )

        if key in seen:
            duplicate_keys.add(key)

        seen.add(key)

    missing_sources = sum(
        not row["source_title"] or not row["source_url"]
        for row in projects
    )

    invalid_statuses = sorted({
        row["project_status"]
        for row in projects
        if row["project_status"] not in valid_statuses
    })

    status_counts = {}

    for row in projects:
        status = row["project_status"]
        status_counts[status] = (
            status_counts.get(status, 0) + 1
        )

    lines = [
        "CDF FINAL QUALITY REPORT",
        "",
        f"Project records: {len(projects)}",
        f"Project columns: {len(PROJECT_FIELDS)}",
        f"Allocation records: {len(allocations)}",
        f"Allocation columns: {len(allocations[0])}",
        f"Duplicate project keys: {len(duplicate_keys)}",
        f"Projects missing source information: {missing_sources}",
        f"Invalid project statuses: {invalid_statuses}",
        "",
        "Project status counts:",
    ]

    for status in sorted(status_counts):
        lines.append(
            f"- {status}: {status_counts[status]}"
        )

    passed = (
        len(PROJECT_FIELDS) == 20
        and len(allocations[0]) == 12
        and len(duplicate_keys) == 0
        and missing_sources == 0
        and not invalid_statuses
    )

    lines.extend([
        "",
        f"Final structural validation: "
        f"{'PASS' if passed else 'CHECK'}",
        "",
        "Blank financial fields mean not reported, not zero.",
        "Known source discrepancies are documented in "
        "metadata/cdf_verification_notes.md.",
    ])

    report = "\n".join(lines)
    QA_FILE.write_text(report, encoding="utf-8")

    print(report)


def main():
    projects = read_projects()
    projects = add_approved_projects(projects)
    write_projects(projects)
    write_notes()
    run_qa(projects)

    print(f"\nProjects file: {PROJECTS_FILE}")
    print(f"Notes file: {NOTES_FILE}")
    print(f"QA report: {QA_FILE}")


if __name__ == "__main__":
    main()