import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(value));
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const timeout = setTimeout(() => {
      loadOrders(search);
    }, 300);
    return () => clearTimeout(timeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search]);

  async function loadOrders(searchTerm) {
    setLoading(true);
    setError("");
    try {
      const params = searchTerm ? { search: searchTerm } : {};
      const resp = await api.get("/api/orders", { params });
      setOrders(resp.data);
    } catch (err) {
      setError("Couldn't load orders.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1 className="page-title">Orders</h1>
      <p className="page-subtitle">All orders placed by your sales team.</p>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Search by customer name…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {error && <div className="error-banner">{error}</div>}
      {loading && <div className="loading-state">Loading…</div>}

      {!loading && orders.length === 0 && (
        <div className="empty-state">No orders match your search.</div>
      )}

      {!loading && orders.length > 0 && (
        <table className="ledger-table">
          <thead>
            <tr>
              <th>Customer</th>
              <th>Salesman</th>
              <th>Date</th>
              <th>Status</th>
              <th className="num">Total</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id} onClick={() => navigate(`/orders/${o.id}`)}>
                <td>{o.customer_name}</td>
                <td>{o.salesman_name}</td>
                <td>{formatDate(o.created_at)}</td>
                <td>
                  <span className={`status-pill status-${o.status}`}>{o.status}</span>
                </td>
                <td className="num">{formatCurrency(o.total_amount)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
