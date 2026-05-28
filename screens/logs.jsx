// Logs Console — full terminal w/ filters + auto-scroll

const LOG_MODULES = ["bgpd", "session", "monitor", "ssh-client", "snmp-poller", "ix-feeder", "core"];
const LOG_SEVS = ["INFO", "WARN", "ERROR", "CRITICAL", "DEBUG"];

const SEED_LOGS = [
  { ts: "2026-05-26T14:08:11.421Z", sev: "INFO",     mod: "bgpd",        msg: "BGP session 200.219.130.1 (AS262332) Established — 124.3k prefixes received" },
  { ts: "2026-05-26T14:08:14.012Z", sev: "INFO",     mod: "session",     msg: "Peer 187.16.220.1 (AS12956) MED updated 100 -> 250 for 17 prefixes" },
  { ts: "2026-05-26T14:08:17.834Z", sev: "DEBUG",    mod: "snmp-poller", msg: "Polled ifHCInOctets on br-edge-01 — delta 412.3 MB" },
  { ts: "2026-05-26T14:08:22.118Z", sev: "INFO",     mod: "monitor",     msg: "Aggregate traffic 3.81 Gbps (in) / 1.92 Gbps (out)" },
  { ts: "2026-05-26T14:08:29.501Z", sev: "WARN",     mod: "bgpd",        msg: "Prefix 200.149.0.0/16 prepend detected via AS174 (length=3)" },
  { ts: "2026-05-26T14:08:33.219Z", sev: "INFO",     mod: "ssh-client",  msg: "SSH session opened to br-edge-02 by netadmin@10.0.5.5" },
  { ts: "2026-05-26T14:08:41.704Z", sev: "ERROR",    mod: "session",     msg: "Hold timer expired with peer 10.0.0.2 (AS263870)" },
  { ts: "2026-05-26T14:08:43.910Z", sev: "INFO",     mod: "session",     msg: "Peer 10.0.0.2 (AS263870) restored — Established" },
  { ts: "2026-05-26T14:08:47.330Z", sev: "WARN",     mod: "bgpd",        msg: "Route flap detected: 187.45.128.0/19 via AS12956 (8 flaps / 15 min)" },
  { ts: "2026-05-26T14:08:51.802Z", sev: "INFO",     mod: "ix-feeder",   msg: "IX.br SP — 248 peers visible on route-server rs1" },
  { ts: "2026-05-26T14:08:55.227Z", sev: "DEBUG",    mod: "snmp-poller", msg: "CPU load br-bgp-rs: 14% / mem 38%" },
  { ts: "2026-05-26T14:09:02.119Z", sev: "CRITICAL", mod: "bgpd",        msg: "Route 187.45.128.0/19 SUPPRESSED — RFD threshold 2000 reached" },
  { ts: "2026-05-26T14:09:07.553Z", sev: "INFO",     mod: "core",        msg: "Configuration snapshot saved — /var/lib/fzbgp/snapshots/2026-05-26_140907.db" },
  { ts: "2026-05-26T14:09:13.821Z", sev: "WARN",     mod: "monitor",     msg: "Latency to AS15169 via IX.br = 4.2ms (avg) — within SLO" },
  { ts: "2026-05-26T14:09:19.408Z", sev: "INFO",     mod: "bgpd",        msg: "Received UPDATE: 1842 NLRI from 200.219.130.1 (AS262332)" },
  { ts: "2026-05-26T14:09:22.610Z", sev: "ERROR",    mod: "ssh-client",  msg: "Authentication failed: user 'admin' on sw-dc1-agg-02 — connection refused" },
  { ts: "2026-05-26T14:09:25.918Z", sev: "INFO",     mod: "monitor",     msg: "Looking-glass query: BGP show route 142.250.0.0/15" },
  { ts: "2026-05-26T14:09:30.044Z", sev: "DEBUG",    mod: "bgpd",        msg: "Trie compaction: 964294 prefixes / 312 MB" },
  { ts: "2026-05-26T14:09:34.711Z", sev: "INFO",     mod: "ix-feeder",   msg: "AS15169 (Google) — new prefix 142.251.46.0/24 announced via IX.br" },
];

function LogsConsole() {
  const [logs, setLogs] = useState(SEED_LOGS);
  const [paused, setPaused] = useState(false);
  const [sev, setSev] = useState(new Set(LOG_SEVS));
  const [mod, setMod] = useState("Todos");
  const [q, setQ] = useState("");
  const termRef = useRef(null);

  useEffect(() => {
    if (paused) return;
    const id = setInterval(() => {
      setLogs(prev => {
        const mods = LOG_MODULES;
        const sevs = ["INFO","INFO","INFO","DEBUG","WARN","INFO","ERROR"];
        const m = mods[Math.floor(Math.random()*mods.length)];
        const s = sevs[Math.floor(Math.random()*sevs.length)];
        const msgs = [
          "Heartbeat received from peer route-server",
          "Polled SNMP counters on edge fleet",
          "Looking-glass query executed by 10.0.5.5",
          "MD5 password rotated on session 187.16.220.1",
          "Prefix-list ipv4-out applied to AS12956 — 3 changes",
          "Route reflection cluster sync OK (3/3 RRs)",
          "Healthcheck SSH br-edge-02 — 22/tcp open",
          "BFD neighbor 10.0.0.10 (AS263870) UP",
        ];
        const msg = msgs[Math.floor(Math.random()*msgs.length)];
        return [...prev, { ts: new Date().toISOString(), sev: s, mod: m, msg }].slice(-300);
      });
    }, 1300);
    return () => clearInterval(id);
  }, [paused]);

  useEffect(() => {
    if (!paused && termRef.current) termRef.current.scrollTop = termRef.current.scrollHeight;
  }, [logs, paused]);

  const toggleSev = (s) => {
    const next = new Set(sev);
    if (next.has(s)) next.delete(s); else next.add(s);
    setSev(next);
  };

  const filtered = logs.filter(l => {
    if (!sev.has(l.sev)) return false;
    if (mod !== "Todos" && l.mod !== mod) return false;
    if (q && !l.msg.toLowerCase().includes(q.toLowerCase())) return false;
    return true;
  });

  return (
    <div data-screen-label="05 Logs">
      <PageHead
        title="Console de"
        accent="Logs"
        sub="Stream em tempo real de todos os módulos. Filtre por severidade, módulo e palavra-chave."
        actions={<>
          <button className="btn"><Icon name="download" size={14}/>Exportar TXT</button>
          <button className="btn"><Icon name="download" size={14}/>Exportar CSV</button>
        </>}
      />

      <div className="filters">
        {LOG_SEVS.map(s => (
          <span key={s} className={"sev sev-" + s} style={{ cursor: "pointer", opacity: sev.has(s) ? 1 : 0.35, padding: "4px 10px", fontSize: 11.5 }} onClick={() => toggleSev(s)}>
            {s}
          </span>
        ))}
        <div style={{ width: 12 }}></div>
        <select className="select" value={mod} onChange={(e) => setMod(e.target.value)}>
          <option>Todos</option>
          {LOG_MODULES.map(m => <option key={m}>{m}</option>)}
        </select>
        <Search value={q} onChange={setQ} placeholder="Buscar mensagem..." width={260}/>
        <div style={{ flex: 1 }}></div>
        <span className="badge badge-blue"><span className="hl-ip" style={{ background: "transparent", border: "none", padding: 0 }}>10.0.0.1</span> IP</span>
        <span className="badge badge-purple"><span className="hl-asn" style={{ background: "transparent", border: "none", padding: 0 }}>AS263870</span> ASN</span>
        <button className="btn btn-sm" onClick={() => setPaused(!paused)}>
          <Icon name={paused ? "play" : "pause"} size={12}/>{paused ? "Retomar" : "Pausar"} auto-scroll
        </button>
        <span className="badge badge-gray">{filtered.length} / {logs.length}</span>
      </div>

      <div className="card card-tight">
        <div className="term-bar">
          <div className="dot-r"></div><div className="dot-y"></div><div className="dot-g"></div>
          <div className="term-title">/var/log/fzbgptools/stream.log</div>
          <div style={{ flex: 1 }}></div>
          {paused
            ? <span className="badge badge-yellow"><span className="ix-dot"></span>pausado</span>
            : <span className="badge badge-green"><span className="ix-dot"></span>tail -f</span>}
        </div>
        <div ref={termRef} className="term" style={{ height: "calc(100vh - 360px)", minHeight: 400, borderRadius: 0, border: "none" }}>
          {filtered.map((l, i) => (
            <span key={i} className="ln">
              <span className="dim">{l.ts.slice(11, 23)}</span>{"  "}
              <span className={"sev sev-" + l.sev}>{l.sev}</span>{" "}
              <span className="info">[{l.mod}]</span>{" "}
              <span className={l.sev === "ERROR" || l.sev === "CRITICAL" ? "err" : l.sev === "WARN" ? "warn" : "ok"}>
                {highlightLog(l.msg)}
              </span>
            </span>
          ))}
          {!paused && <span className="cursor"></span>}
        </div>
      </div>
    </div>
  );
}

window.LogsConsole = LogsConsole;

// ─── Syntax highlighting for IPs, ASNs, CIDRs, prefixes ─────────────────
// Token order: AS-PATH numbers, CIDR ranges, IPv4, IPv6, prefix-words.
const HL_RE = /(AS\d{1,7}|(?:\d{1,3}\.){3}\d{1,3}\/\d{1,2}|(?:\d{1,3}\.){3}\d{1,3}|(?:[0-9a-f]+:){2,7}[0-9a-f]+(?:\/\d{1,3})?|\b(?:Established|UP|DOWN|SUPPRESSED|OK|FAIL)\b)/gi;

function highlightLog(text) {
  if (!text) return text;
  const out = [];
  let last = 0;
  let m;
  const re = new RegExp(HL_RE);
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(text.slice(last, m.index));
    const tok = m[0];
    let cls = "";
    if (/^AS\d/.test(tok)) cls = "hl-asn";
    else if (/\//.test(tok) && /\./.test(tok)) cls = "hl-cidr";
    else if (/^(?:\d{1,3}\.){3}\d{1,3}$/.test(tok)) cls = "hl-ip";
    else if (/:/.test(tok)) cls = "hl-ipv6";
    else if (/^(Established|UP|OK)$/i.test(tok)) cls = "hl-ok";
    else if (/^(DOWN|FAIL|SUPPRESSED)$/i.test(tok)) cls = "hl-bad";
    out.push(<span key={out.length} className={cls}>{tok}</span>);
    last = m.index + tok.length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

window.highlightLog = highlightLog;
