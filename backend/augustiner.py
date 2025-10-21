from backend.parsers.AugustinerParser import AugustinerParser
from backend.scripts.scraper_augustiner import download_augustiner_menu

def updateAugustiner():
    try:
        download_augustiner_menu()
        AugustinerParser("backend/menus/TageskarteAugustiner.pdf").run()
    except Exception as e:
        print(f"[Update Error]{e}")

if __name__ == "__main__":
    updateAugustiner()
