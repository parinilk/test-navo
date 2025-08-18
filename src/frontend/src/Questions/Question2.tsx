

import { useEffect, useRef, useState } from "react";

interface Message {
  sender: "User" | "LLM";
  text: string;
}

const initialMessages: Message[] = [
  { sender: "User", text: "What is the capital of France?" },
  { sender: "LLM", text: "The capital of France is Paris." }
];

const Question2 = ({ onPin }: { onPin: (text: string) => void }) => {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [selectedText, setSelectedText] = useState("");
  const [showPin, setShowPin] = useState(false);
  const [pinPosition, setPinPosition] = useState({ x: 0, y: 0 });
  const [inputText, setInputText] = useState("");
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [editText, setEditText] = useState("");
  const [showConfirm, setShowConfirm] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // --- scroll to bottom whenever messages change ---
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const handleMouseUp = () => {
      const selection = window.getSelection();
      const text = selection?.toString();
      if (text && text.trim() !== "" && selection) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        setSelectedText(text);
        setShowPin(true);
        setPinPosition({ x: rect.left, y: rect.top });
      } else {
        setShowPin(false);
      }
    };

    document.addEventListener("mouseup", handleMouseUp);
    return () => document.removeEventListener("mouseup", handleMouseUp);
  }, []);

  const handlePinClick = () => {
    onPin(selectedText);
    setShowPin(false);
    setSelectedText("");
    window.getSelection()?.removeAllRanges();
  };

  const handleSend = () => {
    if (inputText.trim() === "") return;
    const userMessage: Message = { sender: "User", text: inputText.trim() };
    const llmResponse: Message = {
      sender: "LLM",
      text: "This is a static LLM response."
    };
    setMessages((prev) => [...prev, userMessage, llmResponse]);
    setInputText("");
  };

  const handleEditClick = (index: number) => {
    setEditIndex(index);
    setEditText(messages[index].text);
  };

  const handleSaveEdit = () => {
    setShowConfirm(true);
  };

  const confirmSave = () => {
    if (editIndex === null) return;
    const updated = [...messages];
    updated[editIndex].text = editText;
    setMessages(updated);
    setEditIndex(null);
    setEditText("");
    setShowConfirm(false);
    console.log("Changes saved, -10 credits deducted.");
  };

  return (
    <div className="relative bg-white p-4 rounded shadow w-[580px] h-[470px] flex flex-col overflow-hidden">
      {/* Header */}
      <h2 className="text-lg font-semibold mb-2">Conversation for Question 2</h2>

      {/* Messages */}
      <div className="space-y-4 flex-1 overflow-y-auto scrollbar-hide pr-2">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-start ${
              msg.sender === "User" ? "justify-end" : "justify-between"
            }`}
          >
            {msg.sender === "LLM" ? (
              <div className="flex flex-col w-full items-start">
                <div className="max-w-[70%] px-4 py-2 rounded-lg bg-gray-100 text-sm text-left">
                  <strong>{msg.sender}:</strong> {msg.text}
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-end max-w-[70%]">
                <div className="px-4 py-2 rounded-lg bg-blue-100 text-sm text-right">
                  <strong>{msg.sender}:</strong> {msg.text}
                </div>
                {/* Edit button below message */}
                <button
                  onClick={() => handleEditClick(idx)}
                  className="text-gray-500 hover:text-gray-700 mt-1"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M12 20h9" />
                    <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                  </svg>
                </button>
              </div>
            )}
          </div>
        ))}
        {/* dummy div to auto-scroll */}
        <div ref={messagesEndRef} />
      </div>

      {/* Floating Pin */}
      {showPin && (
        <button
          onClick={handlePinClick}
          style={{
            position: "absolute",
            top: pinPosition.y + window.scrollY - 40,
            left: pinPosition.x + window.scrollX,
            zIndex: 1000
          }}
          className="bg-white border border-gray-400 px-2 py-1 text-xs rounded shadow hover:bg-gray-100"
        >
          📌 Pin
        </button>
      )}

      {/* Input */}
      <div className="pt-3 border-t mt-3 flex items-center">
        <input
          type="text"
          placeholder="Please add context to your question"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          className="flex-1 bg-transparent outline-none text-sm px-3 py-2"
        />
        <button className="ml-2 p-2" onClick={handleSend}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            fill="none"
            viewBox="0 0 18 18"
          >
            <path
              d="M16.5 9a.51.51 0 0 1-.058.239.57.57 0 0 1-.157.199.65.65 0 0 1-.26.1L2.785 15.714a.61.61 0 0 1-.674-.465.61.61 0 0 1 .163-.506l2.132-5.72a.91.91 0 0 0 0-.602L2.274 2.7a.61.61 0 0 1 .674-.764l13.5 6.375a.6.6 0 0 1 .26.1.57.57 0 0 1 .157.199A.51.51 0 0 1 16.5 9ZM16.5 9H4.5"
              stroke="blue"
              strokeWidth="1.125"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>

      {/* Edit Modal */}
      {editIndex !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow-lg w-1/3">
            <h3 className="font-semibold mb-2">Edit Message</h3>
            <textarea
              className="w-full border border-gray-300 p-2 text-sm mb-4"
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
            />
            <div className="flex gap-2 justify-end">
              <button
                className="text-sm text-white bg-green-800 px-3 py-1 rounded"
                onClick={handleSaveEdit}
              >
                Save
              </button>
              <button
                className="text-sm text-gray-700 border px-3 py-1 rounded"
                onClick={() => setEditIndex(null)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Popup */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-lg w-80 text-center">
            <h2 className="text-lg font-semibold mb-4">Confirm Save</h2>
            <p className="text-gray-600 mb-6">
              To make these changes, you will lose{" "}
              <span className="font-bold text-red-500">10 credits</span>.
            </p>
            <div className="flex justify-around">
              <button
                onClick={() => setShowConfirm(false)}
                className="px-4 py-2 bg-gray-300 rounded-lg hover:bg-gray-400"
              >
                Cancel
              </button>
              <button
                onClick={confirmSave}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Question2;
