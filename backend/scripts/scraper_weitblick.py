import requests
from pathlib import Path
import pymupdf

def download_weitblick_menu():
    url = "https://weitblick-eventlocation.de/uploads/wochenkarten/Wochenkarte.pdf"
    menu_dir = Path(__file__).resolve().parent.parent / "menus"
    menu_dir.mkdir(exist_ok=True)
    target_full = menu_dir / "Wochenkarte_full.pdf"
    target_firstpage = menu_dir / "Wochenkarte.pdf"

    print(f"Downloading Weitblick Wochenkarte from {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(target_full, "wb") as f:
            f.write(response.content)
        print(f"Saved full PDF: {target_full.name}")

        with pymupdf.open(target_full) as doc:
            first_page = pymupdf.open()
            first_page.insert_pdf(doc, from_page=0, to_page=0)
            first_page.save(target_firstpage)
            first_page.close()

        print(f"Saved first page as: {target_firstpage.name}")
        target_full.unlink(missing_ok=True)

    except Exception as e:
        print(f"Failed to fetch Weitblick Wochenkarte: {e}")

if __name__ == "__main__":
    download_weitblick_menu()

