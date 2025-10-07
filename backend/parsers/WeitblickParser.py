import pymupdf
import re
import datetime
from backend.database import SessionLocal
from backend.models import Speisen, Restaurant


class WeitblickParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.restaurant_name = "Weitblick"

    def remove_weekdays(self, text: str) -> str:
        WEEKDAY_PATTERN = re.compile(
            r"\b(?:Mo|Di|Mi|Do|Fr|Sa|So|Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag"
            r"|Mon(?:day)?|Tue(?:sday)?|Wed(?:nesday)?|Thu(?:rsday)?|Fri(?:day)?|Sat(?:urday)?|Sun(?:day)?)\b",
            re.IGNORECASE,
        )
        return WEEKDAY_PATTERN.sub("", text).strip()

    def crop_pdf(self) -> dict[str, list[str]]:
        doc = pymupdf.open(self.pdf_path)
        page = doc[0]
        puffer = 60
        structured_menu = {}

        for i in range(5):
            rect = page.rect
            width_per_day = (rect.width - puffer * 2) / 5
            left = rect.x0 + puffer + i * width_per_day
            right = left + width_per_day
            new_rect = pymupdf.Rect(left, rect.y0 + puffer, right, rect.y1 - puffer)

            blocks = page.get_text("blocks")
            blocks_in_area = [
                b for b in blocks
                if b[0] >= new_rect.x0 and b[2] <= new_rect.x1
                and b[1] >= new_rect.y0 and b[3] <= new_rect.y1
            ]
            blocks_in_area.sort(key=lambda b: (b[1], b[0]))
            cropped_text = "\n".join([b[4] for b in blocks_in_area])

            cropped_text = self.remove_weekdays(cropped_text)
            items = [
                item.strip()
                    .replace("\n", " ")
                    .replace("  ", " ")
                    .replace(" I ", ", ")
                for item in cropped_text.split("€")
                if item.strip()
            ]

            day_name = f"Day {i+1}"
            structured_menu[day_name] = []
            if len(items) >= 2:
                try:
                    salatbar = (
                        "Salatbar "
                        + items[0].split(" ")[-2]
                        + " "
                        + items[0].split(" ")[-1]
                        + "€"
                    )
                    salatbar1 = (
                        "Salatbar "
                        + items[1].split(" ")[-2]
                        + " "
                        + items[1].split(" ")[-1]
                        + "€"
                    )
                    structured_menu[day_name].append(salatbar)
                    structured_menu[day_name].append(salatbar1)
                except Exception:
                    pass

            for entry in items[2:]:
                structured_menu[day_name].append(entry + "€")

        return structured_menu

    def split_name_price(self, s: str) -> tuple[str, float]:
        m = re.search(r"(\d{1,3}[.,]\d{2})\s*€?", s)
        if not m:
            return s.strip(), 0.0
        price = float(m.group(1).replace(",", "."))
        name = s[: m.start()].strip()
        return name, price

    def write_to_db(self, menu: dict[str, list[str]]):
        db = SessionLocal()
        restaurant = db.query(Restaurant).filter_by(Name=self.restaurant_name).first()
        if not restaurant:
            restaurant = Restaurant(Name=self.restaurant_name)
            db.add(restaurant)
            db.commit()
            db.refresh(restaurant)

        for day, items in menu.items():
            for item in items:
                name, price = self.split_name_price(item)
                day_number = int(day.split(" ")[1]) - 1
                dish_date = datetime.date.today() + datetime.timedelta(days=day_number)
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
        print(f"Parsing {self.pdf_path} ...")
        menu = self.crop_pdf()
        self.write_to_db(menu)
        print(f"Completed parsing for {self.restaurant_name}")


if __name__ == "__main__":
    parser = WeitblickParser("backend/menus/Wochenkarte.pdf")
    parser.run()

