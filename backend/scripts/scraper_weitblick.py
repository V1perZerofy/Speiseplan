import requests
from pathlib import Path

def download_weitblick_menu():
    url = "https://www.weitblick-example.de/wochenkarte.pdf"
    menu_dir = Path(__file__).resolve().parent.parent / "menus"
    menu_dir.mkdir(exist_ok=True)
    target = menu_dir / "Wochenkarte.pdf"

    print(f"Downloading Weitblick Wochenkarte from {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(target, "wb") as f:
            f.write(response.content)
        print(f"Saved {target.name}")
    except Exception as e:
        print(f"Failed to fetch Weitblick Wochenkarte: {e}")

if __name__ == "__main__":
    download_weitblick_menu()

