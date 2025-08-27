'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { User } from '@supabase/supabase-js'

interface MockAuthContextType {
  user: User | null
  loading: boolean
}

const MockAuthContext = createContext<MockAuthContextType>({
  user: null,
  loading: false,
})

export const useMockAuth = () => useContext(MockAuthContext)

export function MockAuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (process.env.NEXT_PUBLIC_DISABLE_AUTH === 'true') {
      const mockUser: User = {
        id: 'mock-user-id',
        email: 'demo@suna.so',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        aud: 'authenticated',
        role: 'authenticated',
        app_metadata: {},
        user_metadata: {},
      }
      setUser(mockUser)
    }
    setLoading(false)
  }, [])

  return (
    <MockAuthContext.Provider value={{ user, loading }}>
      {children}
    </MockAuthContext.Provider>
  )
}
