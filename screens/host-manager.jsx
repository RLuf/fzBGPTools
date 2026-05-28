// Host Manager — CRUD with action buttons

const INITIAL_HOSTS = [
  { id: 1, hostname: "br-edge-01",       ip: "10.0.0.1",      ssh: 22,  telnet: 23,  user: "netadmin",  type: "Router",   vendor: "MikroTik", group: "SP-Core",  status: "Online" },
  { id: 2, hostname: "br-edge-02",       ip: "10.0.0.2",      ssh: 22,  telnet: 23,  user: "netadmin",  type: "Router",   vendor: "MikroTik", group: "SP-Core",  status: "Online" },
  { id: 3, hostname: "br-bgp-rs",        ip: "10.0.0.10",     ssh: 22,  telnet: 23,  user: "ops",       type: "Router",   vendor: "Cisco",    group: "SP-Core",  status: "Online" },
  { id: 4, hostname: "sw-dc1-agg-01",    ip: "10.0.1.5",      ssh: 22,  telnet: 23,  user: "admin",     type: "Switch",   vendor: "Juniper",  group: "DC1",      status: "Online" },
  { id: 5, hostname: "sw-dc1-agg-02",    ip: "10.0.1.6",      ssh: 22,  telnet: 23,  user: "admin",     type: "Switch",   vendor: "Juniper",  group: "DC1",      status: "Offline" },
  { id: 6, hostname: "fw-perimeter-01",  ip: "10.0.0.250",    ssh: 22,  telnet: 23,  user: "secadmin",  type: "Firewall", vendor: "Cisco",    group: "Security", status: "Online" },
  { id: 7, hostname: "lookingglass",     ip: "200.149.1.50",  ssh: 22,  telnet: 23,  user: "lg",        type: "Server",   vendor: "Linux",    group: "Tools",    status: "Online" },
  { id: 8, hostname: "rs-ix-sp",         ip: "200.219.130.1", ssh: 22,  telnet: 23,  user: "peering",   type: "Router",   vendor: "Cisco",    group: "IX",       status: "Online" },
  { id: 9, hostname: "br-bgp-collector", ip: "10.0.5.5",      ssh: 22,  telnet: 23,  user: "collector", type: "Server",   vendor: "Linux",    group: "Tools",    status: "Online" },
  { id: 10,hostname: "mx-pe-01",         ip: "10.0.2.20",     ssh: 22,  telnet: 23,  user: "ne",        type: "Router",   vendor: "Juniper",  group: "PE",       status: "Online" },
];

const VENDOR_BADGE = {
  "MikroTik": "badge-blue",
  "Cisco":    "badge-cyan",
  "Juniper":  "badge-green",
  "Linux":    "badge-purple",
  "Outro":    "badge-gray",
};

function HostManager() {
  const [rows, setRows] = useState(INITIAL_HOSTS);
  const [q, setQ] = useState("");
  const [fType, setFType] = useState("Todos");
  const [editing, setEditing] = useState(null);

  const filtered = rows.filter(r => {
    if (q && !(`${r.hostname} ${r.ip} ${r.group}`).toLowerCase().includes(q.toLowerCase())) return false;
    if (fType !== "Todos" && r.type !== fType) return false;
    return true;
  });

  const onSave = (d) => {
    if (d.id) setRows(rows.map(r => r.id === d.id ? d : r));
    else setRows([{ ...d, id: Date.now(), status: "Online" }, ...rows]);
    setEditing(null);
  };
  const onDelete = (id) => { if (confirm("Remover este host?")) setRows(rows.filter(r => r.id !== id)); };

  return (
    <div data-screen-label="03 Host Manager">
      <PageHead
        title="Host"
        accent="Manager"
        sub="Inventário de roteadores, switches, firewalls e servidores. Conecte-se diretamente via SSH ou Telnet."
        actions={<>
          <button className="btn"><Icon name="refresh" size={14}/>Sondar status</button>
          <button className="btn btn-primary" onClick={() => setEditing({})}><Icon name="plus" size={14}/>Adicionar Host</button>
        </>}
      />

      <div className="filters">
        <Search value={q} onChange={setQ} placeholder="Buscar host, IP ou grupo..."/>
        <select className="select" value={fType} onChange={(e) => setFType(e.target.value)}>
          <option>Todos</option><option>Router</option><option>Switch</option><option>Server</option><option>Firewall</option>
        </select>
        <div style={{ flex: 1 }}></div>
        <span className="badge badge-green"><span className="ix-dot"></span>{rows.filter(r => r.status === "Online").length} online</span>
        <span className="badge badge-gray">{rows.filter(r => r.status === "Offline").length} offline</span>
      </div>

      <div className="table-wrap">
        <table className="t">
          <thead>
            <tr>
              <th>Hostname</th>
              <th style={{ width: 140 }}>IP</th>
              <th style={{ width: 70 }}>SSH</th>
              <th style={{ width: 70 }}>Telnet</th>
              <th style={{ width: 110 }}>Usuário</th>
              <th style={{ width: 100 }}>Tipo</th>
              <th style={{ width: 100 }}>Fabricante</th>
              <th style={{ width: 100 }}>Grupo</th>
              <th style={{ width: 90 }}>Status</th>
              <th style={{ width: 230, textAlign: "right" }}>Ações</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(r => (
              <tr key={r.id}>
                <td><div style={{ fontWeight: 600 }}>{r.hostname}</div></td>
                <td className="mono" style={{ fontSize: 11.5 }}>{r.ip}</td>
                <td className="mono" style={{ color: "var(--text-mute)" }}>{r.ssh}</td>
                <td className="mono" style={{ color: "var(--text-mute)" }}>{r.telnet}</td>
                <td className="mono" style={{ fontSize: 11.5 }}>{r.user}</td>
                <td><span className="badge badge-gray">{r.type}</span></td>
                <td><span className={"badge " + (VENDOR_BADGE[r.vendor] || "badge-gray")}>{r.vendor}</span></td>
                <td><span className="mono" style={{ fontSize: 11, color: "var(--text-dim)" }}>{r.group}</span></td>
                <td>
                  <span className={r.status === "Online" ? "badge badge-green" : "badge badge-gray"}>
                    <span className={"s-dot " + (r.status === "Online" ? "s-on" : "s-off")} style={{ marginRight: 0 }}></span>
                    {r.status}
                  </span>
                </td>
                <td>
                  <div className="t-actions">
                    <button className="btn btn-sm" title="SSH"><Icon name="ssh" size={12}/>SSH</button>
                    <button className="btn btn-sm" title="Telnet"><Icon name="telnet" size={12}/>Tel</button>
                    <button className="btn btn-sm btn-icon" title="Ping"><Icon name="ping" size={13}/></button>
                    <button className="btn btn-sm btn-icon" title="Traceroute"><Icon name="route" size={13}/></button>
                    <button className="btn btn-sm btn-icon" title="Editar" onClick={() => setEditing(r)}><Icon name="edit" size={13}/></button>
                    <button className="btn btn-sm btn-icon btn-danger" title="Remover" onClick={() => onDelete(r.id)}><Icon name="trash" size={13}/></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {editing && <HostModal initial={editing} onClose={() => setEditing(null)} onSave={onSave}/>}
    </div>
  );
}

function HostModal({ initial, onClose, onSave }) {
  const [f, setF] = useState({
    id: initial.id,
    hostname: initial.hostname || "",
    ip: initial.ip || "",
    ssh: initial.ssh || 22,
    telnet: initial.telnet || 23,
    user: initial.user || "",
    password: "",
    type: initial.type || "Router",
    vendor: initial.vendor || "MikroTik",
    group: initial.group || "",
  });
  const set = (k, v) => setF({ ...f, [k]: v });
  return (
    <Modal
      title={initial.id ? `Editar ${initial.hostname}` : "Adicionar novo Host"}
      onClose={onClose}
      width={620}
      footer={<>
        <button className="btn" onClick={onClose}>Cancelar</button>
        <button className="btn btn-primary" onClick={() => onSave(f)}>{initial.id ? "Salvar alterações" : "Adicionar Host"}</button>
      </>}
    >
      <div className="grid-2">
        <Field label="Hostname"><input className="input" placeholder="br-edge-01" value={f.hostname} onChange={(e) => set("hostname", e.target.value)}/></Field>
        <Field label="Endereço IP"><input className="input" placeholder="10.0.0.1" value={f.ip} onChange={(e) => set("ip", e.target.value)}/></Field>
      </div>
      <div className="grid-3">
        <Field label="Porta SSH"><input className="input" type="number" value={f.ssh} onChange={(e) => set("ssh", +e.target.value)}/></Field>
        <Field label="Porta Telnet"><input className="input" type="number" value={f.telnet} onChange={(e) => set("telnet", +e.target.value)}/></Field>
        <Field label="Grupo"><input className="input" placeholder="SP-Core" value={f.group} onChange={(e) => set("group", e.target.value)}/></Field>
      </div>
      <div className="grid-2">
        <Field label="Usuário"><input className="input" placeholder="netadmin" value={f.user} onChange={(e) => set("user", e.target.value)}/></Field>
        <Field label="Senha"><input className="input" type="password" placeholder="••••••••" value={f.password} onChange={(e) => set("password", e.target.value)}/></Field>
      </div>
      <div className="grid-2">
        <Field label="Tipo">
          <select className="select" value={f.type} onChange={(e) => set("type", e.target.value)}>
            <option>Router</option><option>Switch</option><option>Server</option><option>Firewall</option>
          </select>
        </Field>
        <Field label="Fabricante">
          <select className="select" value={f.vendor} onChange={(e) => set("vendor", e.target.value)}>
            <option>MikroTik</option><option>Cisco</option><option>Juniper</option><option>Linux</option><option>Outro</option>
          </select>
        </Field>
      </div>
    </Modal>
  );
}

window.HostManager = HostManager;
