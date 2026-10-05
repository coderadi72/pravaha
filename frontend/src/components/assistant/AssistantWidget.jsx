import { useEffect, useRef, useState } from "react";
import { assistantApi } from "../../api/assistant.js";
import { resolveApiUrl } from "../../api/config.js";
import { catalogue, detailLabels, modernLabels, conversationLabels, getSuggestions } from "./catalogue.js";
import Robot from "./Robot.jsx";
import "../../styles/assistant.css";
import { useUiPreferences } from "../../ui/useUiPreferences.js";

function EvidenceRecord({ record }) {
  return <dl className="pr-assistant-facts">{Object.entries(record.data).map(([key, value]) => <div key={key}><dt>{key}</dt><dd>{value == null ? "UNKNOWN" : typeof value === "object" ? JSON.stringify(value, null, 2) : String(value)}</dd></div>)}</dl>;
}

function AnswerContent({ answer }) {
  return <div className="pr-assistant-answer">{answer.claims.map((claim, index) => <section key={index}>{claim.title && <h3>{claim.title}</h3>}{claim.text.split(/\n\s*\n/).map((paragraph, i) => {
    const lines = paragraph.split("\n");
    if (lines.length > 2 && /^\s*\|?\s*:?-{3,}:?\s*\|[\s|:-]+$/.test(lines[1])) {
      const cells = (line) => line.trim().replace(/^\||\|$/g, "").split("|").map((cell) => cell.trim());
      const headings = cells(lines[0]);
      return <div className="pr-assistant-table" key={i}><table><thead><tr>{headings.map((heading, j) => <th key={j} scope="col">{heading}</th>)}</tr></thead><tbody>{lines.slice(2).map((line, row) => <tr key={row}>{cells(line).slice(0, headings.length).map((cell, column) => <td key={column}>{cell}</td>)}</tr>)}</tbody></table></div>;
    }
    return lines.every((line) => /^\s*(?:[-•]|\d+[.)])\s+/.test(line)) ? <ul key={i}>{lines.map((line, j) => <li key={j}>{line.replace(/^\s*(?:[-•]|\d+[.)])\s+/, "")}</li>)}</ul> : <p key={i}>{paragraph}</p>;
  })}</section>)}</div>;
}

export default function AssistantWidget({ user, activities = [] }) {
  const [open, setOpen] = useState(false);
  const [config, setConfig] = useState(null);
  const [project, setProject] = useState("");
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [source, setSource] = useState(null);
  const [expired, setExpired] = useState(false);
  const [activity, setActivity] = useState("");
  const [moreSuggestions, setMoreSuggestions] = useState(false);
  const [responding, setResponding] = useState(false);
  const [copied, setCopied] = useState(null);
  const [copyError, setCopyError] = useState("");
  const { language } = useUiPreferences();
  const conversation = useRef(null), controller = useRef(null), epoch = useRef(0);
  const input = useRef(null), launcher = useRef(null), panel = useRef(null), messages = useRef(null), last = useRef(null);
  const sequence = useRef(0), stickToBottom = useRef(true);
  const lastResult = history.findLast((turn) => turn.result)?.result;
  const lang = lastResult?.language || language;
  const t = catalogue[lang] || catalogue.en;
  const ui = { ...(modernLabels[lang] || modernLabels.en), ...(conversationLabels[lang] || conversationLabels.en) };
  const prompts = getSuggestions(user.role, lang, project);
  const projectName = config?.projects.find((p) => p.id === project)?.name || (config?.organizationScope ? t.organization : t.choose);
  const roleLabel = { ADMIN: "Admin", PROJECT_MANAGER: "PM", TEAM_LEADER: "TL" }[user.role] || user.role;
  const boot = async () => {
    setError("");
    try { const data = await assistantApi.contexts(); setConfig(data); setProject(data.projects[0]?.id || ""); }
    catch (failure) {
      if ([401, 403].includes(failure.status)) { setExpired(true); setHistory([]); conversation.current = null; }
      setError(failure.message);
    }
  };
  useEffect(() => {
    const c = new AbortController();
    assistantApi.contexts(0, c.signal).then((data) => { setConfig(data); setProject(data.projects[0]?.id || ""); }).catch((failure) => { if (failure.name !== "AbortError") setError(failure.message); });
    return () => { c.abort(); controller.current?.abort(); epoch.current += 1; };
  }, []);
  useEffect(() => { if (open) input.current?.focus(); }, [open]);
  useEffect(() => { if (stickToBottom.current && messages.current) messages.current.scrollTop = messages.current.scrollHeight; }, [history, busy, source]);
  useEffect(() => {
    if (!responding) return;
    const timer = setTimeout(() => setResponding(false), 850);
    return () => clearTimeout(timer);
  }, [responding]);
  const cancel = () => { controller.current?.abort(); epoch.current += 1; setBusy(false); setError(t.cancelled); };
  const reset = () => { controller.current?.abort(); epoch.current += 1; setBusy(false); setHistory([]); setSource(null); setActivity(""); setQuestion(""); setError(""); setCopied(null); setCopyError(""); setResponding(false); setMoreSuggestions(false); conversation.current = null; last.current = null; stickToBottom.current = true; requestAnimationFrame(() => input.current?.focus()); };
  const minimize = () => { if (busy) cancel(); setOpen(false); requestAnimationFrame(() => launcher.current?.focus()); };
  const send = async (text = question, intent, retryId) => {
    if (!text.trim() || busy || expired) return;
    const version = ++epoch.current;
    controller.current?.abort(); controller.current = new AbortController();
    setBusy(true); setError(""); setCopyError(""); setSource(null); setQuestion(""); setResponding(false); stickToBottom.current = true;
    const id = retryId ?? ++sequence.current;
    const turn = { id, question: text, result: null, intent, guidanceVisible: false };
    setHistory((h) => retryId ? h.map((previous) => previous.id === id ? turn : previous) : [...h.slice(-Math.max(0, (config?.historyLimit || 8) - 1)), turn].slice(-(config?.historyLimit || 8)));
    const body = { question: text, intent, project_id: project || null, activity_id: activity || null, language, conversation: conversation.current };
    last.current = { text, intent, id };
    try {
      const result = await assistantApi.ask(body, controller.current.signal);
      if (epoch.current !== version) return;
      conversation.current = result.conversation;
      setHistory((h) => h.map((previous) => previous.id === id ? { ...previous, result } : previous));
      setResponding(result.mode === "AI");
    } catch (failure) {
      if (epoch.current !== version) return;
      if ([401, 403].includes(failure.status)) { setHistory([]); conversation.current = null; setExpired(true); setError(t.expired); }
      else if (failure.code === "CONVERSATION_EXPIRED") { setHistory([]); conversation.current = null; setError(t.expired); }
      else setError(failure.name === "AbortError" ? t.cancelled : failure.message);
    } finally { if (epoch.current === version) setBusy(false); }
  };
  const inspect = async (event, path) => {
    event.preventDefault(); setError("");
    const version = ++epoch.current;
    controller.current?.abort(); controller.current = new AbortController(); setBusy(true); stickToBottom.current = true;
    try { const data = await assistantApi.source(path, controller.current.signal); if (epoch.current === version) setSource(data); }
    catch (failure) {
      if (epoch.current === version) {
        if ([401, 403, 409].includes(failure.status)) { setHistory([]); conversation.current = null; if (failure.status !== 409) setExpired(true); }
        setError(failure.message);
      }
    } finally { if (epoch.current === version) setBusy(false); }
  };
  const keyboard = (event) => {
    if (event.key === "Escape") { event.preventDefault(); minimize(); }
    if (event.key === "Tab") {
      const nodes = panel.current?.querySelectorAll("button:not(:disabled),select:not(:disabled),textarea:not(:disabled),a[href],summary");
      if (!nodes?.length) return;
      if (event.shiftKey && document.activeElement === nodes[0]) { event.preventDefault(); nodes[nodes.length - 1].focus(); }
      else if (!event.shiftKey && document.activeElement === nodes[nodes.length - 1]) { event.preventDefault(); nodes[0].focus(); }
    }
  };
  const copyResponse = async (turn) => {
    try {
      const answer = turn.result.answer;
      const text = [...answer.claims.map((claim) => [claim.title, claim.text].filter(Boolean).join("\n")), ...answer.assumptions, ...answer.uncertainty, ...answer.next_investigation].join("\n\n");
      await navigator.clipboard.writeText(text); setCopied(turn.id); setCopyError("");
    } catch { setCopyError(ui.copyFailed); }
  };
  const state = error ? "error" : busy ? "thinking" : responding ? "responding" : question ? "listening" : lastResult?.mode === "GUIDED_FALLBACK" ? "fallback" : lastResult?.mode === "AI" ? "success" : "idle";
  const composerKey = (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); send(); }
  };
  return <div className="pr-assistant-widget">
    {!open && <button ref={launcher} className="pr-assistant-launcher" type="button" aria-label={t.open} aria-expanded="false" onClick={() => setOpen(true)}><Robot /><span>{t.title}</span></button>}
    {open && <section ref={panel} className="pr-assistant-panel" role="dialog" aria-label={t.title} onKeyDown={keyboard}>
      <header><Robot state={state} /><div className="pr-assistant-identity"><h2>{t.title}</h2><small>{projectName} · {roleLabel}</small></div><div className="pr-assistant-header-actions"><button type="button" disabled={busy} onClick={reset} aria-label={t.reset} title={t.reset}>↺</button><button type="button" onClick={minimize} aria-label={t.close} title={t.close}>−</button></div></header>
      <div className="pr-assistant-context"><label>{ui.project}<select aria-label={t.context} value={project} disabled={busy || expired} onChange={(e) => { reset(); setProject(e.target.value); }}><option value="">{config?.organizationScope ? t.organization : t.choose}</option>{config?.projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}</select></label>
      <label>{ui.activity}<select aria-label={detailLabels[lang].activity} value={activity} disabled={busy} onChange={(e) => setActivity(e.target.value)}><option value="">{detailLabels[lang].all}</option>{activities.filter((a) => a.projectId === project && !a.archived).map((a) => <option key={a.id} value={a.id}>{a.activityId || a.id} · {a.activityName}</option>)}</select></label></div>
      {config?.hasMore && <button type="button" onClick={async () => { try { const next = await assistantApi.contexts(config.offset + config.limit); setConfig((c) => ({ ...next, projects: [...c.projects, ...next.projects] })); } catch (e) { setError(e.message); } }}>{detailLabels[lang].more}</button>}
      <div ref={messages} className="pr-assistant-messages" onScroll={() => { const container = messages.current; if (container) stickToBottom.current = container.scrollHeight - container.scrollTop - container.clientHeight < 56; }}>
        {config && config.providerStatus !== "CONFIGURED" && <p className="pr-assistant-notice">{t.disabled}</p>}
        {!config && error && <p className="pr-assistant-notice">{t.staticHelp}</p>}
        {!history.length && <><div className="pr-assistant-welcome"><span className="pr-assistant-scope">{roleLabel} · {user.organizationId}</span><h3>{ui.welcome}{user.name && `, ${user.name.split(/\s+/)[0]}`}</h3><p>{project && <strong>{projectName}. </strong>}{ui.intro}</p></div><div className="pr-assistant-suggestions">{prompts.slice(0, moreSuggestions ? undefined : 5).map(([intent, text, label]) => <button key={intent} title={text} type="button" disabled={!config || busy || expired} onClick={() => send(text, intent)}>{label}</button>)}{prompts.length > 5 && <button type="button" className="pr-assistant-more" aria-expanded={moreSuggestions} onClick={() => setMoreSuggestions((value) => !value)}>{moreSuggestions ? ui.less : ui.more}</button>}</div></>}
        {history.map((turn) => { const { id, question: q, result, intent, guidanceVisible } = turn; return <article className="pr-assistant-turn" key={id}><p className="pr-assistant-question">{q}</p>{result && <><div className="pr-assistant-response-heading"><Robot state={result.mode === "GUIDED_FALLBACK" ? "fallback" : result.mode === "AI" ? "success" : "idle"} /><span className={`pr-assistant-mode ${result.mode === "AI" ? "is-ai" : "is-guidance"}`}>{result.mode === "AI" ? t.ai : guidanceVisible ? ui.guidance : ui.assistant}</span>{(result.mode !== "GUIDED_FALLBACK" || guidanceVisible) && <button type="button" className="pr-assistant-copy" onClick={() => copyResponse(turn)}>{copied === id ? ui.copied : ui.copy}</button>}</div>
          {result.mode === "GUIDED_FALLBACK" && <div className="pr-assistant-notice"><p>{config?.providerStatus === "CONFIGURED" ? ui.unavailable : t.disabled}</p><div className="pr-assistant-fallback-actions"><button type="button" disabled={busy || expired} onClick={() => send(q, intent, id)}>{ui.retry}</button>{!guidanceVisible && <button type="button" onClick={() => setHistory((h) => h.map((previous) => previous.id === id ? { ...previous, guidanceVisible: true } : previous))}>{ui.useGuidance}</button>}</div></div>}
          {(result.mode !== "GUIDED_FALLBACK" || guidanceVisible) && <><AnswerContent answer={result.answer} /><small>{result.context.scope} · {result.context.projectName || result.context.organizationName} {result.context.teamId && `· ${result.context.teamId}`} · {result.context.dataLabel}</small>
          {result.checkedAt && <small>{t.checked}: {result.checkedAt}</small>}{result.partial && <p>{t.partial}</p>}
          {result.mode === "AI" && <small className="pr-assistant-advisory">{t.interpretation}</small>}
          {[...result.answer.assumptions, ...result.answer.uncertainty, ...result.answer.next_investigation].length > 0 && <details className="pr-assistant-notes"><summary>{ui.notes}</summary><ul>{[...result.answer.assumptions, ...result.answer.uncertainty, ...result.answer.next_investigation].map((note, i) => <li key={i}>{note}</li>)}</ul></details>}
          {result.evidence.length > 0 && <details><summary>{t.sources} ({result.evidence.length})</summary>{result.evidence.map((record) => <div className="pr-assistant-evidence" key={record.evidenceId}><strong>{record.recordId}</strong><small>{record.dataset} · {record.dataCategory} · {record.timestamp || "UNKNOWN"}</small><EvidenceRecord record={record} /><a href={resolveApiUrl(record.source)} onClick={(e) => inspect(e, record.source)}>{t.source}</a></div>)}</details>}</>}</>}
        </article>; })}
        {source && <article className="pr-assistant-source" tabIndex="-1"><h3>{t.sources}: {source.record.recordId}</h3><small>{t.checked}: {source.checkedAt} · {source.dataset}</small><EvidenceRecord record={source.record} />{source.limitations.map((note, i) => <p key={i}>{note}</p>)}</article>}
        {busy && <p className="pr-assistant-loading" role="status"><span aria-hidden="true"><i /><i /><i /></span>{history.at(-1)?.result ? ui.sourceLoading : ui.thinking}</p>}{error && <div role="alert"><p>{error}</p>{!expired && <button type="button" disabled={busy} onClick={() => last.current ? send(last.current.text, last.current.intent, last.current.id) : boot()}>{ui.retry}</button>}</div>}{copyError && <p role="status" className="pr-assistant-notice">{copyError}</p>}
      </div>
      <form onSubmit={(e) => { e.preventDefault(); send(); }}><label className="pr-assistant-sr" htmlFor="pr-assistant-question">{t.question}</label><div className="pr-assistant-composer"><textarea ref={input} id="pr-assistant-question" value={question} onKeyDown={composerKey} onChange={(e) => setQuestion(e.target.value)} placeholder={t.placeholder} maxLength={config?.questionLimit || 1200} disabled={busy || expired || !config} rows={Math.min(3, question.split("\n").length)} />{busy ? <button type="button" onClick={cancel} aria-label={t.cancel} title={t.cancel}>■</button> : <button type="submit" aria-label={ui.send} title={ui.send} disabled={!config || expired || !question.trim()}>↑</button>}</div><div className="pr-assistant-composer-meta"><small>{ui.enter}</small><small>{question.length}/{config?.questionLimit || 1200}</small></div></form>
    </section>}
  </div>;
}
