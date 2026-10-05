import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { apiRequest } from "../frontend/src/api/client.js";
import { assistantApi } from "../frontend/src/api/assistant.js";
import { catalogue, languages, suggestions, modernLabels, conversationLabels, getSuggestions } from "../frontend/src/components/assistant/catalogue.js";

test("assistant language catalogues contain equivalent labels and suggested intents", () => {
  for (const language of Object.keys(languages)) {
    assert.deepEqual(Object.keys(catalogue[language]).sort(), Object.keys(catalogue.en).sort());
    assert.deepEqual(suggestions[language].map(([intent]) => intent), suggestions.en.map(([intent]) => intent));
    for (const value of Object.values(catalogue[language])) assert.ok(value.length > 0);
    assert.match(catalogue[language].staticHelp, /static|स्थिर/i);
  }
});

test("compact assistant preserves translated chips, keyboard composition and bounded input", async () => {
  for (const language of Object.keys(languages)) {
    assert.deepEqual(Object.keys(modernLabels[language]).sort(), Object.keys(modernLabels.en).sort());
    for (const [intent] of suggestions[language]) assert.ok(modernLabels[language].chips[intent]);
  }
  const source = await readFile(new URL("../frontend/src/components/assistant/AssistantWidget.jsx", import.meta.url), "utf8");
  for (const token of ['!history.length', 'moreSuggestions ? undefined : 5', '!event.shiftKey', '!event.nativeEvent.isComposing', 'maxLength={config?.questionLimit || 1200}', 'config?.historyLimit', 'claim.title', 'pr-assistant-composer']) assert.ok(source.includes(token), token);
  assert.doesNotMatch(source, /result\.(?:failure|provider|model)|dangerouslySetInnerHTML/);
});

test("suggestions reflect the authorized role and organization context", () => {
  for (const language of Object.keys(languages)) {
    assert.deepEqual(Object.keys(conversationLabels[language]).sort(), Object.keys(conversationLabels.en).sort());
    const manager = getSuggestions("PROJECT_MANAGER", language, "PRJ-001");
    const leader = getSuggestions("TEAM_LEADER", language, "PRJ-001");
    const adminProject = getSuggestions("ADMIN", language, "PRJ-001");
    const adminOrganization = getSuggestions("ADMIN", language, "");
    for (const prompts of [manager, leader, adminProject, adminOrganization]) {
      assert.ok(prompts.every(([intent, text, label]) => intent && text && label));
      assert.equal(new Set(prompts.map(([intent]) => intent)).size, prompts.length);
    }
    assert.ok(manager.some(([intent]) => intent === "review_help"));
    assert.ok(leader.some(([intent]) => intent === "submit_help"));
    assert.ok(leader.every(([intent]) => !["review_help", "health"].includes(intent)));
    assert.deepEqual(adminOrganization.map(([intent]) => intent), ["overview", "dialogue"]);
  }
  assert.match(getSuggestions("TEAM_LEADER", "en", "PRJ-001")[0][1], /my team/);
  assert.deepEqual(getSuggestions("WORKFORCE", "en", "PRJ-001"), []);
});

test("conversation feedback corresponds to real request and returned response states", async () => {
  const source = await readFile(new URL("../frontend/src/components/assistant/AssistantWidget.jsx", import.meta.url), "utf8");
  assert.ok(source.indexOf('const turn = { id, question: text, result: null') < source.indexOf('await assistantApi.ask'));
  assert.match(source, /setResponding\(result.mode === "AI"\)/);
  for (const token of ["stickToBottom.current", "onScroll", "retryId", "guidanceVisible", "ui.useGuidance", "navigator.clipboard.writeText", "lastResult?.language"]) assert.ok(source.includes(token), token);
  assert.match(source, /const \{ language \} = useUiPreferences\(\)/);
  assert.match(source, /const body = \{[^\n]*language, conversation:/);
  assert.doesNotMatch(source, /ui\.preference/);
  assert.doesNotMatch(source, /setInterval|fake.*(?:typing|stream)|localStorage|result\.(?:failure|provider|model)/i);
});

test("central client preserves real AbortError cancellation", async () => {
  const original = globalThis.fetch;
  try {
    const cancellation = new DOMException("Cancelled", "AbortError");
    globalThis.fetch = async () => { throw cancellation; };
    await assert.rejects(apiRequest("/api/assistant/ask", { signal: new AbortController().signal }, "/api"), (error) => error === cancellation);
  } finally { globalThis.fetch = original; }
});

test("assistant source client rejects arbitrary URLs and mutation paths", () => {
  for (const path of ["https://evil.invalid", "/api/reviews/update/confirm", "/api/assistant/source?sql=select"]) assert.throws(() => assistantApi.source(path));
});

test("assistant is added only after workforce and department restrictions", async () => {
  const source = await readFile(new URL("../frontend/src/App.jsx", import.meta.url), "utf8");
  assert.ok(source.indexOf('user.role === "WORKFORCE"') < source.indexOf("const assistant ="));
  assert.ok(source.indexOf('user.role === "DEPARTMENT"') < source.indexOf("const assistant ="));
  assert.match(source, /key=\{`\$\{user.id\}:\$\{user.organizationId\}:\$\{user.role\}`\}/);
});

test("robot uses bundled inline SVG with actual states and reduced motion", async () => {
  const robot = await readFile(new URL("../frontend/src/components/assistant/Robot.jsx", import.meta.url), "utf8");
  const style = await readFile(new URL("../frontend/src/styles/assistant.css", import.meta.url), "utf8");
  assert.match(robot, /<svg/); assert.doesNotMatch(robot, /Temp|clipboard|https:|three|canvas/);
  for (const state of ["idle", "listening", "thinking", "responding", "success", "fallback", "error"]) assert.ok(style.includes(state === "idle" ? "pr-pet-breathe" : `is-${state}`));
  assert.match(robot, /linearGradient/);
  assert.match(robot, /useId/);
  assert.match(robot, /pr-pet-eyes/);
  assert.doesNotMatch(robot, /clipboard|Temp|AppData/);
  assert.match(style, /prefers-reduced-motion:reduce/);
  assert.match(style, /100dvh/); assert.match(style, /calc\(100vw/);
});

test("widget exposes context, modes, source validation, keyboard and stale-response guard", async () => {
  const source = await readFile(new URL("../frontend/src/components/assistant/AssistantWidget.jsx", import.meta.url), "utf8");
  for (const token of ["AbortController", "epoch.current !== version", "conversation.current = null", "CONVERSATION_EXPIRED", "GUIDED_FALLBACK", "resolveApiUrl(record.source)", "Escape", "Tab", "setHistory([])"]) assert.ok(source.includes(token), token);
  assert.doesNotMatch(source, /dangerouslySetInnerHTML|localStorage|VITE_.*KEY/);
});
