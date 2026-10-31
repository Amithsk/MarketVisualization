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
