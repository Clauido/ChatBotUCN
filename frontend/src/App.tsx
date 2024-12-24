import ChatBot from "@/components/chat-bot";
import Login from "@/components/login";
import { useEffect, useState } from "react";
import Spinner from "@/components/ui/spinner";

const checkToken = async () => {
  try {
    const token = window.localStorage.getItem("auth");
    if (token) {
      const req = await fetch(`${window.API_URL}/auth/validate`, {
        method: "GET",
        headers: {
          "Authorization": token
        }
      });
      if (req.ok) {
        const data = await req.json();
        const storage = window.localStorage;
        storage.setItem("auth", data.token)
        return true;
      }
    }
  } catch {
    window.localStorage.clear()
    return false
  }
}

const handleGoogleCallback = async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get("code");
  
  if (code) {
    const req = await fetch(`${window.API_URL}/auth/callback/google?code=${code}`);
    if (req.ok) {
        const data = await req.json();
        const storage = window.localStorage;
        storage.setItem("auth", data.token)
        storage.setItem("user_info", JSON.stringify(data.user_info))
    }
    window.location.replace("/");
  }
}

export default function App() {
  const [ isLogged, setIsLogged ] = useState<boolean | null>(null);

  useEffect(() => {
    const checkLogin = async () => {
      await handleGoogleCallback()

      if (await checkToken()) {
        return setIsLogged(true);
      }
      return setIsLogged(false);
    }
    if (isLogged === null) {
      checkLogin();
    }
  },[])

  return (
    <main className="h-dvh bg-zinc-800">
      {isLogged === null && (
        <Spinner/>
      )}
      {isLogged === false && (
        <Login/>
      )}
      {isLogged === true && (
        <ChatBot/>
      )}
    </main>
  );
}
