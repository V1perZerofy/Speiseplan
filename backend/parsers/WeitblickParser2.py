import pymupdf
import re
import datetime
from backend.database import SessionLocal
from backend.models import Speisen, Restaurant


class WeitblickParser:
    def __init__(self, pdf_path: str, debug: bool = False):
        self.pdf_path = pdf_path
        self.restaurant_name = "Weitblick"
        self.debug = debug
        
    def read_rectangles(self, rects):
        doc = pymupdf.open(self.pdf_path)
        page = doc[0]
        menu = []
        for rect in rects:
            text = page.get_textbox(rect)
            menu.append(text)
        return menu

    def get_anchors(self):
        WEEKDAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
        doc = pymupdf.open(self.pdf_path)
        page = doc[0]
        all_y0 = []
        all = []
        res = []
        for day in WEEKDAYS:
            matches = page.search_for(day)
            for i, match in enumerate(matches):
                all.append(match)
                all_y0.append(match.y0)
        avg_y0 = sum(all_y0) / len(all_y0)
        for match in all:
            if -10 < (match.y0 - avg_y0) < 10:
                tmp = ((match.x0 + match.x1) / 2, match.y1)
                res.append(tmp)
        return res

    def build_rects(self, anchors):
        res = []
        for anchor in anchors:
            tmp = pymupdf.Rect(int(anchor[0]) - 76, int(anchor[1]) + 1, int(anchor[0]) + 76, 497)
            res.append(tmp)
        return res

    def cleanup_menu(self, day_menus):
        structured_menu = {}
        pattern = r"(.*?\d{1,3}(?:[.,]\d{2})\s*€?)"
        for i, day_menu in enumerate(day_menus):
            structured_menu[i] = []
            day_menu = day_menu.strip().replace("€", "").replace("\n", ", ").replace(" | ", ", ").replace("  ", " ").replace(" ,", ",").replace("1,50m", "")
            if self.debug:
                print(f"__________________{i}___________")
                print(day_menu)
                print("_________________________________")
            parts = re.split(pattern, day_menu)

            for part in parts:
                if part != "":
                    part = re.sub(r"^[,\s]+", "", part)
                    structured_menu[i].append(part)
        return structured_menu
            
    def split_name_price(self, s: str) -> tuple[str, float]:
        m = re.search(r"(\d{1,3}[.,]\d{2})\s*€?", s)
        if not m:
            return s.strip(), 0.0
        price = float(m.group(1).replace(",", "."))
        name = s[: m.start()].strip()
        return name, price

    def write_to_db(self, menu: dict[int, list[str]]):
        db = SessionLocal()
        restaurant = db.query(Restaurant).filter_by(Name=self.restaurant_name).first()
        if not restaurant:
            restaurant = Restaurant(Name=self.restaurant_name)
            db.add(restaurant)
            db.commit()
            db.refresh(restaurant)

        for i, items in menu.items():
            for item in items:
                name, price = self.split_name_price(item)
                dish_date = datetime.date.today() + datetime.timedelta(days=i)
                dish = Speisen(
                    Name=name,
                    Preis=price,
                    Datum=dish_date,
                    r_ID=restaurant.r_ID,
                )
                db.add(dish)

        db.commit()
        db.close()
        print(f"Saved weekly menu for {self.restaurant_name}")


    def run(self):
        anchors = self.get_anchors()
        self.write_to_db(self.cleanup_menu(self.read_rectangles(self.build_rects(anchors))))


if __name__ == "__main__":
    WeitblickParser("backend/menus/Wochenkarte.pdf", False).run()
