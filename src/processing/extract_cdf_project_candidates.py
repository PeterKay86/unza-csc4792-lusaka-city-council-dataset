import csv
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "cdf"
    / "db-unza26-csc4792-lusaka_city_council_cdf_articles.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "cdf"
    / "db-unza26-csc4792-lusaka_city_council_cdf_project_candidates.csv"
)

OUTPUT_FIELDS = [
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


def clean_text(value):
    """Remove excessive spaces and line breaks."""

    return re.sub(r"\s+", " ", str(value or "")).strip()


def identify_category(text):
    """Determine the project category from keywords."""

    text = text.lower()

    category_rules = [
        (
            "Health infrastructure",
            [
                "hospital",
                "clinic",
                "health facility",
                "maternity",
                "mortuary",
                "health post",
            ],
        ),
        (
            "Education infrastructure",
            [
                "school",
                "classroom",
                "laboratory",
                "bursary",
                "student desk",
            ],
        ),
        (
            "Water and sanitation",
            [
                "water",
                "borehole",
                "reticulation",
                "sanitation",
                "toilet",
                "ablution",
                "drain",
                "drainage",
            ],
        ),
        (
            "Road infrastructure",
            [
                "road",
                "bridge",
                "culvert",
                "paving",
                "paved",
            ],
        ),
        (
            "Market infrastructure",
            [
                "market",
                "trading shelter",
                "market shelter",
            ],
        ),
        (
            "Skills development",
            [
                "skills centre",
                "skills center",
                "training centre",
                "training center",
            ],
        ),
        (
            "Public safety",
            [
                "police post",
                "fire station",
                "security",
            ],
        ),
        (
            "Community infrastructure",
            [
                "community centre",
                "community center",
                "civic centre",
                "civic center",
                "sports facility",
            ],
        ),
    ]

    for category, keywords in category_rules:
        if any(keyword in text for keyword in keywords):
            return category

    return "Other community development"


def identify_status(text):
    """Determine the reported project status from keywords."""

    text = text.lower()

    status_rules = [
        (
            "Handed over",
            [
                "officially handed over",
                "handed over",
            ],
        ),
        (
            "Completed",
            [
                "completed",
                "commissioned",
                "officially opened",
            ],
        ),
        (
            "Near completion",
            [
                "nearing completion",
                "almost complete",
                "near completion",
            ],
        ),
        (
            "Under construction",
            [
                "under construction",
                "construction underway",
                "works underway",
                "ongoing construction",
                "being constructed",
            ],
        ),
        (
            "Approved",
            [
                "approved project",
                "projects approved",
                "approved cdf",
            ],
        ),
        (
            "Planned",
            [
                "planned project",
                "proposed project",
                "set to begin",
            ],
        ),
    ]

    for status, keywords in status_rules:
        if any(keyword in text for keyword in keywords):
            return status

    return "Unknown"


def extract_completion_percentage(text):
    """Extract a stated completion percentage, if available."""

    patterns = [
        r"(\d{1,3})\s*%\s+complete",
        r"completion\s+(?:rate\s+)?(?:of\s+)?(\d{1,3})\s*%",
        r"(\d{1,3})\s*%\s+completion",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            percentage = int(match.group(1))

            if 0 <= percentage <= 100:
                return percentage

    return ""


def shorten_description(text, maximum_length=500):
    """Create a concise description from the article text."""

    text = clean_text(text)

    if len(text) <= maximum_length:
        return text

    shortened = text[:maximum_length].rsplit(" ", 1)[0]

    return f"{shortened}..."


def read_articles():
    """Read the scraped CDF articles."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(
            csv_file,
            delimiter="|",
        )

        return list(reader)


def create_candidates(articles):
    """Convert articles into structured project candidates."""

    candidates = []

    for number, article in enumerate(
        articles,
        start=1,
    ):
        title = clean_text(article.get("title"))
        article_text = clean_text(article.get("article_text"))
        combined_text = f"{title} {article_text}"

        publication_date = clean_text(
            article.get("publication_date")
        )

        financial_year = (
            publication_date[:4]
            if len(publication_date) >= 4
            else ""
        )

        candidate = {
            "record_id": f"LCC-CDF-CAND-{number:03d}",
            "financial_year": financial_year,
            "constituency": clean_text(
                article.get("constituencies")
            ),
            "ward": clean_text(article.get("wards")),
            "project_name": title,
            "project_category": identify_category(combined_text),
            "project_description": shorten_description(article_text),
            "approved_budget_zmw": "",
            "amount_disbursed_zmw": "",
            "amount_spent_zmw": "",
            "project_status": identify_status(combined_text),
            "completion_percentage": extract_completion_percentage(
                combined_text
            ),
            "approval_date": "",
            "completion_date": "",
            "beneficiaries": "",
            "contractor": "",
            "source_title": title,
            "source_url": clean_text(article.get("source_url")),
            "date_accessed": clean_text(
                article.get("date_accessed")
            ),
            "notes": (
                "Automatically extracted candidate; "
                "requires manual verification."
            ),
        }

        candidates.append(candidate)

    return candidates


def save_candidates(candidates):
    """Save candidates using the required pipe separator."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=OUTPUT_FIELDS,
            delimiter="|",
            quoting=csv.QUOTE_MINIMAL,
        )

        writer.writeheader()
        writer.writerows(candidates)

    print(f"Saved {len(candidates)} project candidates to:")
    print(OUTPUT_FILE)


def main():
    """Run the project-candidate extraction process."""

    print("Reading scraped CDF articles...")

    articles = read_articles()

    print(f"Articles read: {len(articles)}")

    candidates = create_candidates(articles)

    save_candidates(candidates)

    print("Project candidate extraction completed.")


if __name__ == "__main__":
    main()