import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import api from "../api";

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(value));
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [series, setSeries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [metricsResp, seriesResp] = await Promise.all([
          api.get("/api/dashboard/metrics"),
          api.get("/api/dashboard/sales-over-time"),
        ]);
        setMetrics(metricsResp.data);
        setSeries(
          seriesResp.data.map((p) => ({
            date: p.date,
            total: Number(p.total_sales),
            orders: p.order_count,
          }))
        );
      } catch (err) {
        setError("Couldn't load dashboard data. Try refreshing the page.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <>
      <h1 className="page-title">Dashboard</h1>
      <p className="page-subtitle">A snapshot of sales activity across your team.</p>

      {error && <div className="error-banner">{error}</div>}
      {loading && <div className="loading-state">Loading…</div>}

      {metrics && (
        <div className="metrics-row">
          <div className="metric-card">
            <div className="metric-label">Total sales</div>
            <div className="metric-value">{formatCurrency(metrics.total_sales)}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Total orders</div>
            <div className="metric-value">{metrics.total_orders}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Customers</div>
            <div className="metric-value">{metrics.total_customers}</div>
          </div>
        </div>
      )}

      {!loading && series.length > 0 && (
        <div className="chart-card">
          <h3 style={{ fontSize: 16, marginBottom: 18 }}>Sales over time</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={series} margin={{ top: 4, right: 12, left: 0, bottom: 0 }}>
              <CartesianGrid stroke="#DCE1DC" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 12, fill: "#5B6560" }} tickLine={false} axisLine={{ stroke: "#DCE1DC" }} />
              <YAxis
                tick={{ fontSize: 12, fill: "#5B6560" }}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => `$${v}`}
              />
              <Tooltip
                formatter={(value, name) => (name === "total" ? [formatCurrency(value), "Sales"] : [value, "Orders"])}
                contentStyle={{ fontSize: 13, borderRadius: 4, border: "1px solid #DCE1DC" }}
              />
              <Line type="monotone" dataKey="total" stroke="#1F5C4B" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {!loading && series.length === 0 && !error && (
        <div className="empty-state">No sales recorded yet. Once orders come in, they'll show up here.</div>
      )}
    </>
  );
}
