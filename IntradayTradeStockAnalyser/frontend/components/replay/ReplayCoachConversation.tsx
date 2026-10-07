"use client";
import { useEffect, useMemo, useState } from "react";
import { formatCoachTimestampList, formatCoachTimestampText } from "../../lib/replayCoachTime";
import { askReplayCoachQuestion, getReplayCoachMessages } from "../../services/replayApi";
import type { ReplayCoachMessage } from "../../types/replay";
import ReplayCoachFeedback from "./ReplayCoachFeedback";

const starters = ["Why was my entry timing weak?", "How was the suggested plan better than my executed trade?", "Which candle confirmed the suggested plan?", "Explain the reward-to-risk calculation.", "What is the main lesson for my next trade?"];

export default function ReplayCoachConversation({ analysisId, onEvidenceTime }: { analysisId: number; onEvidenceTime: (time: string) => void }) {
    const [messages, setMessages] = useState<ReplayCoachMessage[]>([]);
    const [question, setQuestion] = useState("");
    const [loading, setLoading] = useState(true);
    const [sending, setSending] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const load = async () => { setLoading(true); try { setMessages((await getReplayCoachMessages(analysisId)).messages); setError(null); } catch { setError("Conversation could not be loaded."); } finally { setLoading(false); } };
    useEffect(() => { void load(); }, [analysisId]);
    const visible = useMemo(() => {
        const completedIds = new Set(messages.filter(m => m.role === "ASSISTANT" && m.status === "COMPLETED").map(m => m.reply_to_message_id));
        const latestFailed = [...messages].reverse().find(m => m.role === "USER" && m.status === "FAILED");
        return messages.filter(m => (m.role === "ASSISTANT" && m.status === "COMPLETED") || (m.role === "USER" && m.status === "COMPLETED" && completedIds.has(m.id)) || (m.role === "USER" && m.status === "PROCESSING") || m.id === latestFailed?.id);
    }, [messages]);
    const send = async () => { if (!question.trim() || sending) return; const text = question; setSending(true); setError(null); try { await askReplayCoachQuestion(analysisId, { question: text, client_request_id: crypto.randomUUID() }); setQuestion(""); await load(); } catch { await load(); setError("Coach answer could not be generated. You can retry the saved question."); } finally { setSending(false); } };
    const updateFeedback = (id: number, value: ReplayCoachMessage["feedback"]) => setMessages(all => all.map(m => m.id === id ? { ...m, feedback: value } : m));
    return <section className="rounded border border-indigo-700 bg-gray-950 p-4"><h3 className="font-semibold">Ask the Coach</h3><p className="mt-1 text-xs text-gray-400">All times are IST.</p>{loading ? <p className="text-sm">Loading conversation…</p> : <><div className="mt-3 space-y-3">{visible.map(message => { const evidenceLabels = formatCoachTimestampList(message.evidence_times); return <article key={message.id} className={message.role === "USER" ? "rounded bg-slate-800 p-3" : "rounded bg-gray-900 p-3"}><b>{message.role === "USER" ? "You" : "Coach"}</b><p className="mt-1 whitespace-pre-wrap text-sm">{message.role === "ASSISTANT" ? formatCoachTimestampText(message.content) : message.content}</p>{message.status === "PROCESSING" && <p className="text-xs text-gray-400">Thinking…</p>}{message.status === "FAILED" && <p className="text-xs text-red-300">Question failed. <button className="text-indigo-300" onClick={() => setQuestion(message.content)}>Retry</button></p>}{message.role === "ASSISTANT" && message.evidence_times.length > 0 && <div className="mt-2 text-xs">Supporting chart evidence: <span className="inline-flex flex-wrap gap-x-2 gap-y-1">{message.evidence_times.map((value, index) => <button key={value} className="text-indigo-300" onClick={() => onEvidenceTime(value)}>{evidenceLabels[index]}</button>)}</span></div>}{message.role === "ASSISTANT" && <ReplayCoachFeedback assistantMessageId={message.id} feedback={message.feedback} onSaved={value => updateFeedback(message.id, value)} />}</article>; })}</div><textarea className="mt-3 w-full rounded bg-gray-900 p-2" value={question} onChange={e => setQuestion(e.target.value)} maxLength={2000} placeholder="Ask about this Coach analysis…" /><button className="mt-2 text-indigo-300 disabled:text-gray-600" disabled={sending || !question.trim()} onClick={send}>{sending ? "Sending…" : "Send"}</button>{error && <p className="mt-2 text-sm text-red-300">{error}</p>}</>}</section>;
}
