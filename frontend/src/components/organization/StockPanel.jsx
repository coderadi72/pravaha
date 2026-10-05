import UiText from "../../ui/UiText.jsx";
import { useEffect, useState } from 'react';
import { organizationApi } from '../../api/organization.js';

export default function StockPanel() {
  const [data, setData] = useState(null);
  const [query, setQuery] = useState('');
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    const timer = setTimeout(() => { organizationApi.stock(query, offset).then((r) => { if (active) { setData(r); setError(''); } }).catch((e) => { if (active) setError(e.message); }); }, 200);
    return () => { active = false; clearTimeout(timer); };
  }, [query,offset]);
  return <section className="org-panel"><h2><UiText>Inventory balances</UiText></h2><p className="org-muted"><UiText>Recorded receipts minus site issues, grouped by material and store. Material movements connect warehouse locations to project/team execution sites.</UiText></p><label><UiText>Search stock</UiText><input value={query} onChange={(e) => { setQuery(e.target.value); setOffset(0); }} /></label>{error && <p role="alert">{error}</p>}{data ? <><div className="org-table-scroll"><table><thead><tr><th><UiText>Store</UiText></th><th><UiText>Material</UiText></th><th><UiText>Unit</UiText></th><th><UiText>Available</UiText></th></tr></thead><tbody>{data.items.map((r) => <tr key={r.store_id+r.material_id}><td>{r.store}</td><td>{r.material}</td><td>{r.unit}</td><td>{r.balance}</td></tr>)}</tbody></table></div>{!data.total && <p><UiText>No receipts or issues recorded.</UiText></p>}<div className="org-pagination"><button type="button" disabled={!offset} onClick={() => setOffset(Math.max(0,offset-25))}><UiText>Previous stock</UiText></button><span>{data.total}<UiText> balances</UiText></span><button type="button" disabled={offset+25>=data.total} onClick={() => setOffset(offset+25)}><UiText>Next stock</UiText></button></div></> : !error && <p role="status"><UiText>Loading stock…</UiText></p>}</section>;
}
