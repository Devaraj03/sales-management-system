import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(value));
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

export default function OrderHistory() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      try {
        const resp = await api.get("/api/orders");
        setOrders(resp.data);
      } catch (err) {
        setError("Couldn't load your orders.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div className="loading-state">Loading…</div>;
  if (error) return <div className="error-banner">{error}</div>;

  if (orders.length === 0) {
    return <div className="empty-state">You haven't submitted any orders yet.</div>;
  }

  return (
    <div className="card-list">
      {orders.map((o) => (
        <div key={o.id} className="list-card" onClick={() => navigate(`/history/${o.id}`)}>
          <div>
            <div className="list-card-title">{o.customer_name}</div>
            <div className="list-card-sub">
              {formatDate(o.created_at)} · <span className={`status-pill status-${o.status}`}>{o.status}</span>
            </div>
          </div>
          <div className="list-card-trailing">{formatCurrency(o.total_amount)}</div>
        </div>
      ))}
    </div>
  );
}
