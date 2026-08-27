import { useEffect, useState } from 'react'

export type AdminTheme = 'light' | 'dark' | 'blue'

export function useAdminTheme() {
  const [theme, setTheme] = useState<AdminTheme>(() => (localStorage.getItem('admin-theme') as AdminTheme) || 'light')
  useEffect(() => {
    localStorage.setItem('admin-theme', theme)
    document.documentElement.dataset.adminTheme = theme
  }, [theme])
  return { theme, setTheme }
}