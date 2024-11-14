"use client";

import { useState, useEffect } from "react";
import { ThumbsUp, ThumbsDown, Send } from "lucide-react";

type Message = {
  id: string;
  content: string;
  role: "user" | "assistant";
};

const Avatar = ({ src, fallback }: { src: string; fallback: string }) => (
  <div className="w-9 h-9 rounded-full bg-gray-300 flex items-center justify-center">
    {src ? (
      <img src={src} alt="avatar" className="w-full h-full rounded-full" />
    ) : (
      fallback
    )}
  </div>
);

const Button = ({
  children,
  className,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement>) => (
  <button
    {...props}
    className={`p-2 mr-3 rounded-full text-white ${className}`}
  >
    {children}
  </button>
);

const Input = ({ ...props }: React.InputHTMLAttributes<HTMLInputElement>) => (
  <input
    {...props}
    className="p-3 pl-6 rounded-full flex-1 bg-inherit text-white overflow-hidden text-ellipsis focus:outline-none"
  />
);

export default function ChatBot() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [feedback, setFeedback] = useState<{
    [key: string]: "up" | "down" | null;
  }>({});

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      const newMessage: Message = {
        id: Date.now().toString(),
        content: input,
        role: "user",
      };
      setMessages((prev) => [...prev, newMessage]);
      setInput("");
      setIsLoading(true);
      simulateResponse(input);
    }
  };

  const simulateResponse = (userInput: string) => {
    setTimeout(() => {
      const responses = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
      ];
      const randomResponse =
        responses[Math.floor(Math.random() * responses.length)];
      const newMessage: Message = {
        id: Date.now().toString(),
        content: randomResponse,
        role: "assistant",
      };
      setMessages((prev) => [...prev, newMessage]);
      setIsLoading(false);
    }, 6000);
  };

  const handleFeedback = (messageId: string, type: "up" | "down") => {
    setFeedback((prev) => ({
      ...prev,
      [messageId]: prev[messageId] === type ? null : type,
    }));
  };

  useEffect(() => {
    const chatContainer = document.getElementById("chat-container");
    if (chatContainer) {
      chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages]);

  return (
    <div className="flex flex-col h-screen py-12 max-w-3xl mx-auto p-4">
      <div
        id="chat-container"
        className="flex-1 overflow-y-auto space-y-4 pb-4 hide-scrollbar"
      >
        <div className="flex">
          <div className="flex items-start mr-2">
            <Avatar src="/image.png" fallback="AI" />
          </div>
          <div
            className={`rounded-3xl py-2 px-5 max-h-10
                text-white
            `}
          >
            <p>¡Hola! ¿En qué puedo ayudarte hoy?</p>
          </div>
        </div>
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === "user" ? "justify-end" : ""}`}
          >
            {message.role !== "user" && (
              <div className="flex items-start mr-2 pt-3">
                <Avatar src="/image.png" fallback="AI" />
              </div>
            )}
            <div
              className={`rounded-3xl py-2 px-5 ${
                message.role === "user"
                  ? "bg-zinc-700 text-white max-w-[75%]"
                  : "text-white"
              }`}
            >
              <p>{message.content}</p>
              {message.role === "assistant" && (
                <div className="flex justify-start mt-2">
                  <Button onClick={() => handleFeedback(message.id, "up")}>
                    <ThumbsUp
                      size={18}
                      className={`${
                        feedback[message.id] === "up" ? "fill-white" : ""
                      }`}
                    />
                  </Button>
                  <Button onClick={() => handleFeedback(message.id, "down")}>
                    <ThumbsDown
                      size={18}
                      className={`${
                        feedback[message.id] === "down" ? "fill-white" : ""
                      }`}
                    />
                  </Button>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-end mr-2">
              <Avatar src="/image.png" fallback="AI" />
            </div>
            <div className="bg-zinc-800 rounded-full p-4">
              <ThinkingAnimation />
            </div>
          </div>
        )}
      </div>
      <form onSubmit={handleSubmit} className="p-1 flex space-x-2 mt-5">
        <div className="flex p-1 items-center w-full rounded-full bg-zinc-700">
          <Input
            value={input}
            onChange={handleInputChange}
            placeholder="Escribe un mensaje..."
            aria-label="Type a message"
          />
          <Button
            type="submit"
            aria-label="Send message"
            className={`p-2 text-white rounded-full transition-colors ${
              input.trim() ? "bg-white" : "bg-zinc-500"
            }`}
          >
            <Send size={18} className="stroke-zinc-700" />
          </Button>
        </div>
      </form>
    </div>
  );
}

function ThinkingAnimation() {
  return (
    <div className="animate-pulse flex space-x-1">
      <div className="w-2 h-2 bg-gray-100 rounded-full animate-bounce"></div>
      <div className="w-2 h-2 bg-gray-100 rounded-full animate-bounce delay-75"></div>
      <div className="w-2 h-2 bg-gray-100 rounded-full animate-bounce delay-150"></div>
    </div>
  );
}
