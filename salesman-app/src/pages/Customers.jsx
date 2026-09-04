import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const timeout = setTimeout(() => {
      load(search);
    }, 300);
    return () => clearTimeout(timeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search]);

  async function load(searchTerm) {
    setLoading(true);
    setError("");
    try {
      const params = searchTerm ? { search: searchTerm } : {};
      const resp = await api.get("/api/customers", { params });
      setCustomers(resp.data);
    } catch (err) {
      setError("Couldn't load customers.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <input
        className="search-input"
        type="text"
        placeholder="Search customers…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {error && <div className="error-banner">{error}</div>}
      {loading && <div className="loading-state">Loading…</div>}

      {!loading && customers.length === 0 && (
        <div className="empty-state">No customers found.</div>
      )}

      <div className="card-list">
        {customers.map((c) => (
          <div key={c.id} className="list-card" onClick={() => navigate(`/customers/${c.id}`)}>
            <div>
              <div className="list-card-title">{c.name}</div>
              <div className="list-card-sub">{c.phone || c.email || "No contact info"}</div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
