// Network Tools — Ping / Traceroute / SSH / Telnet

const NT_HOSTS = [
  { hostname: "br-edge-01", ip: "10.0.0.1", port: 22, user: "netadmin" },
  { hostname: "br-edge-02", ip: "10.0.0.2", port: 22, user: "netadmin" },
  { hostname: "br-bgp-rs",  ip: "10.0.0.10", port: 22, user: "ops" },
  { hostname: "rs-ix-sp",   ip: "200.219.130.1", port: 22, user: "peering" },
];

const PING_OUTPUT = (target) => [
  { cls: "info",   text: `PING ${target} (${target}) 56(84) bytes of data.` },
  { cls: "ok",     text: `64 bytes from ${target}: icmp_seq=1 ttl=58 time=4.12 ms` },
  { cls: "ok",     text: `64 bytes from ${target}: icmp_seq=2 ttl=58 time=3.98 ms` },
  { cls: "ok",     text: `64 bytes from ${target}: icmp_seq=3 ttl=58 time=4.05 ms` },
  { cls: "ok",     text: `64 bytes from ${target}: icmp_seq=4 ttl=58 time=4.21 ms` },
  { cls: "ok",     text: `64 bytes from ${target}: icmp_seq=5 ttl=58 time=4.09 ms` },
  { cls: "ok",     text: `64 bytes from ${target}: icmp_seq=6 ttl=58 time=3.92 ms` },
  { cls: "ok",     text: `64 bytes from ${target}: icmp_seq=7 ttl=58 time=4.14 ms` },
  { cls: "dim",    text: `` },
  { cls: "info",   text: `--- ${target} ping statistics ---` },
  { cls: "ok",     text: `7 packets transmitted, 7 received, 0% packet loss, time 6011ms` },
  { cls: "ok",     text: `rtt min/avg/max/mdev = 3.920/4.073/4.210/0.094 ms` },
];

const TRACE_OUTPUT = [
  { hop: 1, ip: "10.0.0.1",        host: "br-edge-01.webstorage.net", asn: "AS263870", as: "Webstorage", ms: "0.4 / 0.5 / 0.4", ix: false },
  { hop: 2, ip: "187.16.220.1",    host: "border1.sp.telefonica.com",  asn: "AS12956",  as: "Telefónica", ms: "1.8 / 1.9 / 1.8", ix: false },
  { hop: 3, ip: "200.219.130.45",  host: "sp.ptt.br",                  asn: "AS262332", as: "IX.br SP",   ms: "2.6 / 2.7 / 2.5", ix: true  },
  { hop: 4, ip: "200.219.130.118", host: "google-pe.sp.ptt.br",        asn: "AS262332", as: "IX.br SP",   ms: "2.9 / 3.0 / 2.8", ix: true  },
  { hop: 5, ip: "108.170.243.1",   host: "tata.bba.google.com",        asn: "AS15169",  as: "Google",     ms: "3.4 / 3.5 / 3.3", ix: false },
  { hop: 6, ip: "142.250.227.142", host: "iad23s90.gmail.com",         asn: "AS15169",  as: "Google",     ms: "4.1 / 4.2 / 4.0", ix: false },
  { hop: 7, ip: "8.8.8.8",         host: "dns.google",                 asn: "AS15169",  as: "Google",     ms: "4.0 / 4.0 / 4.1", ix: false },
];

const SSH_OUTPUT = (host) => [
  { cls: "dim",  text: `$ ssh ${host.user}@${host.ip} -p ${host.port}` },
  { cls: "info", text: `The authenticity of host '${host.ip} (${host.ip})' can't be established.` },
  { cls: "dim",  text: `ED25519 key fingerprint is SHA256:qXyZ7n2lP9b8e1F4hT5R3wK6vN0jM2sO7uA1cD9gE3I.` },
  { cls: "dim",  text: `Are you sure you want to continue connecting (yes/no/[fingerprint])? yes` },
  { cls: "ok",   text: `Warning: Permanently added '${host.ip}' (ED25519) to the list of known hosts.` },
  { cls: "ok",   text: `${host.user}@${host.ip}'s password: ********` },
  { cls: "dim",  text: `` },
  { cls: "info", text: `  MikroTik RouterOS 7.13.5` },
  { cls: "info", text: `  ┌─────────────────────────────────────────────┐` },
  { cls: "info", text: `  │  ${host.hostname.padEnd(20)} BGP / MPLS PE Router  │` },
  { cls: "info", text: `  └─────────────────────────────────────────────┘` },
  { cls: "dim",  text: `` },
  { cls: "ok",   text: `Last login: Mon May 26 14:08:42 2026 from 10.0.5.5` },
  { cls: "ok",   text: `[${host.user}@${host.hostname}] > /routing bgp peer print` },
  { cls: "dim",  text: `Flags: X - disabled, E - established` },
  { cls: "info", text: ` #   NAME            INSTANCE   REMOTE-ADDRESS    REMOTE-AS   STATE` },
  { cls: "info", text: ` 0 E ix-sp-rs1       default    200.219.130.1     262332      established` },
  { cls: "info", text: ` 1 E ix-sp-rs2       default    200.219.130.2     262332      established` },
  { cls: "info", text: ` 2 E telefonica-1    default    187.16.220.1      12956       established` },
  { cls: "info", text: ` 3 E cogent-1        default    38.122.18.21      174         established` },
  { cls: "info", text: ` 4 E google-direct   default    8.8.4.4           15169       established` },
  { cls: "ok",   text: `[${host.user}@${host.hostname}] >` },
];

function PingTab() {
  const [target, setTarget] = useState("8.8.8.8");
  const [running, setRunning] = useState(false);
  const [lines, setLines] = useState([]);

  const run = () => {
    setRunning(true); setLines([{ cls: "dim", text: `$ ping -c 7 ${target}` }]);
    const out = PING_OUTPUT(target);
    out.forEach((ln, i) => {
      setTimeout(() => {
        setLines(prev => [...prev, ln]);
        if (i === out.length - 1) setRunning(false);
      }, 120 + i * 130);
    });
  };

  return (
    <div>
      <div className="tool-input-row" style={{ marginBottom: 14 }}>
        <input className="input" placeholder="IP ou hostname (ex: 8.8.8.8)" value={target} onChange={(e) => setTarget(e.target.value)}/>
        <select className="select" style={{ width: 140 }}><option>7 pacotes</option><option>10 pacotes</option><option>30 pacotes</option><option>Contínuo</option></select>
        <button className="btn btn-primary" onClick={run} disabled={running}><Icon name="play" size={12}/>Executar</button>
      </div>
      <div className="card card-tight">
        <div className="term-bar">
          <div className="dot-r"></div><div className="dot-y"></div><div className="dot-g"></div>
          <div className="term-title">~/ping {target}</div>
          <div style={{ flex: 1 }}></div>
          {running ? <span className="badge badge-green"><span className="ix-dot"></span>executando</span> : <span className="badge badge-gray">pronto</span>}
        </div>
        <div className="term" style={{ minHeight: 360, borderRadius: 0, border: "none" }}>
          {lines.length === 0 && <span className="dim">{`// Resultados aparecerão aqui após executar.`}</span>}
          {lines.map((l, i) => (<span key={i} className={"ln " + l.cls}>{l.text || "\u00A0"}</span>))}
          {running && <span className="cursor"></span>}
        </div>
      </div>
    </div>
  );
}

function TracerouteTab() {
  const [target, setTarget] = useState("8.8.8.8");
  const [running, setRunning] = useState(false);
  const [hops, setHops] = useState([]);

  const run = () => {
    setRunning(true); setHops([]);
    TRACE_OUTPUT.forEach((h, i) => {
      setTimeout(() => {
        setHops(prev => [...prev, h]);
        if (i === TRACE_OUTPUT.length - 1) setRunning(false);
      }, 250 + i * 220);
    });
  };

  return (
    <div>
      <div className="tool-input-row" style={{ marginBottom: 14 }}>
        <input className="input" placeholder="IP ou hostname destino" value={target} onChange={(e) => setTarget(e.target.value)}/>
        <select className="select" style={{ width: 160 }}><option>ICMP</option><option>UDP</option><option>TCP/443</option></select>
        <button className="btn btn-primary" onClick={run} disabled={running}><Icon name="play" size={12}/>Executar</button>
      </div>
      <div className="table-wrap">
        <table className="t">
          <thead>
            <tr>
              <th style={{ width: 50 }}>#</th>
              <th style={{ width: 150 }}>IP</th>
              <th>Hostname</th>
              <th style={{ width: 100 }}>ASN</th>
              <th>Nome AS</th>
              <th style={{ width: 160 }}>RTT (ms)</th>
            </tr>
          </thead>
          <tbody>
            {hops.length === 0 && (
              <tr><td colSpan="6" style={{ textAlign: "center", color: "var(--text-mute)", padding: 32 }}>
                {running ? "Sondando hops..." : "Aguardando execução."}
              </td></tr>
            )}
            {hops.map(h => (
              <tr key={h.hop}>
                <td className="mono" style={{ color: "var(--text-mute)" }}>{h.hop}</td>
                <td className="mono">{h.ip}</td>
                <td style={{ color: "var(--text-dim)" }}>{h.host}</td>
                <td><span className={"badge " + (h.ix ? "badge-purple" : "badge-blue")}>{h.asn}</span></td>
                <td>{h.as} {h.ix && <span className="badge badge-purple" style={{ marginLeft: 6, fontSize: 9 }}>IX/PTT</span>}</td>
                <td className="mono" style={{ color: "var(--green)" }}>{h.ms}</td>
              </tr>
            ))}
            {running && hops.length < TRACE_OUTPUT.length && (
              <tr>
                <td className="mono" style={{ color: "var(--text-mute)" }}>{hops.length + 1}</td>
                <td colSpan="5" className="mono dim" style={{ color: "var(--text-mute)" }}>* * * sondando...</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ShellTab({ kind }) {
  const isSsh = kind === "ssh";
  const [mode, setMode] = useState("saved");
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [manualIp, setManualIp] = useState("");
  const [manualPort, setManualPort] = useState(isSsh ? 22 : 23);
  const [manualUser, setManualUser] = useState("");
  const [pwd, setPwd] = useState("");
  const [running, setRunning] = useState(false);
  const [lines, setLines] = useState([]);
  const [cmd, setCmd] = useState("");

  const connect = () => {
    const host = mode === "saved" ? NT_HOSTS[selectedIdx] : { hostname: manualIp, ip: manualIp, user: manualUser, port: manualPort };
    setRunning(true); setLines([]);
    const out = SSH_OUTPUT(host);
    out.forEach((ln, i) => {
      setTimeout(() => {
        setLines(prev => [...prev, ln]);
        if (i === out.length - 1) setRunning(false);
      }, 80 + i * 100);
    });
  };

  const sendCmd = (e) => {
    e.preventDefault();
    if (!cmd.trim()) return;
    const host = mode === "saved" ? NT_HOSTS[selectedIdx] : { hostname: manualIp, user: manualUser };
    setLines(prev => [...prev,
      { cls: "ok", text: `[${host.user}@${host.hostname}] > ${cmd}` },
      { cls: "dim", text: `(${cmd.split(" ")[0]} OK — output simulado)` },
    ]);
    setCmd("");
  };

  return (
    <div className="split-2">
      <div className="card">
        <div className="card-header">
          <h3>{isSsh ? "Conexão SSH" : "Conexão Telnet"}</h3>
        </div>
        <div className="card-body" style={{ display: "grid", gap: 14 }}>
          <div className="tabs" style={{ width: "100%", padding: 4 }}>
            <div className={"tab" + (mode === "saved" ? " active" : "")} onClick={() => setMode("saved")} style={{ flex: 1, justifyContent: "center" }}>Host cadastrado</div>
            <div className={"tab" + (mode === "manual" ? " active" : "")} onClick={() => setMode("manual")} style={{ flex: 1, justifyContent: "center" }}>Manual</div>
          </div>

          {mode === "saved" ? (
            <Field label="Selecione um host">
              <select className="select" value={selectedIdx} onChange={(e) => setSelectedIdx(+e.target.value)}>
                {NT_HOSTS.map((h, i) => (<option key={h.hostname} value={i}>{h.hostname} — {h.ip}</option>))}
              </select>
            </Field>
          ) : (
            <>
              <div className="grid-2">
                <Field label="IP / Host"><input className="input" value={manualIp} onChange={(e) => setManualIp(e.target.value)} placeholder="10.0.0.1"/></Field>
                <Field label="Porta"><input className="input" type="number" value={manualPort} onChange={(e) => setManualPort(+e.target.value)}/></Field>
              </div>
              <Field label="Usuário"><input className="input" value={manualUser} onChange={(e) => setManualUser(e.target.value)} placeholder="netadmin"/></Field>
            </>
          )}
          <Field label="Senha"><input className="input" type="password" value={pwd} onChange={(e) => setPwd(e.target.value)} placeholder="••••••••"/></Field>
          <button className="btn btn-primary" onClick={connect} disabled={running}>
            <Icon name={isSsh ? "ssh" : "telnet"} size={13}/>{running ? "Conectando..." : `Conectar ${isSsh ? "SSH" : "Telnet"}`}
          </button>
          <div style={{ fontSize: 11, color: "var(--text-mute)", lineHeight: 1.5 }}>
            {isSsh
              ? "Conexão criptografada. Suporta autenticação por chave (~/.ssh/id_ed25519) ou senha."
              : "⚠ Telnet transmite credenciais em texto puro. Use apenas em redes management isoladas."}
          </div>
        </div>
      </div>

      <div className="card card-tight" style={{ minHeight: 540 }}>
        <div className="term-bar">
          <div className="dot-r"></div><div className="dot-y"></div><div className="dot-g"></div>
          <div className="term-title">
            {mode === "saved" ? `${NT_HOSTS[selectedIdx].user}@${NT_HOSTS[selectedIdx].hostname}` : `${manualUser || "user"}@${manualIp || "host"}`}
          </div>
          <div style={{ flex: 1 }}></div>
          {lines.length > 0 ? <span className="badge badge-green"><span className="ix-dot"></span>conectado</span> : <span className="badge badge-gray">desconectado</span>}
        </div>
        <div className="term" style={{ minHeight: 450, borderRadius: 0, border: "none" }}>
          {lines.length === 0
            ? <span className="dim">{`// Pressione "Conectar ${isSsh ? "SSH" : "Telnet"}" para iniciar uma sessão.`}</span>
            : lines.map((l, i) => (<span key={i} className={"ln " + l.cls}>{l.text || "\u00A0"}</span>))}
          {running && <span className="cursor"></span>}
        </div>
        {lines.length > 0 && !running && (
          <form onSubmit={sendCmd} style={{ display: "flex", gap: 8, padding: 10, borderTop: "1px solid rgba(255,255,255,0.05)", background: "#050810" }}>
            <span className="mono" style={{ color: "var(--accent-2)", padding: "8px 4px" }}>{">"}</span>
            <input className="input" style={{ background: "transparent", border: "none", padding: 6, fontFamily: "JetBrains Mono, monospace" }}
                   value={cmd} onChange={(e) => setCmd(e.target.value)}
                   placeholder="digite um comando e enter..."/>
          </form>
        )}
      </div>
    </div>
  );
}

function NetworkTools() {
  const [tab, setTab] = useState("ping");
  const tabs = [
    { id: "ping",    label: "Ping",       icon: "ping" },
    { id: "trace",   label: "Traceroute", icon: "route" },
    { id: "ssh",     label: "SSH",        icon: "ssh" },
    { id: "telnet",  label: "Telnet",     icon: "telnet" },
  ];
  return (
    <div data-screen-label="04 Network Tools">
      <PageHead
        title="Network"
        accent="Tools"
        sub="Diagnóstico de conectividade, latência e acesso CLI remoto."
      />
      <div className="tabs">
        {tabs.map(t => (
          <div key={t.id} className={"tab" + (tab === t.id ? " active" : "")} onClick={() => setTab(t.id)}>
            <Icon name={t.icon} size={14}/>{t.label}
          </div>
        ))}
      </div>
      {tab === "ping"   && <PingTab/>}
      {tab === "trace"  && <TracerouteTab/>}
      {tab === "ssh"    && <ShellTab kind="ssh"/>}
      {tab === "telnet" && <ShellTab kind="telnet"/>}
    </div>
  );
}

window.NetworkTools = NetworkTools;
