import type { Message } from "@/types"
import { create } from "zustand"
import { persist } from "zustand/middleware"

interface ChatState {
  messages: Message[]
  isTyping: boolean
  addMessage: (message: Message) => void
  setIsTyping: (isTyping: boolean) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      messages: [],
      isTyping: false,
      addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
      setIsTyping: (isTyping) => set({ isTyping }),
      clearMessages: () => set({ messages: [] }),
    }),
    {
      name: "chat-storage",
    },
  ),
)

