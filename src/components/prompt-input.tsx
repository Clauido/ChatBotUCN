import { PaperAirplaneIcon } from "@heroicons/react/24/outline";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useState } from "react";

interface PromptInputProps {
  onSubmit: (message: string) => void;
}

export function PromptInput({ onSubmit }: PromptInputProps) {
  const [inputValue, setInputValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(inputValue);
    setInputValue("");
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="px-4 flex gap-3">
        <Input
          type="text"
          placeholder="Envía un mensaje a ChatGPT"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
        />
        <Button type="submit" disabled={!inputValue}>
          <PaperAirplaneIcon />
        </Button>
      </div>
      <div className="px-4 pt-2 text-center">
        <small className="text-gray-500">
          ChatGPT puede cometer errores. Comprueba la información importante.
        </small>
      </div>
    </form>
  );
}
