import React, {useEffect, useState} from "react";
import {createRoot} from "react-dom/client";
import "./style.css";

function App() {
  const [metrics, setMetrics] = useState(null);
  const [risk, setRisk] = useState(null);
  useEffect(() => {
    fetch("/api/metrics").then(r => r.json()).then(setMetrics);
    fetch("/api/employees/E00001/risk").then(r => r.json()).then(setRisk);
  }, []);
  return <main className="container">
    <h1>PayInsight</h1><p className="muted">Payroll risk overview</p>
    <section className="cards">
      <article><span>Payroll events</span><strong>{metrics?.payroll_events ?? "—"}</strong></article>
      <article><span>Employees</span><strong>{metrics?.employees ?? "—"}</strong></article>
      <article><span>Sample risk</span><strong>{risk?.band ?? "—"}</strong></article>
    </section>
    {risk && <section className="panel"><h2>{risk.employee_id} risk score: {risk.score}</h2>
      <ul>{risk.findings.map(f => <li key={f.rule_id}><b>{f.rule_id}</b> — {f.message}</li>)}</ul>
    </section>}
  </main>
}
createRoot(document.getElementById("root")).render(<App/>);
