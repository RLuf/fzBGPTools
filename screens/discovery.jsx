// Discovery — Auto-detection of hosts/services + range groups + monitoring

const RANGE_GROUPS = [
  {
    id: "g1",
    name: "Backbone SP",
    ranges: ["10.0.0.0/24", "10.0.5.0/24"],
    color: "#3da9fc",
    hostsTotal: 38,
    hostsUp: 36,
    lastScan: "há 2 min",
    scanning: false,
    hosts: [
      { ip: "10.0.0.1",   hostname: "br-edge-01",        vendor: "MikroTik", os: "RouterOS 7.13.5", services: ["SSH:22","BGP:179","SNMP:161","NETCONF:830"],         routes: 964294, status: "online",   rtt: 0.4 },
      { ip: "10.0.0.2",   hostname: "br-edge-02",        vendor: "MikroTik", os: "RouterOS 7.13.5", services: ["SSH:22","BGP:179","SNMP:161","NETCONF:830"],         routes: 964291, status: "online",   rtt: 0.5 },
      { ip: "10.0.0.10",  hostname: "br-bgp-rs",         vendor: "Cisco",    os: "IOS-XR 7.10.1",   services: ["SSH:22","BGP:179","SNMP:161","gRPC:57400"],          routes: 712450, status: "online",   rtt: 0.6 },
      { ip: "10.0.0.250", hostname: "fw-perimeter-01",   vendor: "Cisco",    os: "FTD 7.4.1",       services: ["SSH:22","HTTPS:443","NETCONF:830"],                  routes: null,   status: "online",   rtt: 0.8 },
      { ip: "10.0.5.5",   hostname: "br-bgp-collector",  vendor: "Linux",    os: "Debian 12.5",     services: ["SSH:22","HTTP:8080","BMP:11019","Postgres:5432"],    routes: null,   status: "online",   rtt: 0.3 },
    ],
  },
  {
    id: "g2",
    name: "Datacenter DC1",
    ranges: ["10.0.1.0/24", "10.0.2.0/24"],
    color: "#a18cff",
    hostsTotal: 84,
    hostsUp: 82,
    lastScan: "há 5 min",
    scanning: false,
    hosts: [
      { ip: "10.0.1.5",  hostname: "sw-dc1-agg-01",  vendor: "Juniper", os: "Junos 22.4R3",   services: ["SSH:22","SNMP:161","NETCONF:830"],            routes: null,   status: "online",  rtt: 0.7 },
      { ip: "10.0.1.6",  hostname: "sw-dc1-agg-02",  vendor: "Juniper", os: "Junos 22.4R3",   services: ["SSH:22"],                                      routes: null,   status: "offline", rtt: null },
      { ip: "10.0.2.20", hostname: "mx-pe-01",        vendor: "Juniper", os: "Junos 22.4R3",   services: ["SSH:22","BGP:179","LDP:646","NETCONF:830"],   routes: 412000, status: "online",  rtt: 1.1 },
      { ip: "10.0.2.21", hostname: "mx-pe-02",        vendor: "Juniper", os: "Junos 22.4R3",   services: ["SSH:22","BGP:179","LDP:646","NETCONF:830"],   routes: 412000, status: "online",  rtt: 1.2 },
    ],
  },
  {
    id: "g3",
    name: "IX Public Peering",
    ranges: ["200.219.130.0/24", "2001:12f8:0:1::/64"],
    color: "#21d4fd",
    hostsTotal: 12,
    hostsUp: 12,
    lastScan: "há 1 min",
    scanning: true,
    hosts: [
      { ip: "200.219.130.1",  hostname: "rs1.sp.ptt.br",     vendor: "Cisco",  os: "IOS-XR 7.9",     services: ["BGP:179","SSH:22"], routes: 248123, status: "online", rtt: 2.4 },
      { ip: "200.219.130.2",  hostname: "rs2.sp.ptt.br",     vendor: "Cisco",  os: "IOS-XR 7.9",     services: ["BGP:179","SSH:22"], routes: 248114, status: "online", rtt: 2.6 },
      { ip: "200.219.130.45", hostname: "lg.sp.ptt.br",      vendor: "Linux",  os: "Ubuntu 22.04",   services: ["HTTPS:443","SSH:22","BMP:11019"], routes: null, status: "online", rtt: 2.5 },
    ],
  },
  {
    id: "g4",
    name: "OOB Management",
    ranges: ["172.16.0.0/24"],
    color: "#4ade80",
    hostsTotal: 22,
    hostsUp: 21,
    lastScan: "há 12 min",
    scanning: false,
    hosts: [],
  },
];

const SERVICE_BADGE = {
  "SSH:22":        "badge-blue",
  "BGP:179":       "badge-purple",
  "SNMP:161":      "badge-cyan",
  "NETCONF:830":   "badge-green",
  "HTTPS:443":     "badge-cyan",
  "HTTP:8080":     "badge-gray",
  "BMP:11019":     "badge-purple",
  "Postgres:5432": "badge-green",
  "gRPC:57400":    "badge-cyan",
  "LDP:646":       "badge-blue",
};

function Discovery() {
  const [groups, setGroups] = useState(RANGE_GROUPS);
  const [activeId, setActiveId] = useState(RANGE_GROUPS[0].id);
  const [monitorAll, setMonitorAll] = useState(true);
  const [autoScanInterval, setAutoScanInterval] = useState(15);
  const [newRange, setNewRange] = useState({ open: false, group: "g1", cidr: "" });

  const active = groups.find(g => g.id === activeId) || groups[0];

  const triggerScan = (gid) => {
    setGroups(prev => prev.map(g => g.id === gid ? { ...g, scanning: true } : g));
    setTimeout(() => {
      setGroups(prev => prev.map(g => g.id === gid ? { ...g, scanning: false, lastScan: "agora" } : g));
    }, 2800);
  };

  const totalHosts = groups.reduce((a, g) => a + g.hostsTotal, 0);
  const totalUp = groups.reduce((a, g) => a + g.hostsUp, 0);

  return (
    <div data-screen-label="04 Discovery">
      <PageHead
        title="Auto"
        accent="descoberta"
        sub="Varredura ativa de ranges, fingerprinting de serviços e monitoramento contínuo de rotas BGP por host."
        actions={<>
          <button className="btn"><Icon name="settings" size={14}/>Política de scan</button>
          <button className="btn btn-primary" onClick={() => setNewRange({ open: true, group: active.id, cidr: "" })}>
            <Icon name="plus" size={14}/>Adicionar Range
          </button>
        </>}
      />

      <div className="stats">
        <div className="stat">
          <div className="lbl">Hosts descobertos</div>
          <div className="val">{totalHosts}</div>
          <div className="delta up">{totalUp} online · {totalHosts - totalUp} offline</div>
        </div>
        <div className="stat">
          <div className="lbl">Grupos de range</div>
          <div className="val">{groups.length}</div>
          <div className="delta">{groups.reduce((a, g) => a + g.ranges.length, 0)} CIDRs monitorados</div>
        </div>
        <div className="stat">
          <div className="lbl">Serviços ativos</div>
          <div className="val">438</div>
          <div className="delta up">SSH · BGP · SNMP · NETCONF</div>
        </div>
        <div className="stat">
          <div className="lbl">Intervalo de varredura</div>
          <div className="val">{autoScanInterval} <span style={{ fontSize: 14, color: "var(--text-mute)" }}>min</span></div>
          <div className="delta">próxima em 4 min</div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: 18 }}>
        {/* Range Groups List */}
        <div className="card">
          <div className="card-header">
            <Icon name="scan" size={15}/>
            <h3>Grupos de <span className="accent">Range</span></h3>
            <div className="spacer"></div>
            <button className="btn btn-sm btn-icon" title="Adicionar grupo"><Icon name="plus" size={13}/></button>
          </div>
          <div className="card-body" style={{ padding: 8, display: "grid", gap: 6 }}>
            {groups.map(g => (
              <div key={g.id}
                   onClick={() => setActiveId(g.id)}
                   style={{
                     padding: "12px 14px",
                     borderRadius: 10,
                     border: "1px solid " + (g.id === activeId ? "var(--border-strong)" : "var(--border)"),
                     background: g.id === activeId ? "rgba(61,169,252,0.08)" : "rgba(255,255,255,0.015)",
                     cursor: "pointer",
                     position: "relative",
                     transition: "all .15s",
                   }}>
                <div style={{ position: "absolute", left: 0, top: 8, bottom: 8, width: 3, borderRadius: 2, background: g.color, opacity: g.id === activeId ? 1 : 0.55 }}></div>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                  <div style={{ fontWeight: 600, fontSize: 13 }}>{g.name}</div>
                  <div style={{ flex: 1 }}></div>
                  {g.scanning ? (
                    <span className="badge badge-cyan"><span className="ix-dot"></span>scan</span>
                  ) : (
                    <span style={{ fontSize: 10, color: "var(--text-mute)" }}>{g.lastScan}</span>
                  )}
                </div>
                <div style={{ fontSize: 11, color: "var(--text-mute)", fontFamily: "JetBrains Mono, monospace", marginBottom: 8 }}>
                  {g.ranges.join("  ·  ")}
                </div>
                <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                  <div style={{ flex: 1, height: 4, borderRadius: 2, background: "rgba(255,255,255,0.05)", overflow: "hidden" }}>
                    <div style={{ height: "100%", width: ((g.hostsUp / g.hostsTotal) * 100) + "%", background: g.color, borderRadius: 2 }}></div>
                  </div>
                  <span className="mono" style={{ fontSize: 10.5, color: "var(--text-dim)" }}>{g.hostsUp}/{g.hostsTotal}</span>
                </div>
              </div>
            ))}
          </div>

          <div style={{ padding: "12px 16px 16px", borderTop: "1px solid var(--border)" }}>
            <div style={{ fontSize: 10.5, color: "var(--text-mute)", textTransform: "uppercase", letterSpacing: "0.12em", fontWeight: 600, marginBottom: 10 }}>
              Configurações globais
            </div>
            <label style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer", marginBottom: 10 }}>
              <input type="checkbox" checked={monitorAll} onChange={(e) => setMonitorAll(e.target.checked)}/>
              <span style={{ fontSize: 12.5 }}>Monitorar serviços continuamente</span>
            </label>
            <div className="field">
              <label>Intervalo de scan (min)</label>
              <select className="select" value={autoScanInterval} onChange={(e) => setAutoScanInterval(+e.target.value)}>
                <option value={5}>5 minutos</option>
                <option value={15}>15 minutos</option>
                <option value={30}>30 minutos</option>
                <option value={60}>1 hora</option>
              </select>
            </div>
          </div>
        </div>

        {/* Active group detail */}
        <div className="card">
          <div className="card-header">
            <div style={{ width: 6, height: 22, borderRadius: 3, background: active.color, marginRight: 4 }}></div>
            <h3>{active.name}</h3>
            <span className="mono" style={{ fontSize: 11.5, color: "var(--text-mute)", marginLeft: 10 }}>
              {active.ranges.join("  ·  ")}
            </span>
            <div className="spacer"></div>
            <button className="btn btn-sm" onClick={() => triggerScan(active.id)} disabled={active.scanning}>
              <Icon name="radar" size={13}/>{active.scanning ? "Varrendo..." : "Scan agora"}
            </button>
            <button className="btn btn-sm"><Icon name="eye" size={13}/>Monitor</button>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            {active.scanning && (
              <div style={{
                padding: "12px 18px",
                background: "rgba(33,212,253,0.06)",
                borderBottom: "1px solid rgba(33,212,253,0.18)",
                display: "flex", alignItems: "center", gap: 12,
                fontSize: 12.5
              }}>
                <Icon name="radar" size={16}/>
                <span>Varrendo {active.ranges.join(", ")} — TCP SYN scan + service fingerprint...</span>
                <div style={{ flex: 1 }}></div>
                <div style={{ width: 200, height: 4, borderRadius: 2, background: "rgba(255,255,255,0.05)", overflow: "hidden" }}>
                  <div style={{ height: "100%", background: active.color, borderRadius: 2, width: "60%", animation: "scanbar 2.8s ease-out forwards" }}></div>
                </div>
              </div>
            )}
            <style>{`@keyframes scanbar { from { width: 5%; } to { width: 100%; } }`}</style>
            <table className="t">
              <thead>
                <tr>
                  <th style={{ width: 150 }}>IP</th>
                  <th>Hostname</th>
                  <th style={{ width: 110 }}>Vendor / OS</th>
                  <th>Serviços detectados</th>
                  <th style={{ width: 110, textAlign: "right" }}>Rotas BGP</th>
                  <th style={{ width: 80, textAlign: "right" }}>RTT</th>
                  <th style={{ width: 100 }}>Status</th>
                  <th style={{ width: 110, textAlign: "right" }}>Monitor</th>
                </tr>
              </thead>
              <tbody>
                {active.hosts.length === 0 ? (
                  <tr><td colSpan="8" style={{ textAlign: "center", padding: 40, color: "var(--text-mute)" }}>
                    Nenhuma varredura ainda neste range. Clique em "Scan agora".
                  </td></tr>
                ) : active.hosts.map(h => (
                  <tr key={h.ip}>
                    <td className="mono" style={{ fontSize: 11.5 }}>{h.ip}</td>
                    <td>
                      <div style={{ fontWeight: 600 }}>{h.hostname}</div>
                    </td>
                    <td>
                      <div style={{ fontSize: 12 }}>{h.vendor}</div>
                      <div style={{ fontSize: 10.5, color: "var(--text-mute)", fontFamily: "JetBrains Mono, monospace" }}>{h.os}</div>
                    </td>
                    <td>
                      <div style={{ display: "flex", gap: 4, flexWrap: "wrap", maxWidth: 320 }}>
                        {h.services.map(s => (
                          <span key={s} className={"badge " + (SERVICE_BADGE[s] || "badge-gray")} style={{ fontSize: 9.5 }}>{s}</span>
                        ))}
                      </div>
                    </td>
                    <td className="mono" style={{ textAlign: "right", color: h.routes ? "var(--accent-2)" : "var(--text-mute)" }}>
                      {h.routes ? h.routes.toLocaleString() : "—"}
                    </td>
                    <td className="mono" style={{ textAlign: "right", color: h.rtt ? (h.rtt < 1 ? "var(--green)" : "var(--yellow)") : "var(--text-mute)" }}>
                      {h.rtt ? h.rtt.toFixed(1) + "ms" : "—"}
                    </td>
                    <td>
                      {h.status === "online"
                        ? <span className="badge badge-green"><span className="ix-dot"></span>online</span>
                        : <span className="badge badge-red"><span className="ix-dot"></span>offline</span>}
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <MonitorToggle initial={h.status === "online"}/>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {newRange.open && <AddRangeModal
        onClose={() => setNewRange({ ...newRange, open: false })}
        groups={groups}
        value={newRange}
        onChange={setNewRange}
        onSave={(payload) => {
          setGroups(prev => prev.map(g => g.id === payload.group ? { ...g, ranges: [...g.ranges, payload.cidr] } : g));
          setNewRange({ ...newRange, open: false });
        }}
      />}
    </div>
  );
}

function MonitorToggle({ initial }) {
  const [on, setOn] = useState(initial);
  return (
    <label style={{
      display: "inline-flex", alignItems: "center", cursor: "pointer", gap: 6, userSelect: "none",
    }}>
      <input type="checkbox" checked={on} onChange={(e) => setOn(e.target.checked)} style={{ display: "none" }}/>
      <div style={{
        width: 32, height: 18, borderRadius: 10,
        background: on ? "var(--neon)" : "rgba(255,255,255,0.06)",
        border: "1px solid " + (on ? "transparent" : "var(--border)"),
        position: "relative", transition: "all .2s",
        boxShadow: on ? "0 0 12px rgba(61,169,252,0.5)" : "none",
      }}>
        <div style={{
          position: "absolute", top: 1, left: on ? 14 : 1,
          width: 14, height: 14, borderRadius: "50%",
          background: on ? "#061122" : "var(--text-dim)",
          transition: "left .2s",
        }}></div>
      </div>
      <span style={{ fontSize: 11, color: on ? "var(--text)" : "var(--text-mute)" }}>{on ? "ON" : "OFF"}</span>
    </label>
  );
}

function AddRangeModal({ onClose, groups, value, onChange, onSave }) {
  return (
    <Modal
      title="Adicionar range CIDR"
      onClose={onClose}
      footer={<>
        <button className="btn" onClick={onClose}>Cancelar</button>
        <button className="btn btn-primary" onClick={() => onSave(value)}>Adicionar e varrer</button>
      </>}
    >
      <Field label="Grupo de range">
        <select className="select" value={value.group} onChange={(e) => onChange({ ...value, group: e.target.value })}>
          {groups.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
        </select>
      </Field>
      <Field label="CIDR (IPv4 ou IPv6)">
        <input className="input" placeholder="10.0.4.0/24" value={value.cidr} onChange={(e) => onChange({ ...value, cidr: e.target.value })}/>
      </Field>
      <div style={{ fontSize: 11.5, color: "var(--text-mute)", lineHeight: 1.5 }}>
        O range será varrido imediatamente após adicionado. Serviços detectados (SSH, BGP, SNMP, NETCONF, etc) serão cadastrados automaticamente e poderão ser monitorados individualmente.
      </div>
    </Modal>
  );
}

window.Discovery = Discovery;
