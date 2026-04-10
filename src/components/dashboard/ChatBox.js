'use client';
import { GoogleGenerativeAI } from "@google/generative-ai"
import React, { useState, useRef, useEffect } from 'react';
import Avatar from '@mui/material/Avatar'



export default function ChatBox() {
  let userdata = null
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'bot', text: "Hey! Ask me anything about your fitness data." }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const genAI = new GoogleGenerativeAI('AIzaSyBXlAm4f3IcwqFv6JcjesvdXvzC08zSEsI')
  useEffect(() => {
    fetch('/userdata.json')
      .then(res => res.json())
      .then(data => userdata = data)
  }, []) // empty array = runs once on mount
  const model = genAI.getGenerativeModel({
    model: "gemini-2.5-flash",
    systemInstruction: `You are a concise health assistant responding in a chat.
                        Keep all responses under 3 sentences with no bullet points,
                        headers or fluff. The user's data here: ${userdata} is used for context`
  })

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', text }]);
    setLoading(true);
    const result = await model.generateContent(text)
    setMessages((prev) => [...prev, { role: 'bot', text: result.response.text() }]);
    setLoading(false);
  };

  return (
    <div className="absolute bottom-4 right-4 flex flex-col items-end gap-3 z-50">
      {open && (
        <div className="w-[320px] flex flex-col rounded-2xl border border-gray-200 bg-white overflow-hidden shadow-lg">

          <div className="flex items-center justify-between bg-blue-500 px-4 py-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-full bg-white/25 flex items-center justify-center text-white text-xs font-medium">
                <Avatar
                  src="/PulseLink_logo.svg"
                  alt="User Name"
                  sx={{ width: 60, height: 60 }}
                />
              </div>
              <span className="text-white text-sm font-medium">Pulsey</span>
            </div>
            <button onClick={() => setOpen(false)} className="text-white text-lg leading-none bg-transparent border-none cursor-pointer">✕</button>
          </div>
          <div className="h-[260px] overflow-y-auto flex flex-col gap-2 p-3 bg-gray-50">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`max-w-[80%] px-3 py-2 rounded-xl text-[13px] leading-relaxed
                  ${m.role === 'bot'
                    ? 'self-start bg-white border border-gray-200 text-gray-700 rounded-bl-sm'
                    : 'self-end bg-blue-500 text-white rounded-br-sm'
                  }`}
              >
                {m.text}
              </div>
            ))}
            {loading && (
              <div className="self-start bg-white border border-gray-200 text-gray-400 text-[13px] px-3 py-2 rounded-xl rounded-bl-sm">
                Typing...
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="flex items-center gap-2 px-3 py-2 border-t border-gray-200 bg-white">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask Pulsey..."
              className="flex-1 rounded-full bg-gray-50 border border-gray-200 px-4 py-1.5 text-[13px] outline-none focus:border-blue-400"
            />
            <button
              onClick={sendMessage}
              className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0 hover:bg-blue-600 transition-colors"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </div>
        </div>
      )}

      <button
        onClick={() => setOpen((o) => !o)}
        className="w-13 h-13 w-[52px] h-[52px] rounded-full bg-blue-500 hover:bg-blue-600 transition-colors flex items-center justify-center shadow-md"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      </button>
    </div>
  );
}