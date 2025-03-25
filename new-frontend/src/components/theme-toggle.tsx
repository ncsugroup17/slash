import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"

export function ThemeToggle() {
  const [isDarkMode, setIsDarkMode] = useState(false)

  useEffect(() => {
    // Check if user has a preference saved in local storage
    const userPreference = localStorage.getItem("theme")
    const isDark = userPreference === "dark" || 
      (!userPreference && window.matchMedia("(prefers-color-scheme: dark)").matches)
    
    setIsDarkMode(isDark)
    document.documentElement.classList.toggle("dark", isDark)
  }, [])

  const toggleTheme = () => {
    const newTheme = !isDarkMode ? "dark" : "light"
    setIsDarkMode(!isDarkMode)
    document.documentElement.classList.toggle("dark")
    localStorage.setItem("theme", newTheme)
  }

  return (
    <Button
      onClick={toggleTheme}
      className="w-9 h-9 p-0"
    >
      {isDarkMode ? (
        <span className="text-lg">☀️</span>
      ) : (
        <span className="text-lg">🌙</span>
      )}
    </Button>
  )
} 