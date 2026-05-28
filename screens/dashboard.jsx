// Dashboard - Peering Graph + Alerts + Last Traceroute

const NODES = [
  { id: "AS263870", org: "Webstorage", type: "self",    x: 50, y: 50, asn: "263870", sub: "OWN" },
  { id: "AS262332", org: "IX.br SP",   type: "ix",      x: 25, y: 18, asn: "262332", sub: "PTT" },
  { id: "AS12956",  org: "Telefônica", type: "transit", x: 78, y: 24, asn: "12956",  sub: "TRA" },
  { id: "AS174",    org: "Cogent",     type: "transit", x: 82, y: 70, asn: "174",    sub: "TRA" },
  { id: "AS15169",  org: "Google",     type: "dest",    x: 22, y: 78, asn: "15169",  sub: "DST" },
  { id: "AS16509",  org: "AWS",        type: "dest",    x: 55, y: 90, asn: "16509",  sub: "DST" },
];

const EDGES = [
  { from: "AS263870", to: "AS262332", label: "Public Peering", kind: "public", bps: "1.2 Gbps" },
  { from: "AS263870", to: "AS12956",  label: "Trânsito IP",    kind: "transit", bps: "850 Mbps" },
  { from: "AS263870", to: "AS174",    label: "Trânsito IP",    kind: "transit", bps: "620 Mbps" },
  { from: "AS262332", to: "AS15169",  label: "BGP Peering",    kind: "peering", bps: "340 Mbps" },
  { from: "AS262332", to: "AS16509",  label: "BGP Peering",    kind: "peering", bps: "510 Mbps" },
  { from: "AS12956",  to: "AS15169",  label: "Trânsito",       kind: "transit", bps: "210 Mbps" },
  { from: "AS174",    to: "AS16509",  label: "Trânsito",       kind: "transit", bps: "280 Mbps" },
];

const ALERTS = [
  { sev: "critical", title: "Prepend detection", desc: "AS174 está fazendo AS-Path prepend (3x) no prefixo 200.149.0.0/16. Possível shift de tráfego.", meta: "AS_PATH 174 174 174 263870 · há 3 min", icon: "alert" },
  { sev: "critical", title: "Route flapping", desc: "Prefixo 187.45.128.0/19 oscilou 8 vezes nos últimos 15 min via AS12956.", meta: "RFD threshold 2000 · suprimido por 30 min", icon: "alert" },
  { sev: "warn",     title: "MED change",     desc: "Telefônica alterou MED de 100 → 250 em 17 prefixos do upstream.", meta: "Sessão eBGP 187.16.220.1 · há 12 min", icon: "bell" },
];

const TRACE = [
  { hop: 1,  ip: "10.0.0.1",        host: "br-edge-01.webstorage.net",  asn: "AS263870", as: "Webstorage",      ms: 0.4,   ix: false },
  { hop: 2,  ip: "187.16.220.1",    host: "border1.sp.telefonica.com",  asn: "AS12956",  as: "Telefônica",      ms: 1.8,   ix: false },
  { hop: 3,  ip: "200.219.130.45",  host: "sp.ptt.br",                  asn: "AS262332", as: "IX.br SP",        ms: 2.6,   ix: true  },
  { hop: 4,  ip: "200.219.130.118", host: "google-pe.sp.ptt.br",        asn: "AS262332", as: "IX.br SP",        ms: 2.9,   ix: true  },
  { hop: 5,  ip: "108.170.243.1",   host: "tata.bba.google.com",        asn: "AS15169",  as: "Google",          ms: 3.4,   ix: false },
  { hop: 6,  ip: "142.250.227.142", host: "iad23s90.gmail.com",         asn: "AS15169",  as: "Google",          ms: 4.1,   ix: false },
  { hop: 7,  ip: "8.8.8.8",         host: "dns.google",                 asn: "AS15169",  as: "Google",          ms: 4.0,   ix: false },
];

function PeeringGraph() {
  const wrapRef = useRef(null);
  const [size, setSize] = useState({ w: 800, h: 500 });
  const [hovered, setHovered] = useState(null);

  useEffect(() => {
    const update = () => {
      if (!wrapRef.current) return;
      const r = wrapRef.current.getBoundingClientRect();
      setSize({ w: r.width, h: r.height });
    };
    update();
    const ro = new ResizeObserver(update);
    if (wrapRef.current) ro.observe(wrapRef.current);
    return () => ro.disconnect();
  }, []);

  const pos = (n) => ({ x: (n.x / 100) * size.w, y: (n.y / 100) * size.h });
  const byId = (id) => NODES.find(n => n.id === id);

  return (
    <div className="graph-wrap" ref={wrapRef}>
      <svg className="graph-svg" viewBox={`0 0 ${size.w} ${size.h}`} preserveAspectRatio="none">
        <defs>
          {/* Animated dash for active connections */}
          <linearGradient id="edge-peering" x1="0" x2="1">
            <stop offset="0" stopColor="#3da9fc" stopOpacity="0.1"/>
            <stop offset="0.5" stopColor="#21d4fd" stopOpacity="0.85"/>
            <stop offset="1" stopColor="#a18cff" stopOpacity="0.1"/>
          </linearGradient>
          <linearGradient id="edge-transit" x1="0" x2="1">
            <stop offset="0" stopColor="#94a3b8" stopOpacity="0.1"/>
            <stop offset="0.5" stopColor="#cbd5e1" stopOpacity="0.6"/>
            <stop offset="1" stopColor="#94a3b8" stopOpacity="0.1"/>
          </linearGradient>
          <linearGradient id="edge-public" x1="0" x2="1">
            <stop offset="0" stopColor="#a18cff" stopOpacity="0.1"/>
            <stop offset="0.5" stopColor="#c4b5ff" stopOpacity="0.85"/>
            <stop offset="1" stopColor="#a18cff" stopOpacity="0.1"/>
          </linearGradient>
          <marker id="arrow-peering" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill="#21d4fd"/>
          </marker>
          <marker id="arrow-transit" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill="#cbd5e1"/>
          </marker>
          <marker id="arrow-public" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill="#c4b5ff"/>
          </marker>
          <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>

        {EDGES.map((e, i) => {
          const a = pos(byId(e.from));
          const b = pos(byId(e.to));
          // Offset endpoints to outside node radius
          const dx = b.x - a.x, dy = b.y - a.y;
          const d = Math.hypot(dx, dy);
          const r = 48;
          const sx = a.x + (dx / d) * r;
          const sy = a.y + (dy / d) * r;
          const ex = b.x - (dx / d) * r;
          const ey = b.y - (dy / d) * r;
          const stroke = `url(#edge-${e.kind})`;
          const marker = `url(#arrow-${e.kind})`;
          const isHover = hovered && (hovered === e.from || hovered === e.to);
          return (
            <g key={i} style={{ opacity: hovered && !isHover ? 0.25 : 1, transition: "opacity .2s" }}>
              <line x1={sx} y1={sy} x2={ex} y2={ey}
                    stroke={stroke} strokeWidth={isHover ? 2.4 : 1.6}
                    markerEnd={marker}
                    filter={isHover ? "url(#glow)" : undefined}
                    strokeDasharray="6 4"
                    style={{ animation: `flow 1.5s linear infinite` }}/>
            </g>
          );
        })}
      </svg>

      <style>{`
        @keyframes flow { to { stroke-dashoffset: -20; } }
      `}</style>

      {/* Edge labels */}
      {EDGES.map((e, i) => {
        const a = pos(byId(e.from));
        const b = pos(byId(e.to));
        const mx = (a.x + b.x) / 2;
        const my = (a.y + b.y) / 2;
        return (
          <div key={i} className={"edge-label " + e.kind} style={{ left: mx, top: my }}>
            {e.label}
          </div>
        );
      })}

      {/* Nodes */}
      {NODES.map(n => {
        const p = pos(n);
        return (
          <div key={n.id}
               className={"graph-node-card node-" + n.type}
               style={{ left: p.x, top: p.y }}
               onMouseEnter={() => setHovered(n.id)}
               onMouseLeave={() => setHovered(null)}>
            <div className="ring">
              <div style={{ textAlign: "center" }}>
                <div className="asn-num">AS{n.asn}</div>
                <div className="asn-sub">{n.sub}</div>
              </div>
            </div>
            <div className="label">{n.id}</div>
            <div className="org">{n.org}</div>
          </div>
        );
      })}

      <div className="graph-legend">
        <div className="it"><span className="sw" style={{ background: "linear-gradient(135deg,#1e40af,#3da9fc)" }}></span>Próprio</div>
        <div className="it"><span className="sw" style={{ background: "linear-gradient(135deg,#6d28d9,#a18cff)" }}></span>IX/PTT</div>
        <div className="it"><span className="sw" style={{ background: "linear-gradient(135deg,#475569,#94a3b8)" }}></span>Trânsito</div>
        <div className="it"><span className="sw" style={{ background: "linear-gradient(135deg,#15803d,#4ade80)" }}></span>Destino</div>
      </div>

      <div className="graph-controls">
        <button className="icon-btn"><Icon name="zoom-in" size={15}/></button>
        <button className="icon-btn"><Icon name="zoom-out" size={15}/></button>
        <button className="icon-btn"><Icon name="fit" size={15}/></button>
        <button className="icon-btn"><Icon name="refresh" size={15}/></button>
      </div>
    </div>
  );
}

function Dashboard() {
  return (
    <div data-screen-label="01 Dashboard">
      <PageHead
        title="Mapa de"
        accent="Peering BGP"
        sub="Visualização ao vivo das sessões eBGP de AS263870 — sessões públicas, trânsitos e destinos prioritários."
        actions={<>
          <button className="btn"><Icon name="refresh" size={14}/>Atualizar</button>
          <button className="btn btn-primary"><Icon name="plus" size={14}/>Nova sessão BGP</button>
        </>}
      />

      <div className="stats" style={{ gridTemplateColumns: "repeat(5, 1fr)" }}>
        <div className="stat">
          <div className="lbl">Sessões eBGP</div>
          <div className="val">7 / 7</div>
          <div className="delta up">↑ 100% Established</div>
        </div>
        <div className="stat">
          <div className="lbl">Prefixos recebidos</div>
          <div className="val">964.3 K</div>
          <div className="delta up">+1.2K nas últimas 24h</div>
        </div>
        <div className="stat hosts-stat">
          <div className="lbl">Hosts monitorados</div>
          <div className="val">
            <span style={{ color: "var(--green)" }}>152</span>
            <span style={{ color: "var(--text-mute)", fontSize: 18, fontWeight: 500 }}> / 156</span>
          </div>
          <div className="delta" style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 4 }}>
            <span style={{ color: "var(--green)", display: "inline-flex", alignItems: "center", gap: 4 }}>
              <span className="s-dot s-on" style={{ margin: 0 }}></span>152 online
            </span>
            <span style={{ color: "var(--red)", display: "inline-flex", alignItems: "center", gap: 4 }}>
              <span className="s-dot" style={{ background: "var(--red)", boxShadow: "0 0 8px var(--red)", margin: 0 }}></span>4 offline
            </span>
          </div>
          <div className="bar" style={{ marginTop: 8 }}>
            <span style={{ width: ((152/156)*100) + "%", background: "linear-gradient(90deg, #4ade80, #22d3a8)" }}></span>
          </div>
        </div>
        <div className="stat">
          <div className="lbl">Tráfego agregado</div>
          <div className="val">3.81 Gbps</div>
          <div className="delta up">↑ 8.4% vs ontem</div>
        </div>
        <div className="stat">
          <div className="lbl">Alertas ativos</div>
          <div className="val" style={{ color: "var(--red)" }}>3</div>
          <div className="delta dn">2 críticos · 1 warn</div>
        </div>
      </div>

      <div className="dash-grid">
        <div className="card">
          <div className="card-header">
            <h3>Topologia <span className="accent">/ Peering BGP</span></h3>
            <div className="spacer"></div>
            <span className="badge badge-green"><span className="ix-dot"></span>Live · 1s</span>
            <button className="btn btn-sm btn-ghost" style={{ marginLeft: 10 }}><Icon name="filter" size={13}/>Filtros</button>
          </div>
          <div className="card-body dash-card-body">
            <PeeringGraph/>
          </div>
        </div>

        <div className="dash-right">
          <div className="card" style={{ display: "flex", flexDirection: "column", minHeight: 0 }}>
            <div className="card-header">
              <h3>Alertas <span className="accent">BGP</span></h3>
              <div className="spacer"></div>
              <span className="badge badge-red">3 ativos</span>
            </div>
            <div className="card-body" style={{ display: "grid", gap: 10, overflow: "auto", flex: 1, minHeight: 0 }}>
              {ALERTS.map((a, i) => (
                <div key={i} className={"alert" + (a.sev === "warn" ? " warn" : "")}>
                  <div className="ico"><Icon name={a.icon} size={14}/></div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div className="ttl">{a.title}</div>
                    <div className="desc">{a.desc}</div>
                    <div className="meta">{a.meta}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card" style={{ display: "flex", flexDirection: "column", minHeight: 0 }}>
            <div className="card-header">
              <h3>Último <span className="accent">Traceroute</span></h3>
              <div className="spacer"></div>
              <span className="mono" style={{ color: "var(--text-mute)", fontSize: 11 }}>→ 8.8.8.8</span>
            </div>
            <div style={{ overflow: "auto", flex: 1, minHeight: 0 }}>
              <table className="t" style={{ fontSize: 11.5 }}>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>IP</th>
                    <th>ASN</th>
                    <th>AS Name</th>
                    <th style={{ textAlign: "right" }}>ms</th>
                  </tr>
                </thead>
                <tbody>
                  {TRACE.map(h => (
                    <tr key={h.hop}>
                      <td className="mono" style={{ color: "var(--text-mute)" }}>{h.hop}</td>
                      <td className="mono">{h.ip}</td>
                      <td>
                        <span className={"badge " + (h.ix ? "badge-purple" : "badge-blue")} style={{ fontSize: 9.5 }}>
                          {h.asn}
                        </span>
                      </td>
                      <td style={{ fontSize: 11.5 }}>
                        {h.as}
                        {h.ix && <span className="badge badge-purple" style={{ marginLeft: 6, fontSize: 9 }}>IX</span>}
                      </td>
                      <td className="mono" style={{ textAlign: "right", color: h.ms > 3 ? "var(--yellow)" : "var(--green)" }}>
                        {h.ms.toFixed(1)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

window.Dashboard = Dashboard;
