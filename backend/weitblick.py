from backend.parsers.WeitblickParser import WeitblickParser
from backend.scripts.scraper_weitblick import download_weitblick_menu

def updateWeitblick():
    try:
        download_weitblick_menu()
        WeitblickParser("backend/menus/Wochenkarte.pdf").run()
    except Exception as e:
        print(f"[Update Error] {e}")

if __name__ == "__main__":
    updateWeitblick()
