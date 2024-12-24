export default function Login() {
    const handleLogin = async () => {
        const req = await fetch(`${window.API_URL}/auth/login/google`);
        if (req.ok) {
            const data = await req.json();
            window.location.replace(data.url);
        }
        else {
            console.error("Error con el backend", req.status)
        }  
    }

    return (
        <div className="flex justify-center items-center h-screen">
            <button onClick={handleLogin} className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
                Google Auth
            </button>        
        </div>
      );
}