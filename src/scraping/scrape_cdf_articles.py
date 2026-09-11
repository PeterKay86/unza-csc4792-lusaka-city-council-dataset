import csv
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
import urllib3
from bs4 import BeautifulSoup


# The official LCC website currently has an expired SSL certificate.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://www.lcc.gov.zm"
CDF_CATEGORY_ID = 56

API_URL = (
    f"{BASE_URL}/wp-json/wp/v2/posts"
    f"?categories={CDF_CATEGORY_ID}"
    f"&per_page=100"
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "cdf"
    / "db-unza26-csc4792-lusaka_city_council_cdf_articles.csv"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/152.0 Safari/537.36"
    )
}

CONSTITUENCIES = [
    "Chawama",
    "Kabwata",
    "Kanyama",
    "Lusaka Central",
    "Mandevu",
    "Matero",
    "Munali",
]


def clean_html(html_content):
    """Convert HTML content into clean plain text."""

    soup = BeautifulSoup(html_content or "", "html.parser")

    for unwanted_element in soup.select(
        "script, style, nav, footer, form, iframe"
    ):
        unwanted_element.decompose()

    text = soup.get_text(" ", strip=True)

    return re.sub(r"\s+", " ", text).strip()


def validate_lcc_url(url):
    """Ensure that only the official LCC website is accessed."""

    parsed_url = urlparse(url)

    allowed_domains = {
        "lcc.gov.zm",
        "www.lcc.gov.zm",
    }

    if parsed_url.netloc not in allowed_domains:
        raise ValueError(f"Blocked non-LCC URL: {url}")


def download_cdf_posts():
    """Download CDF posts from the official LCC WordPress API."""

    validate_lcc_url(API_URL)

    print("Downloading CDF records from the official LCC API...")
    print(API_URL)

    response = requests.get(
        API_URL,
        headers=HEADERS,
        timeout=60,
        verify=False,
    )

    response.raise_for_status()

    posts = response.json()

    if not isinstance(posts, list):
        raise ValueError("The API response was not a list of posts.")

    print(f"Downloaded {len(posts)} CDF articles.")

    return posts


def extract_constituencies(text):
    """Identify Lusaka constituencies mentioned in the article."""

    matches = []

    for constituency in CONSTITUENCIES:
        if constituency.lower() in text.lower():
            matches.append(constituency)

    return "; ".join(matches)


def extract_wards(text):
    """Identify wards and ward numbers mentioned in the article."""

    ward_patterns = [
        r"\b[A-Za-z][A-Za-z\- ]{0,30}\s+Ward\s+\d+\b",
        r"\bWard\s+\d+\b",
    ]

    matches = set()

    for pattern in ward_patterns:
        found_wards = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        for ward in found_wards:
            cleaned_ward = re.sub(
                r"\s+",
                " ",
                ward,
            ).strip()

            matches.add(cleaned_ward)

    return "; ".join(sorted(matches))


def process_posts(posts):
    """Transform API posts into dataset records."""

    records = []

    for number, post in enumerate(posts, start=1):

        title_html = post.get("title", {}).get("rendered", "")
        content_html = post.get("content", {}).get("rendered", "")

        title = clean_html(title_html)
        article_text = clean_html(content_html)

        publication_date = post.get("date", "")[:10]
        source_url = post.get("link", "")
        source_post_id = post.get("id", "")

        combined_text = f"{title} {article_text}"

        record = {
            "record_id": f"LCC-CDF-ARTICLE-{number:03d}",
            "source_post_id": source_post_id,
            "publication_date": publication_date,
            "title": title,
            "constituencies": extract_constituencies(combined_text),
            "wards": extract_wards(combined_text),
            "article_text": article_text,
            "source_url": source_url,
            "date_accessed": datetime.now().strftime("%Y-%m-%d"),
        }

        records.append(record)

    return records


def save_records(records):
    """Save the records using the required pipe separator."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "record_id",
        "source_post_id",
        "publication_date",
        "title",
        "constituencies",
        "wards",
        "article_text",
        "source_url",
        "date_accessed",
    ]

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
            delimiter="|",
            quoting=csv.QUOTE_MINIMAL,
        )

        writer.writeheader()
        writer.writerows(records)

    print()
    print(f"Saved {len(records)} records to:")
    print(OUTPUT_FILE)


def main():
    """Run the complete CDF data extraction process."""

    print("Starting Lusaka City Council CDF scraper...")
    print()

    try:
        posts = download_cdf_posts()
        records = process_posts(posts)
        save_records(records)

        print()
        print("Scraping completed successfully.")

    except requests.RequestException as error:
        print()
        print(f"Website request failed: {error}")

    except ValueError as error:
        print()
        print(f"Data validation failed: {error}")


if __name__ == "__main__":
    main()