import { useEffect, useState } from "react";
import { getMenu, getRestaurants, Restaurant, Dish } from "./api";

export default function App() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [menu, setMenu] = useState<Dish[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split("T")[0]
  );
  const [selectedRestaurant, setSelectedRestaurant] = useState<number | "">("");

  useEffect(() => {
    getRestaurants().then(setRestaurants);
  }, []);

  useEffect(() => {
    getMenu(selectedDate).then(setMenu);
  }, [selectedDate]);

  const filteredMenu = selectedRestaurant
    ? menu.filter((m) => m.r_ID === selectedRestaurant)
    : menu;

  return (
    <div className="min-h-screen bg-slate-50 text-gray-800 px-6 py-8">
      {/* HEADER */}
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">🍽️ Today's Menus</h1>
        <p className="text-gray-500">Check what’s served nearby</p>
      </header>

      {/* FILTER BAR */}
      <div className="flex flex-wrap gap-4 mb-8 items-center">
        <div>
          <label className="text-sm text-gray-600 block mb-1">Date</label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <div>
          <label className="text-sm text-gray-600 block mb-1">Restaurant</label>
          <select
            value={selectedRestaurant}
            onChange={(e) =>
              setSelectedRestaurant(
                e.target.value ? Number(e.target.value) : ""
              )
            }
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="">All Restaurants</option>
            {restaurants.map((r) => (
              <option key={r.r_ID} value={r.r_ID}>
                {r.Name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* MENU GRID */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {filteredMenu.length > 0 ? (
          filteredMenu.map((dish) => (
            <div
              key={dish.s_ID}
              className="bg-white p-4 rounded-xl shadow hover:shadow-md transition"
            >
              <h2 className="text-lg font-semibold text-slate-900">
                {dish.Name}
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                {dish.Restaurant} — {dish.Datum}
              </p>
              <p className="text-blue-600 font-semibold mt-2">
                {dish.Preis.toFixed(2)} €
              </p>
            </div>
          ))
        ) : (
          <p className="text-gray-500">No menu data available for this day.</p>
        )}
      </div>
    </div>
  );
}

