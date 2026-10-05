import UiText from "../../ui/UiText.jsx";
import { useState } from "react";
import { ingestionApi } from "../../api/client.js";
import { resolveApiUrl } from "../../api/config.js";
export default function FieldEvidence({ update }) {
  const [files, setFiles] = useState(null), [message, setMessage] = useState(""), [busy, setBusy] = useState(false);
  async function load() { setBusy(true); try { setFiles((await ingestionApi.attachments(update.id)).items); } catch (e) { setMessage(e.message); } finally { setBusy(false); } }
  return <details className="ingestion-panel"><summary><UiText>Structured details and attachments</UiText></summary>{["quantity", "unit", "remarks", "blocker", "crew", "equipment"].filter(k => update[k] != null && update[k] !== "").map(k => <p key={k}><strong>{k}:</strong> {update[k]}</p>)}<button type="button" disabled={busy} onClick={load}><UiText>Load attachments</UiText></button>{files?.length === 0 && <p><UiText>No persisted attachments.</UiText></p>}{files?.map(f => <article key={f.id}><p><a href={resolveApiUrl(`/api/attachments/${encodeURIComponent(f.id)}`)}>{f.filename}</a> · {f.mimeType} · {f.size}<UiText> bytes</UiText></p><small><UiText>Uploaded </UiText>{new Date(f.createdAt).toLocaleString()}<UiText> · checksum </UiText>{f.checksum}</small>{["ocr", "asr", "advanced"].map(provider => <button key={provider} type="button" disabled={busy} onClick={async () => { setBusy(true); try { const r = await ingestionApi.process(f.id, provider); setMessage(`${provider}: ${r.status}. ${r.reason}`); } catch (e) { setMessage(e.message); } finally { setBusy(false); } }}><UiText>Request </UiText>{provider}</button>)}</article>)}{message && <p role="status">{message}</p>}</details>;
}
