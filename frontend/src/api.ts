const API_BASE = "http://127.0.0.1:8000";

export class Dish {
  s_ID: number;
  Name: string;
  Preis: number;
  Datum: string;
  r_ID: number;
  Restaurant: string;
};

export class Restaurant {
  r_ID: number;
  Name: string;
};

export async function getRestaurants(): Promise<Restaurant[]> {
  const res = await fetch(`${API_BASE}/restaurants`);
  if (!res.ok) throw new Error("Failed to fetch restaurants");
  return res.json();
}

export async function getMenu(restaurant: string, date?: string): Promise<Dish[]> {
  const url = date ? `${API_BASE}/menu?restaurant_str=${restaurant}&date_str=${date}` : `${API_BASE}/menu`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch menu");
  return res.json();
}
