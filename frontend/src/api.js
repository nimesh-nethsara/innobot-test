const API_BASE_URL = "http://127.0.0.1:5000/api";

export async function apiFetch(endpoint, options = {}) {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  
  const headers = {
    "Content-Type": "application/json",
    // Attach X-User-Id for backend authentication
    ...(user.id && { "X-User-Id": user.id.toString() }),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Something went wrong");
  }

  return data;
}