import { PaperAirplaneIcon } from "@heroicons/react/24/outline";
import { ThemeProvider } from "./components/theme-provider";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";

import { useState } from "react";

function App() {
  const [inputValue, setInputValue] = useState("");

  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <div className="fixed bottom-4">
        <div className="px-4 flex gap-3">
          <Input
            type="text"
            placeholder="Envía un mensaje a ChatGPT"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
          />
          <Button disabled={!inputValue}>
            <PaperAirplaneIcon />
          </Button>
        </div>
        <div className="flex px-4 pt-3 justify-center text-center">
          <small className="text-gray-500">
            ChatGPT puede cometer errores. Comprueba la información importante.
          </small>
        </div>
      </div>
    </ThemeProvider>
  );
}

export default App;
