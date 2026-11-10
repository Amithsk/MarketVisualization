"use client"
import { useState } from "react"

export default function TradeAddForm({ onSubmit }: { onSubmit: (payload: any) => void }) {
  const [quantity, setQuantity] = useState("")
  const [price, setPrice] = useState("")
  const [time, setTime] = useState("")
  const [note, setNote] = useState("")
  const valid = Number(quantity) > 0 && Number(price) > 0 && !!time && !!note.trim()
  return <div className="mt-4 space-y-2 rounded border border-blue-200 bg-blue-50 p-3 text-sm">
    <h3 className="font-semibold">Add to position</h3>
    <input type="number" min="1" placeholder="Quantity" className="w-full rounded border p-2" value={quantity} onChange={e => setQuantity(e.target.value)} />
    <input type="number" min="0.000001" step="0.01" placeholder="Actual fill price" className="w-full rounded border p-2" value={price} onChange={e => setPrice(e.target.value)} />
    <input type="datetime-local" step="1" className="w-full rounded border p-2" value={time} onChange={e => setTime(e.target.value)} />
    <textarea placeholder="What did you see in the stock and NIFTY?" className="w-full rounded border p-2" value={note} onChange={e => setNote(e.target.value)} />
    <button disabled={!valid} className="w-full rounded bg-blue-700 py-2 text-white disabled:opacity-40" onClick={() => onSubmit({ quantity: Number(quantity), price: Number(price), execution_timestamp: `${time}+05:30`, note, client_request_id: crypto.randomUUID() })}>Record add</button>
  </div>
}
