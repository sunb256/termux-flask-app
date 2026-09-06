import { useState } from "react"

import { Button } from "@/components/ui/button"


function App() {
  const [message, setMessage] = useState("未接続")

  const checkApi = async () => {
    const response = await fetch("/api/health")

    if (!response.ok) {
      setMessage(`HTTP Error: ${response.status}`)
      return
    }

    const data = await response.json()

    setMessage(data.message)
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-3xl font-bold">
        Termux App
      </h1>

      <Button onClick={checkApi}>
        Flask API 接続確認
      </Button>

      <div>
        {message}
      </div>
    </div>
  )
}

export default App