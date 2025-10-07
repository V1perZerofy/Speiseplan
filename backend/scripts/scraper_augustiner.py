import requests
from pathlib import Path

def download_augustiner_menu():
    url = "https://neuhauser-augustiner.com/speisekarten/Tageskarte.pdf"
    menu_dir = Path(__file__).resolve().parent.parent / "menus"
    menu_dir.mkdir(exist_ok=True)
    target = menu_dir / "TageskarteAugustiner.pdf"

    print(f"Downloading Augustiner Tageskarte from {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(target, "wb") as f:
            f.write(response.content)
        print(f"Saved {target.name}")
    except Exception as e:
        print(f"Failed to fetch Tageskarte Augustiner: {e}")

if __name__ == "__main__":
    download_augustiner_menu()
