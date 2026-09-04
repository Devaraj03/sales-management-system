import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(value));
}

export default function Products() {
  const [products, setProducts] = useState([]);
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
      const resp = await api.get("/api/products", { params });
      setProducts(resp.data);
    } catch (err) {
      setError("Couldn't load products.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <input
        className="search-input"
        type="text"
        placeholder="Search products…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {error && <div className="error-banner">{error}</div>}
      {loading && <div className="loading-state">Loading…</div>}

      {!loading && products.length === 0 && (
        <div className="empty-state">No products found.</div>
      )}

      <div className="card-list">
        {products.map((p) => (
          <div key={p.id} className="list-card" onClick={() => navigate(`/products/${p.id}`)}>
            <div>
              <div className="list-card-title">{p.name}</div>
              <div className="list-card-sub">
                {p.sku} · {p.stock_quantity} in stock
              </div>
            </div>
            <div className="list-card-trailing">{formatCurrency(p.price)}</div>
          </div>
        ))}
      </div>
    </>
  );
}
