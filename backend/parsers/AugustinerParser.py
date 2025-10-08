import pdfplumber
import re
import datetime
from backend.database import SessionLocal
from backend.models import Speisen, Restaurant


class AugustinerParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.restaurant_name = "Augustiner"


    def remove_weekdays(self, text: str) -> str:
        """Removes weekday names from text."""
        WEEKDAY_PATTERN = re.compile(
            r"\b(?:Mo|Di|Mi|Do|Fr|Sa|So|Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag"
            r"|Mon(?:day)?|Tue(?:sday)?|Wed(?:nesday)?|Thu(?:rsday)?|Fri(?:day)?|Sat(?:urday)?|Sun(?:day)?)\b",
            re.IGNORECASE,
        )
        return WEEKDAY_PATTERN.sub("", text).strip()

    def read_pdf(self) -> str:
        """Reads text content from all pages of the menu PDF."""
        text = ""
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
        return text


    def process_menu(self, text: str) -> dict[str, list[str]]:
        """Splits text into sections and dish entries."""
        sections = {}
        text = self.remove_weekdays(text)

        if "TAGESKARTE" in text:
            mittagstisch, rest = text.split("TAGESKARTE", 1)
            sections["Mittagstisch"] = mittagstisch.strip()
            if "Dessert" in rest:
                tageskarte, dessert = rest.split("Dessert", 1)
                sections["Tageskarte"] = tageskarte.strip()
                sections["Dessert"] = dessert.strip()
            else:
                sections["Tageskarte"] = rest.strip()
        else:
            sections["All"] = text.strip()

        structured = {}
        for section, block in sections.items():
            # Split by € and clean up formatting
            items = [
                item.strip().replace("\n", " ").replace("  ", " ").replace("❖", "")
                for item in block.split("€")
                if item.strip()
            ]
            structured[section] = [item + " €" for item in items]
        return structured


    def write_to_db(self, menu: dict[str, list[str]]):
        db = SessionLocal()

        # Get or create Restaurant
        restaurant = db.query(Restaurant).filter_by(Name=self.restaurant_name).first()
        if not restaurant:
            restaurant = Restaurant(Name=self.restaurant_name)
            db.add(restaurant)
            db.commit()
            db.refresh(restaurant)

        today = datetime.date.today()

        for section, items in menu.items():
            for item in items:
                # Extract name and price
                m = re.search(r"(\d{1,3}[.,]\d{2})\s*€?", item)
                if m:
                    price = float(m.group(1).replace(",", "."))
                    name = item[: m.start()].strip()
                else:
                    name = item.strip()
                    price = 0.0

                dish = Speisen(
                    Name=name,
                    Preis=price,
                    Datum=today,
                    r_ID=restaurant.r_ID,
                )
                db.add(dish)

        db.commit()
        db.close()


    def run(self):
        print(f"Parsing {self.pdf_path} ...")
        text = self.read_pdf()
        menu = self.process_menu(text)
        self.write_to_db(menu)
        print(f"Completed parsing for {self.restaurant_name}")


if __name__ == "__main__":
    parser = AugustinerParser("backend/menus/TageskarteAugustiner.pdf")
    parser.run()
