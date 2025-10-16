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

    def remove_weekdays(self, text: str) -> str:
        WEEKDAY_PATTERN = re.compile(
            r"\b(?:Mo|Di|Mi|Do|Fr|Sa|So|Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag"
            r"|Mon(?:day)?|Tue(?:sday)?|Wed(?:nesday)?|Thu(?:rsday)?|Fri(?:day)?|Sat(?:urday)?|Sun(?:day)?)\b",
            re.IGNORECASE,
        )
        return WEEKDAY_PATTERN.sub("", text).strip()

    def clean_text(self, text: str) -> str:
        """Remove restaurant header, footer text, and redundant parts."""
        text = re.sub(r"WEITBLICK.*?Market", "", text, flags=re.IGNORECASE)
        text = re.sub(r"Von\s+\d{1,2}\.\s*\w+\s+bis\s+\d{1,2}\.\s*\w+", "", text, flags=re.IGNORECASE)
        text = re.sub(r"Tagesaktuelle.*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"Ab sofort.*Barzahlung.*", "", text, flags=re.IGNORECASE)
        text = self.remove_weekdays(text)
        return text.strip()

    def crop_pdf(self) -> dict[str, list[str]]:
        doc = pymupdf.open(self.pdf_path)
        page = doc[0]
        rect = page.rect
        structured_menu = {}

        # tuned margins for Weitblick layout
        top_margin = 96
        bottom_margin = 44
        horizontal_margin = 60
        between_margin = 0
        width_per_day = 173
        print(rect.width)
        for i in range(5):
            left = rect.x0 + horizontal_margin + i * width_per_day - (between_margin if i > 0 else 0)
            right = left + width_per_day + (between_margin if i < 4 else 0)
            top = rect.y0 + top_margin
            bottom = rect.y1 - bottom_margin
            area = pymupdf.Rect(left, top, right, bottom)

            blocks = [
                b for b in page.get_text("blocks")
                if b[0] < area.x1 and b[2] > area.x0 and b[1] < area.y1 and b[3] > area.y0
            ]
            blocks.sort(key=lambda b: (b[1], b[0]))
            cropped_text = "\n".join([b[4] for b in blocks])

            cropped_text = self.clean_text(cropped_text)

            if self.debug:
                print(f"===== DAY {i+1} =====")
                print(cropped_text)
                print("=====================\n")
            
            cropped_text = self.remove_weekdays(cropped_text)

            # dish-level cleanup restored
            parts = re.split(r'(?=\d{1,2)[.,]\d{2}\s*€', cropped_text)
            
            items = []
            for part in parts:
                cleaned = (part.strip()
                           .replace("\n", " ")
                           .replace(" | ", ", ")
                           .replace("  ", " ")
                )
                if cleaned:
                    items.append(cleaned)


            day_name = f"Day {i+1}"
            structured_menu[day_name] = []
            
            if items and "salatbar" in items[0].lower():
                try:
                    for j in range(min(2, len(items))):
                        parts = items[j].split()
                        if len(parts) >= 2:
                            price = " ".join(parts[-2:]) + "€"
                            structured_menu[day_name].append(f"Salatbar {price}")
                except Exception:
                    pass
                start_index = 2
            else:
                start_index = 0


            for entry in items[start_index:]:
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
    parser = WeitblickParser("backend/menus/Wochenkarte.pdf", debug=True)
    parser.run()

