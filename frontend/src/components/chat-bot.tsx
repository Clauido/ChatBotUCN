"use client";

import { useState, useEffect } from "react";
import { ThumbsUp, ThumbsDown, Send } from "lucide-react";
import axios from "axios";
import { marked } from 'marked';

marked.setOptions({
  breaks: true,
  gfm: true,
});

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

const MessageContent = ({ content, role }: { content: string; role: "user" | "assistant" }) => {
  if (role === "assistant") {
    const htmlContent = marked.parse(content);
    return (
      <div 
        className="prose prose-invert max-w-none"
        dangerouslySetInnerHTML={{ __html: htmlContent }}
      />
    );
  }
  return <p className="whitespace-pre-wrap">{content}</p>;
};

export default function ChatBot() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [feedback, setFeedback] = useState<{
    [key: string]: "up" | "down" | null;
  }>({});
  const [showWelcome, setShowWelcome] = useState(true);
  const welcomeText = "¿En qué puedo ayudarte?";
  const [displayText, setDisplayText] = useState("");

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      setShowWelcome(false);
      const newMessage: Message = {
        id: Date.now().toString(),
        content: input,
        role: "user",
      };
      setMessages((prev) => [...prev, newMessage]);
      setInput("");
      setIsLoading(true);

      try {
        let accumulatedContent = "";
        let processedLines = new Set<string>();
        let isFirstChunk = true;

        const response = await axios.post(
          `${window.API_URL}/chat`,
          {
            query: input, 
            history: []
          },
          {
            responseType: 'text',
            headers: {
              "Content-Type": "application/json",
            },
            onDownloadProgress: (progressEvent) => {
              const responseText = progressEvent.event.target.responseText;
              const lines = responseText.split('\n').filter(Boolean);
              
              try {
                lines.forEach((line: string) => {
                  if (!processedLines.has(line)) {
                    processedLines.add(line);
                    const parsedLine = JSON.parse(line);
                    if (parsedLine.response.message.content) {
                      if (isFirstChunk) {
                        const assistantMessage: Message = {
                          id: Date.now().toString(),
                          content: parsedLine.response.message.content,
                          role: "assistant",
                        };
                        setMessages(prev => [...prev, assistantMessage]);
                        setIsLoading(false);
                        isFirstChunk = false;
                        accumulatedContent = parsedLine.response.message.content;
                      } else {
                        accumulatedContent += parsedLine.response.message.content;
                        setMessages((prev) => {
                          const updatedMessages = [...prev];
                          const lastMessage = updatedMessages[updatedMessages.length - 1];
                          if (lastMessage.role === "assistant") {
                            lastMessage.content = accumulatedContent;
                          }
                          return updatedMessages;
                        });
                      }
                    }
                  }
                });
              } catch (error) {
                // Ignore parse errors for incomplete chunks
              }
            },
          }
        );

        if (response.status !== 200) {
          console.error("Failed to fetch response");
        }
      } catch (error) {
        console.error("Error during API call:", error);
        setIsLoading(false);
      }
    }
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

  useEffect(() => {
    if (!showWelcome) return;

    let i = 0;
    const typingInterval = setInterval(() => {
      if (i < welcomeText.length) {
        setDisplayText(welcomeText.slice(0, i + 1));
        i++;
      } else {
        clearInterval(typingInterval);
      }
    }, 40);

    return () => clearInterval(typingInterval);
  }, [showWelcome]);
  
  return (
    <div className="flex flex-col h-screen py-12 max-w-3xl mx-auto p-4">
      {showWelcome ? (
        <div className="flex-1 flex flex-col items-center justify-center space-y-8">
          <h1 className="text-4xl font-bold text-white text-center">
            {displayText}
          </h1>
          <form onSubmit={handleSubmit} className="w-full max-w-2xl">
            <div className="flex p-1 items-center w-full rounded-full bg-zinc-700">
              <Input
                value={input}
                onChange={handleInputChange}
                placeholder="Escribe un mensaje..."
                aria-label="Type a message"
                disabled={isLoading}
              />
              <Button
                type="submit"
                aria-label="Send message"
                disabled={isLoading}
                className={`p-2 text-white rounded-full transition-colors ${
                  input.trim() ? "bg-white" : "bg-zinc-500"
                }`}
              >
                <Send size={18} className="stroke-zinc-700" />
              </Button>
            </div>
          </form>
        </div>
      ) : (
        <>
          <div
            id="chat-container"
            className="flex-1 overflow-y-auto space-y-4 pb-4 hide-scrollbar"
          > 
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
                      : "bg-zinc-800 text-white max-w-[75%]"
                  }`}
                >
                  <MessageContent content={message.content} role={message.role} />
                  {message.role === "assistant" && (
                    <div className="flex justify-start mt-2">
                      <Button onClick={() => handleFeedback(message.id, "up")}>
                        <ThumbsUp
                          size={18}
                          className={`${feedback[message.id] === "up" ? "fill-white" : ""}`}
                        />
                      </Button>
                      <Button onClick={() => handleFeedback(message.id, "down")}>
                        <ThumbsDown
                          size={18}
                          className={`${feedback[message.id] === "down" ? "fill-white" : ""}`}
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
                disabled={isLoading}
              />
              <Button
                type="submit"
                aria-label="Send message"
                disabled={isLoading}
                className={`p-2 text-white rounded-full transition-colors ${
                  input.trim() ? "bg-white" : "bg-zinc-500"
                }`}
              >
                <Send size={18} className="stroke-zinc-700" />
              </Button>
            </div>
          </form>
        </>
      )}
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
