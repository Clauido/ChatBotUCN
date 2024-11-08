import { PromptInput } from "./components/prompt-input";
import { ThemeProvider } from "./components/theme-provider";
import { useState } from "react";

function App() {
  const [message, setMessage] = useState("");
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (submittedMessage: string) => {
    setMessage(submittedMessage);
    setIsSubmitted(true);
  };

  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <div className="flex min-h-screen flex-col items-center justify-center text-center">
        {!isSubmitted ? (
          <h1 className="mb-36 px-4 text-3xl font-semibold">
            ¿Con qué puedo ayudarte?
          </h1>
        ) : (
          <div className="mb-36 px-4 text-xl">{message}</div>
        )}
        <div className="fixed bottom-4">
          <PromptInput onSubmit={handleSubmit} />
        </div>
      </div>
    </ThemeProvider>
  );
}

export default App;
