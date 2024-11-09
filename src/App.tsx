"use client";

import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ThemeProvider } from "./components/theme-provider";

type Message = {
  id: number;
  content: string;
  sender: "user" | "bot";
};

export default function FullScreenChat() {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, content: "¡Hola! ¿Cómo puedo ayudarte hoy?", sender: "bot" },
  ]);
  const [input, setInput] = useState("");
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (input.trim()) {
      const userMessage: Message = {
        id: messages.length + 1,
        content: input,
        sender: "user",
      };
      setMessages([...messages, userMessage]);

      // Simulate bot response
      setTimeout(() => {
        const botMessage: Message = {
          id: messages.length + 2,
          content: "Soy un simple bot. ¡No tengo respuestas reales aún!",
          sender: "bot",
        };
        setMessages((prevMessages) => [...prevMessages, botMessage]);
      }, 1000);

      setInput("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <ThemeProvider>
      <div className="flex flex-col h-screen bg-background">
        <header className="flex items-center justify-between p-4 border-b">
          <h1 className="text-2xl font-bold">ChatGPT</h1>
        </header>
        <ScrollArea className="flex-grow p-4" ref={scrollAreaRef}>
          <div className="max-w-2xl mx-auto">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.sender === "user" ? "justify-end" : "justify-start"
                } mb-4`}
              >
                <div
                  className={`flex ${
                    message.sender === "user" ? "flex-row-reverse" : "flex-row"
                  } items-start max-w-[80%]`}
                >
                  <Avatar className="w-8 h-8">
                    <AvatarFallback>
                      {message.sender === "user" ? "U" : "AI"}
                    </AvatarFallback>
                    <AvatarImage
                      src={
                        message.sender === "user"
                          ? "../public/user.jpg"
                          : "../public/bot.png"
                      }
                    />
                  </Avatar>
                  <div
                    className={`mx-2 p-3 rounded-lg ${
                      message.sender === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    }`}
                  >
                    {message.content}
                  </div>
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        </ScrollArea>
        <footer className="p-4">
          <div className="flex items-center space-x-2 max-w-2xl mx-auto">
            <Input
              type="text"
              placeholder="Envía un mensaje a ChatGPT"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-grow"
            />
            <Button type="submit" size="icon" onClick={handleSend}>
              <Send className="h-4 w-4" />
              <span className="sr-only">Send</span>
            </Button>
          </div>
        </footer>
      </div>
    </ThemeProvider>
  );
}
