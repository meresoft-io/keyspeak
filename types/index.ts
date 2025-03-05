export interface ClientParameters {
  id: string
  clientName: string
  clientType: string
  budgetMin: number
  budgetMax: number
  urgencyLevel: number
  personalityTraits: string[]
  propertyPreferences: string
  specialRequirements?: string
}

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

