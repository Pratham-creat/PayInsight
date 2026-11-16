import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

function Metric({ label, value, accent }) {
  return <article className={`metric ${accent || ""}`}><span>{label}</span><strong>{value ?? "—"}</strong></article>;
}

function App() {
  const [metrics, setMetrics] = useState(null);
  const [payments, setPayments] = useState([]);
  const [selected, setSelected] = useState(null);
  useEffect(() => {
    Promise.all([fetch(`${API}/api/metrics`).then(r => r.json()), fetch(`${API}/api/payments?limit=12`).then(r => r.json())])
      .then(([m, p]) => { setMetrics(m); setPayments(p); });
  }, []);
  const inspect = (payment) => fetch(`${API}/api/payments/${payment.payment_id}/risk`).then(r => r.json()).then(setSelected);
  return <main className="shell">
    <header><div className="brand"><div className="logo">P</div><div><h1>PayInsight</h1><p>Payment intelligence, without the guesswork.</p></div></div><div className="live"><i /> Live data</div></header>
    <section className="hero"><div><p className="eyebrow">Risk operations</p><h2>Know every payment<br /><em>before it moves.</em></h2></div><p className="hero-copy">A clear view of payment health, fraud signals, and merchant performance across your network.</p></section>
    <section className="metrics"><Metric label="Total volume" value={metrics && `$${metrics.total_volume.toLocaleString(undefined, {maximumFractionDigits: 0})}`} /><Metric label="Payments" value={metrics?.total_payments.toLocaleString()} /><Metric label="High risk" value={metrics?.high_risk_payments} accent="warning" /><Metric label="Success rate" value={metrics && `${((metrics.successful_payments / metrics.total_payments) * 100).toFixed(1)}%`} accent="success" /></section>
    <section className="content"><div className="panel"><div className="panel-head"><div><p className="eyebrow">Latest activity</p><h3>Payment stream</h3></div><span className="count">{payments.length} recent</span></div><div className="table-wrap"><table><thead><tr><th>Payment</th><th>Merchant</th><th>Amount</th><th>Status</th><th /></tr></thead><tbody>{payments.map(p => <tr key={p.payment_id} onClick={() => inspect(p)}><td><b>{p.payment_id}</b><small>{new Date(p.created_at).toLocaleString()}</small></td><td>{p.merchant_id}<small>{p.merchant_category}</small></td><td className="amount">${Number(p.amount).toFixed(2)} <small>{p.currency}</small></td><td><span className={`status ${p.status}`}>{p.status}</span></td><td className="arrow">→</td></tr>)}</tbody></table></div></div>
      <aside className="panel detail"><p className="eyebrow">Risk inspection</p>{selected ? <><h3>{selected.risk_band} risk</h3><div className="score">{selected.risk_score}<small>/ 100</small></div><p className="decision">Recommended: <b>{selected.decision}</b></p><ul>{selected.findings.map(f => <li key={f.rule_id}><b>{f.rule_id.replaceAll("_", " ")}</b><span>{f.message}</span></li>)}</ul></> : <div className="empty"><span>◎</span><p>Select a payment<br />to inspect its signals.</p></div>}</aside>
    </section>
    <footer><span>PayInsight v1.0</span><span>Built for confident payment decisions.</span></footer>
  </main>;
}
createRoot(document.getElementById("root")).render(<App />);
