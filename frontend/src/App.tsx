import { useEffect, useState } from "react";
import { getMenu, getRestaurants, Dish, Restaurant } from "./api.ts";

function useTheme() {
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    const saved = localStorage.getItem("theme");
    if (saved === "light" || saved === "dark") return saved;
    return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  });
  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem("theme", theme);
  }, [theme]);
  return { theme, toggle: () => setTheme(t => (t === "dark" ? "light" : "dark")) };
}

function App() {
  const [menu, setMenu] = useState<Dish[]>([]);
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const { theme, toggle } = useTheme();
  const [selectedDate, setSelectedDate] = useState<string>(
    () => new Date().toISOString().split("T")[0]
  );
  const changeDay = (offset: number) => {
    const newDate = new Date(selectedDate);
    newDate.setDate(newDate.getDate() + offset);
    setSelectedDate(newDate.toISOString().split("T")[0]);
  };
  const setToday = () => {
    setSelectedDate(new Date().toISOString().split("T")[0]);
  };
  const [selectedRestaurant, setSelectedRestaurant] = useState<string>(
    () => "Augustiner"
  );

  useEffect(() => {
    getRestaurants().then(setRestaurants);
  }, []);

  useEffect(() => {
    if (selectedDate) {
      getMenu(selectedRestaurant, selectedDate)
        .then((data) => {
          if (!data || data.length === 0) {
            setMenu([]);
          } else {
            setMenu(data);
          }
        })
        .catch((err) => {
        console.warn("No menu found or fetch failed:", err.message);
        setMenu([]);
      });
    }
  }, [selectedDate]);

  useEffect(() => {
    if (selectedRestaurant) {
      getMenu(selectedRestaurant, selectedDate)
        .then((data) => {
          if (!data || data.length === 0) {
            setMenu([]);
          } else {
            setMenu(data);
          }
        })
        .catch((err) => {
          console.warn("No menu found or fetch failed:", err.message);
          setMenu([]);
        })
    }
  }, [selectedRestaurant]);

  return (
    <div
      className="h-screen grid"
      style={{
        gridTemplateColumns: "220px 1fr",
        gridTemplateAreas: `"nav main"`,
      }}
    >
      <nav
        className="bg-gray-100 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 p-4 flex flex-col justify-between"
        style={{ gridArea: "nav" }}
      >
        <div>
          <h2 className="text-xl font-bold mb-4 text-gray-800 dark:text-gray-100">Restaurants</h2>
          <ul className="space-y-2">
            {restaurants.map((r) => (
              <li
                key={r.r_ID}
                onClick={() => setSelectedRestaurant(r.Name)}
                className={`cursor-pointer p-2 rounded text-gray-700 dark:text-gray-300 
                  hover:bg-gray-200 dark:hover:bg-gray-800
                  ${selectedRestaurant === r.Name ? "bg-gray-300 dark:bg-gray-700 font-semibold" : ""}`}
              >
                {r.Name}
              </li>
            ))}
            <li>
              <input type="date" value={selectedDate} onChange={(e) => setSelectedDate(e.target.value)} className="mb-4 p-2 border rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"/>
            </li>
            <li>
              <button onClick={() => changeDay(-1)} className="px-3 py-1 rounded text-gray-900 dark:text-gray-100 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600"> - </button>
              <button onClick={() => setToday()} className="px-3 py-1 rounded text-gray-900 dark:text-gray-100 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600"> Heute </button>
              <button onClick={() => changeDay(1)} className="px-3 py-1 rounded text-gray-900 dark:text-gray-100 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600"> + </button>
            </li>
          </ul>
        </div>
        <button
          onClick={toggle}
          className="mt-4 p-2 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-gray-100"
        >
          {theme === "dark" ? "Light" : "Dark"} Mode
        </button>
      </nav>

      <main className="p-4 overflow-y-auto bg-gray-50 dark:bg-gray-950" style={{ gridArea: "main" }}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {menu.map((d) => (
            <Card key={d.s_ID} name={d.Name} price={d.Preis} date={d.Datum} />
          ))}
        </div>
      </main>
    </div>
  );
}

function Card({ name, price, date }: { name: string; price: number; date: string }) {
  return (
    <div className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700">
      <h5 className="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{name}</h5>
      <p className="text-sm text-gray-500 dark:text-gray-400">{date}</p>
      <p className="text-gray-700 dark:text-gray-200">{price} €</p>
    </div>
  );
}

export default App;
