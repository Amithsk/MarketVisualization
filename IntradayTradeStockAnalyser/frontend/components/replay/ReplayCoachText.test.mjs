import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (name) => readFileSync(new URL(`./${name}`, import.meta.url), "utf8");

test("Replay Coach starter and full-session entry label are neutral", () => {
  const conversation = read("ReplayCoachConversation.tsx");
  const panel = read("ReplayCoachPanel.tsx");

  assert.match(conversation, /What does the evidence show about my entry timing\?/);
  assert.doesNotMatch(conversation, /Why was my entry timing weak\?/);
  assert.match(panel, /Entry trigger\/condition\./);
  assert.doesNotMatch(panel, /Completed-candle condition before entry\./);
});

test("Trade Effect keeps the movement classification visible and calculation expandable", () => {
  const review = read("ActiveTradeReview.tsx");
  assert.match(review, /TRADE EFFECT/);
  assert.match(review, /movement_classification/);
  assert.match(review, /\/share/);
  assert.match(review, /View trade effect calculation/);
  assert.match(review, /Position updated/);
  assert.doesNotMatch(review, /target gap|stop buffer/i);
});

test("Active-trade candle cards use the scoped high-contrast palette", () => {
  const review = read("ActiveTradeReview.tsx");
  for (const color of ["#F8FAFC", "#CBD5E1", "#E2E8F0", "#67E8F9", "#86EFAC", "#FCA5A5", "#FDE68A"]) assert.match(review, new RegExp(color));
  assert.match(review, /focus-visible:outline/);
});

test("Replay chart markers use the authoritative execution sequence as a compact pointer", () => {
  const chart = read("../charts/CandlestickChart.tsx");
  const charts = read("../charts/SynchronizedCharts.tsx");
  assert.match(chart, /text: `#\$\{event\.sequence\}`/);
  assert.doesNotMatch(chart, /text: `#\$\{event\.sequence\} \$\{event\.event_type\}/);
  assert.match(charts, /#\{event\.sequence\} \{event\.event_type\}/);
  assert.match(chart, /event\.event_type === "EXIT"/);
  assert.match(chart, /event\.event_type === "ADD"/);
});

test("Coach and active-trade disclosures retain accessible, independent controls", () => {
  const panel = read("ReplayCoachPanel.tsx");
  const review = read("ActiveTradeReview.tsx");
  assert.match(panel, /aria-controls=\{contentId\}/);
  assert.match(panel, /setExpanded\(true\)/);
  assert.match(review, /Expand all/);
  assert.match(review, /Collapse all/);
  assert.match(review, /useState<Set<string>>\(new Set\(\)\)/);
  assert.match(review, /aria-expanded=\{expanded\}/);
  assert.match(review, /Trade effect unavailable/);
});
