// ASN Manager — CRUD

const INITIAL_ASN = [
  { id: 1, asn: "263870", org: "Webstorage Provedor",  ranges: "200.149.0.0/16, 2804:7f0::/32", country: "BR", type: "Próprio",  status: "Ativo",   date: "2019-04-12" },
  { id: 2, asn: "262332", org: "IX.br SP (NIC.br)",    ranges: "200.219.128.0/20",              country: "BR", type: "IX",       status: "Ativo",   date: "2020-08-03" },
  { id: 3, asn: "12956",  org: "Telefónica Backbone",  ranges: "213.140.0.0/16, 2a02:8800::/32", country: "ES", type: "Trânsito", status: "Ativo",   date: "2019-04-15" },
  { id: 4, asn: "174",    org: "Cogent Communications",ranges: "38.0.0.0/8, 2001:550::/32",      country: "US", type: "Trânsito", status: "Ativo",   date: "2019-06-22" },
  { id: 5, asn: "15169",  org: "Google LLC",           ranges: "8.8.8.0/24, 142.250.0.0/15",    country: "US", type: "Peer",     status: "Ativo",   date: "2021-02-18" },
  { id: 6, asn: "16509",  org: "Amazon AWS",           ranges: "52.0.0.0/11, 2600:1f00::/24",   country: "US", type: "Peer",     status: "Ativo",   date: "2021-05-30" },
  { id: 7, asn: "32934",  org: "Meta / Facebook",      ranges: "31.13.24.0/21, 157.240.0.0/16", country: "US", type: "Peer",     status: "Ativo",   date: "2022-01-09" },
  { id: 8, asn: "13335",  org: "Cloudflare Inc.",      ranges: "1.1.1.0/24, 104.16.0.0/12",     country: "US", type: "Peer",     status: "Ativo",   date: "2022-03-14" },
  { id: 9, asn: "53013",  org: "Locaweb Serviços",     ranges: "186.202.0.0/16",                country: "BR", type: "Peer",     status: "Inativo", date: "2020-11-02" },
  { id: 10,asn: "28571",  org: "RNP Brasil",            ranges: "200.143.192.0/18",              country: "BR", type: "Peer",     status: "Ativo",   date: "2023-07-21" },
];

const TYPE_BADGE = {
  "Próprio":  "badge-blue",
  "Peer":     "badge-cyan",
  "Trânsito": "badge-gray",
  "IX":       "badge-purple",
};

function AsnManager() {
  const [rows, setRows] = useState(INITIAL_ASN);
  const [q, setQ] = useState("");
  const [fType, setFType] = useState("Todos");
  const [fStatus, setFStatus] = useState("Todos");
  const [editing, setEditing] = useState(null);

  const filtered = rows.filter(r => {
    if (q && !(`${r.asn} ${r.org} ${r.ranges}`).toLowerCase().includes(q.toLowerCase())) return false;
    if (fType !== "Todos" && r.type !== fType) return false;
    if (fStatus !== "Todos" && r.status !== fStatus) return false;
    return true;
  });

  const onSave = (data) => {
    if (data.id) {
      setRows(rows.map(r => r.id === data.id ? data : r));
    } else {
      setRows([{ ...data, id: Date.now(), date: new Date().toISOString().slice(0,10) }, ...rows]);
    }
    setEditing(null);
  };

  const onDelete = (id) => {
    if (confirm("Remover este ASN?")) setRows(rows.filter(r => r.id !== id));
  };

  return (
    <div data-screen-label="02 ASN Manager">
      <PageHead
        title="ASN"
        accent="Manager"
        sub="Cadastro e governança de números de sistema autônomo, prefixos e relações de peering."
        actions={<>
          <button className="btn"><Icon name="upload" size={14}/>Importar CSV</button>
          <button className="btn"><Icon name="download" size={14}/>Exportar CSV</button>
          <button className="btn btn-primary" onClick={() => setEditing({})}><Icon name="plus" size={14}/>Adicionar ASN</button>
        </>}
      />

      <div className="stats" style={{ gridTemplateColumns: "repeat(4, 1fr)" }}>
        <div className="stat"><div className="lbl">Total ASNs</div><div className="val">{rows.length}</div><div className="delta up">Próprios · Peers · Trânsito</div></div>
        <div className="stat"><div className="lbl">Próprios</div><div className="val">{rows.filter(r => r.type === "Próprio").length}</div><div className="delta">Originados por nós</div></div>
        <div className="stat"><div className="lbl">Peers</div><div className="val">{rows.filter(r => r.type === "Peer").length}</div><div className="delta up">Diretos + via IX</div></div>
        <div className="stat"><div className="lbl">Trânsito</div><div className="val">{rows.filter(r => r.type === "Trânsito").length}</div><div className="delta">Upstream providers</div></div>
      </div>

      <div className="filters">
        <Search value={q} onChange={setQ} placeholder="Buscar ASN, organização ou prefixo..."/>
        <select className="select" value={fType} onChange={(e) => setFType(e.target.value)}>
          <option>Todos</option><option>Próprio</option><option>Peer</option><option>Trânsito</option><option>IX</option>
        </select>
        <select className="select" value={fStatus} onChange={(e) => setFStatus(e.target.value)}>
          <option>Todos</option><option>Ativo</option><option>Inativo</option>
        </select>
        <div style={{ flex: 1 }}></div>
        <span className="badge badge-gray">{filtered.length} resultados</span>
      </div>

      <div className="table-wrap">
        <table className="t">
          <thead>
            <tr>
              <th style={{ width: 100 }}>ASN</th>
              <th>Organização</th>
              <th>Prefixos / Ranges</th>
              <th style={{ width: 60 }}>País</th>
              <th style={{ width: 110 }}>Tipo</th>
              <th style={{ width: 100 }}>Status</th>
              <th style={{ width: 120 }}>Cadastro</th>
              <th style={{ width: 130, textAlign: "right" }}>Ações</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(r => (
              <tr key={r.id}>
                <td><span className="mono" style={{ fontWeight: 700 }}>AS{r.asn}</span></td>
                <td><div style={{ fontWeight: 600 }}>{r.org}</div></td>
                <td><span className="mono" style={{ fontSize: 11.5, color: "var(--text-dim)" }}>{r.ranges}</span></td>
                <td><span className="badge badge-gray">{r.country}</span></td>
                <td><span className={"badge " + (TYPE_BADGE[r.type] || "badge-gray")}>{r.type}</span></td>
                <td>
                  <span className={"badge " + (r.status === "Ativo" ? "badge-green" : "badge-gray")}>
                    <span className="ix-dot"></span>{r.status}
                  </span>
                </td>
                <td className="mono" style={{ fontSize: 11.5, color: "var(--text-mute)" }}>{r.date}</td>
                <td>
                  <div className="t-actions">
                    <button className="btn btn-sm btn-icon" title="Editar" onClick={() => setEditing(r)}><Icon name="edit" size={13}/></button>
                    <button className="btn btn-sm btn-icon btn-danger" title="Remover" onClick={() => onDelete(r.id)}><Icon name="trash" size={13}/></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {editing && <AsnModal initial={editing} onClose={() => setEditing(null)} onSave={onSave}/>}
    </div>
  );
}

function AsnModal({ initial, onClose, onSave }) {
  const [f, setF] = useState({
    id: initial.id,
    asn: initial.asn || "",
    org: initial.org || "",
    ranges: initial.ranges || "",
    country: initial.country || "BR",
    type: initial.type || "Peer",
    status: initial.status || "Ativo",
  });
  const set = (k, v) => setF({ ...f, [k]: v });
  return (
    <Modal
      title={initial.id ? `Editar AS${initial.asn}` : "Adicionar novo ASN"}
      onClose={onClose}
      footer={<>
        <button className="btn" onClick={onClose}>Cancelar</button>
        <button className="btn btn-primary" onClick={() => onSave(f)}>{initial.id ? "Salvar alterações" : "Adicionar ASN"}</button>
      </>}
    >
      <div className="grid-2">
        <Field label="Número ASN"><input className="input" placeholder="263870" value={f.asn} onChange={(e) => set("asn", e.target.value)}/></Field>
        <Field label="País">
          <select className="select" value={f.country} onChange={(e) => set("country", e.target.value)}>
            <option>BR</option><option>US</option><option>ES</option><option>AR</option><option>CL</option><option>DE</option>
          </select>
        </Field>
      </div>
      <Field label="Nome da organização" full>
        <input className="input" placeholder="Ex: Cloudflare Inc." value={f.org} onChange={(e) => set("org", e.target.value)}/>
      </Field>
      <Field label="Prefixos / Ranges (CIDR — separe múltiplos com vírgula, espaço ou nova linha)" full>
        <CidrInput value={f.ranges} onChange={(v) => set("ranges", v)}/>
      </Field>
      <div className="grid-2">
        <Field label="Tipo">
          <select className="select" value={f.type} onChange={(e) => set("type", e.target.value)}>
            <option>Próprio</option><option>Peer</option><option>Trânsito</option><option>IX</option>
          </select>
        </Field>
        <Field label="Status">
          <select className="select" value={f.status} onChange={(e) => set("status", e.target.value)}>
            <option>Ativo</option><option>Inativo</option>
          </select>
        </Field>
      </div>
    </Modal>
  );
}

window.AsnManager = AsnManager;

// ─── Multi-CIDR chip input ───────────────────────────────────────────────
function parseCidrs(str) {
  return (str || "").split(/[,\s\n]+/).map(s => s.trim()).filter(Boolean);
}

function validateCidr(c) {
  // very loose validation: IPv4 a.b.c.d/n or IPv6 with ::/n
  const v4 = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\/(\d{1,2})$/;
  const v6 = /^[0-9a-f:]+\/\d{1,3}$/i;
  if (v4.test(c)) {
    const m = c.match(v4);
    const ok = m.slice(1, 5).every(o => +o >= 0 && +o <= 255) && +m[5] <= 32;
    return ok ? "v4" : "bad";
  }
  if (v6.test(c) && c.includes(":")) return "v6";
  return "bad";
}

function CidrInput({ value, onChange }) {
  const [draft, setDraft] = useState("");
  const items = parseCidrs(value);
  const inputRef = useRef(null);

  const add = (txt) => {
    const next = parseCidrs(txt);
    if (!next.length) return;
    const merged = Array.from(new Set([...items, ...next]));
    onChange(merged.join(", "));
    setDraft("");
  };
  const remove = (i) => {
    const next = items.filter((_, idx) => idx !== i);
    onChange(next.join(", "));
  };

  const onKey = (e) => {
    if (e.key === "Enter" || e.key === "," || e.key === " " || e.key === "Tab") {
      if (draft.trim()) {
        e.preventDefault();
        add(draft);
      }
    } else if (e.key === "Backspace" && !draft && items.length) {
      remove(items.length - 1);
    }
  };

  const onPaste = (e) => {
    const text = (e.clipboardData || window.clipboardData).getData("text");
    if (text && /[,\s\n]/.test(text)) {
      e.preventDefault();
      add(text);
    }
  };

  return (
    <div>
      <div
        onClick={() => inputRef.current && inputRef.current.focus()}
        style={{
          background: "rgba(11,15,25,0.6)",
          border: "1px solid var(--border)",
          borderRadius: 9,
          padding: "8px 10px",
          minHeight: 80,
          display: "flex",
          flexWrap: "wrap",
          gap: 6,
          alignContent: "flex-start",
          cursor: "text",
        }}>
        {items.map((c, i) => {
          const k = validateCidr(c);
          const cls = k === "v4" ? "badge-blue" : k === "v6" ? "badge-purple" : "badge-red";
          return (
            <span key={i} className={"badge " + cls}
                  style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 11, padding: "4px 8px", gap: 6 }}>
              {k === "bad" && <Icon name="alert" size={10}/>}
              {c}
              <button onClick={(e) => { e.stopPropagation(); remove(i); }}
                      style={{ background: "transparent", border: "none", color: "inherit", cursor: "pointer", padding: 0, opacity: 0.6, display: "inline-flex" }}>
                <Icon name="x" size={11}/>
              </button>
            </span>
          );
        })}
        <input
          ref={inputRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKey}
          onPaste={onPaste}
          onBlur={() => draft.trim() && add(draft)}
          placeholder={items.length === 0 ? "200.149.0.0/16, 2804:7f0::/32, ..." : ""}
          style={{
            background: "transparent",
            border: "none",
            outline: "none",
            color: "var(--text)",
            fontFamily: "JetBrains Mono, monospace",
            fontSize: 12,
            flex: 1,
            minWidth: 180,
            padding: "4px 2px",
          }}
        />
      </div>
      <div style={{ display: "flex", gap: 12, marginTop: 6, fontSize: 11, color: "var(--text-mute)" }}>
        <span>{items.length} prefixo{items.length !== 1 ? "s" : ""}</span>
        <span>· IPv4: <span style={{ color: "#7ec3ff" }}>{items.filter(c => validateCidr(c) === "v4").length}</span></span>
        <span>· IPv6: <span style={{ color: "#c4b5ff" }}>{items.filter(c => validateCidr(c) === "v6").length}</span></span>
        {items.some(c => validateCidr(c) === "bad") && (
          <span style={{ color: "var(--red)" }}>· {items.filter(c => validateCidr(c) === "bad").length} inválido(s)</span>
        )}
        <span style={{ marginLeft: "auto" }}>Enter, espaço ou vírgula para adicionar</span>
      </div>
    </div>
  );
}

window.CidrInput = CidrInput;
