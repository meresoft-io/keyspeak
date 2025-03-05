import type { ClientParameters } from "@/types"
import { create } from "zustand"

interface ClientState {
  client: ClientParameters | null
  setClient: (client: ClientParameters) => void
}

export const useClientStore = create<ClientState>((set) => ({
  client: null,
  setClient: (client) => set({ client }),
}))

