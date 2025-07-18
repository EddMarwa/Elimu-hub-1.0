"use client";
import { useRef, useEffect, useState } from "react";
import { FiSend } from "react-icons/fi";

const AI_AVATAR = "/globe.svg";
const USER_AVATAR = "/file.svg";

const exampleSubjects = ["Mathematics", "English", "Science", "Kiswahili", "History"];
const exampleQuestions = [
  "What is photosynthesis?",
  "Explain Pythagoras' theorem.",
  "Summarize the Mau Mau uprising.",
  "How do you solve quadratic equations?",
  "What is the importance of education?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: "Hello! I am Elimu Hub AI. How can I assist you with the Kenyan curriculum today?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Scroll to bottom on new message
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages((msgs) => [
      ...msgs,
      { sender: "user", text: input },
    ]);
    setInput("");
    setLoading(true);
    // Simulate AI response
    setTimeout(() => {
      setMessages((msgs) => [
        ...msgs,
        {
          sender: "ai",
          text: "This is a sample AI response. (In production, this will be curriculum-aligned and context-aware.)",
        },
      ]);
      setLoading(false);
    }, 1200);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleSend();
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-green-200 via-yellow-100 to-green-300">
      {/* Header */}
      <header className="w-full py-6 px-4 flex items-center justify-between bg-white/80 shadow-md z-10">
        <div className="flex items-center gap-3">
          <span className="text-3xl font-extrabold text-green-700">Elimu </span>
          <span className="text-3xl font-extrabold bg-gradient-to-r from-yellow-400 via-green-500 to-green-700 bg-clip-text text-transparent">Hub</span>
          <span className="text-3xl font-extrabold text-yellow-500"> AI</span>
        </div>
        <span className="text-sm text-gray-500 font-mono">Elimu Hub</span>
      </header>
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar (optional) */}
        <aside className="hidden md:flex flex-col w-64 bg-white/60 border-r border-green-100 p-6 gap-8">
          <div>
            <h3 className="font-bold text-green-700 mb-2">Subjects</h3>
            <ul className="space-y-1">
              {exampleSubjects.map((subj) => (
                <li key={subj} className="text-gray-700 hover:text-green-700 cursor-pointer transition-colors">{subj}</li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="font-bold text-green-700 mb-2">Example Questions</h3>
            <ul className="space-y-1">
              {exampleQuestions.map((q, i) => (
                <li key={i} className="text-gray-600 hover:text-green-700 cursor-pointer transition-colors text-sm">{q}</li>
              ))}
            </ul>
          </div>
        </aside>
        {/* Chat Area */}
        <main className="flex-1 flex flex-col justify-end">
          <div ref={chatRef} className="flex-1 overflow-y-auto px-2 sm:px-8 py-6 space-y-4 bg-transparent">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`flex items-end gap-2 max-w-[80%] ${msg.sender === "user" ? "flex-row-reverse" : ""}`}>
                  <img
                    src={msg.sender === "user" ? USER_AVATAR : AI_AVATAR}
                    alt={msg.sender === "user" ? "User" : "AI"}
                    className="w-8 h-8 rounded-full bg-white border border-gray-200 shadow-sm"
                  />
                  <div className={`rounded-2xl px-4 py-2 text-base shadow-md ${msg.sender === "user" ? "bg-green-600 text-white" : "bg-white text-gray-800 border border-green-100"}`}>
                    {msg.text}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="flex items-end gap-2 max-w-[80%]">
                  <img
                    src={AI_AVATAR}
                    alt="AI"
                    className="w-8 h-8 rounded-full bg-white border border-gray-200 shadow-sm"
                  />
                  <div className="rounded-2xl px-4 py-2 text-base shadow-md bg-white text-gray-800 border border-green-100 flex items-center gap-2">
                    <span className="animate-pulse">Thinking...</span>
                    <span className="w-2 h-2 bg-green-400 rounded-full animate-bounce"></span>
                  </div>
                </div>
              </div>
            )}
          </div>
          {/* Input Area */}
          <div className="w-full bg-white/80 px-4 py-4 flex items-center gap-2 border-t border-green-100">
            <input
              type="text"
              className="flex-1 rounded-full border border-green-200 px-4 py-2 text-lg focus:outline-none focus:ring-2 focus:ring-green-400 bg-white shadow-sm placeholder:text-gray-600 text-gray-900"
              placeholder="Type your question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button
              onClick={handleSend}
              className="rounded-full bg-green-700 hover:bg-yellow-500 transition-colors text-white p-3 shadow-lg disabled:opacity-50"
              disabled={loading || !input.trim()}
              aria-label="Send"
            >
              <FiSend size={22} />
            </button>
          </div>
        </main>
      </div>
    </div>
  );
} 