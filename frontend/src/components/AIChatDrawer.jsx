import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Bot, Send, Sparkles, X, PhoneCall, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';
import { SourceBadge } from './SourceBadge';

export const AIChatDrawer = ({ isOpen, onClose, contextSubServiceId, contextSubServiceName }) => {
  const [messages, setMessages] = useState([]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => `session-${Math.random().toString(36).substring(7)}`);

  useEffect(() => {
    if (contextSubServiceName) {
      setMessages([
        {
          sender: 'bot',
          text: `Hello! I can help you with **${contextSubServiceName}**. What would you like to know?`,
          source_status: null,
          intent: 'GREETING'
        }
      ]);
    } else {
      setMessages([
        {
          sender: 'bot',
          text: "Hello! I'm your GSP Grounded AI Assistant. I can help you with verified government schemes, scholarships, certificates, eligibility, and citizen applications.\n\nWhat can I help you with today?",
          source_status: null,
          intent: 'GREETING'
        }
      ]);
    }
  }, [contextSubServiceName, isOpen]);

  if (!isOpen) return null;

  const handleSendMessage = async (textToSend) => {
    const userText = textToSend || inputQuery;
    if (!userText.trim()) return;

    // Append user message
    const newMsgs = [...messages, { sender: 'user', text: userText }];
    setMessages(newMsgs);
    setInputQuery('');

    try {
      setLoading(true);
      const res = await apiService.chatAI(sessionId, userText, 'AP', 'AP-NTR', 'Vijayawada Urban');
      const aiData = res.data;

      setMessages([
        ...newMsgs,
        {
          sender: 'bot',
          text: aiData.explanation,
          intent: aiData.intent,
          mode: aiData.mode,
          source_status: aiData.mode === 'GOVERNMENT_GROUNDED' && aiData.source_status === 'VERIFIED' ? 'VERIFIED' : null,
          service: aiData.mode === 'GOVERNMENT_GROUNDED' ? aiData.resolved_sub_service : null,
          questions: aiData.questions,
          warnings: aiData.warnings
        }
      ]);
    } catch (err) {
      console.error('AI chat error:', err);
      setMessages([
        ...newMsgs,
        {
          sender: 'bot',
          text: "I'm having trouble retrieving verified records right now. Please check back shortly or request a staff callback.",
          source_status: null
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const contextQuestions = contextSubServiceName
    ? [
        `What documents do I need for ${contextSubServiceName}?`,
        `How much is the official fee?`,
        `Do I need to visit an office physically?`,
        `Can someone help me fill the form?`
      ]
    : [
        'Father name wrong in birth certificate',
        'Income certificate for college',
        'I lost my voter card',
        'Renew my driving licence'
      ];

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[450px] bg-slate-950 border-l border-slate-800 shadow-2xl flex flex-col justify-between">
      {/* Drawer Header */}
      <div className="p-4 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-saffron-500/20 text-saffron-400 flex items-center justify-center font-bold">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white font-heading">GSP Grounded Assistant</h3>
            <span className="text-[10px] text-emerald-400 font-semibold block">
              {contextSubServiceName ? `Context: ${contextSubServiceName}` : 'Grounded RAG (No Hallucinations)'}
            </span>
          </div>
        </div>

        <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-800 text-slate-400">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4 text-xs">
        {messages.map((m, idx) => (
          <div key={idx} className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}>
            <div
              className={`p-3.5 rounded-2xl max-w-[85%] leading-relaxed space-y-2 ${
                m.sender === 'user'
                  ? 'bg-saffron-500 text-white rounded-br-none font-medium'
                  : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none'
              }`}
            >
              <p className="whitespace-pre-line">{m.text}</p>

              {m.sender === 'bot' && m.source_status && (
                <div className="pt-1">
                  <SourceBadge status={m.source_status} />
                </div>
              )}

              {/* Service Details Card inside chat (Only for government-grounded service answers) */}
              {m.service && (
                <div className="p-3 rounded-xl bg-slate-950 border border-emerald-500/30 text-[11px] space-y-1">
                  <span className="font-bold text-emerald-400 block">{m.service.sub_service_name}</span>
                  <p className="text-slate-400">Statutory Fee: ₹{m.service.official_fee} • {m.service.processing_time}</p>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-xs text-saffron-400 p-2 bg-slate-900 rounded-xl w-fit">
            <RefreshCw className="w-4 h-4 animate-spin" />
            <span>Thinking...</span>
          </div>
        )}
      </div>

      {/* Context Suggested Prompts */}
      <div className="px-4 py-2 bg-slate-900/50 border-t border-slate-900 flex flex-wrap gap-1.5 text-[10px]">
        {contextQuestions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSendMessage(q)}
            className="px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-slate-300 hover:border-saffron-500/50 hover:text-white transition-colors"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSendMessage();
        }}
        className="p-3 bg-slate-900 border-t border-slate-800 flex items-center gap-2"
      >
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder={contextSubServiceName ? `Ask about ${contextSubServiceName}...` : 'Ask GSP assistant anything...'}
          className="w-full bg-slate-950 text-slate-100 placeholder-slate-500 border border-slate-800 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-saffron-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="p-2 rounded-xl bg-saffron-500 hover:bg-saffron-600 text-white shadow"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
