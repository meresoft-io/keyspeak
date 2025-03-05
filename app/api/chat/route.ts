import { NextResponse } from "next/server"
import type { ClientParameters } from "@/types"

// This is a mock implementation since we can't directly integrate with Grok
// In a real app, this would use the AI SDK to connect to an LLM API
export async function POST(req: Request) {
  try {
    const { message, clientParams } = await req.json()

    // Validate input
    if (!message || !clientParams) {
      return NextResponse.json({ error: "Message and client parameters are required" }, { status: 400 })
    }

    // Process the client parameters to generate a contextually appropriate response
    const response = generateMockResponse(message, clientParams)

    // Simulate a delay to mimic AI processing time
    await new Promise((resolve) => setTimeout(resolve, 1000))

    return NextResponse.json({ response })
  } catch (error) {
    console.error("Error in chat API:", error)
    return NextResponse.json({ error: "Failed to process chat message" }, { status: 500 })
  }
}

function generateMockResponse(message: string, clientParams: ClientParameters): string {
  const {
    clientName,
    budgetMin,
    budgetMax,
    urgencyLevel,
    personalityTraits,
    propertyPreferences,
    specialRequirements,
  } = clientParams

  // Simple keyword-based response generation
  if (message.toLowerCase().includes("price") || message.toLowerCase().includes("budget")) {
    return `My budget is between $${budgetMin.toLocaleString()} and $${budgetMax.toLocaleString()}. I'm hoping to find something on the lower end of that range, but I can be flexible for the right property.`
  }

  if (message.toLowerCase().includes("location") || message.toLowerCase().includes("area")) {
    return "I'm primarily interested in the downtown area, but I'm also open to the western suburbs if there are good schools nearby."
  }

  if (message.toLowerCase().includes("timeline") || message.toLowerCase().includes("when")) {
    return urgencyLevel > 7
      ? "I need to move within the next month. My current lease is ending soon."
      : "I'm hoping to move within the next 3-4 months, but I'm not in a huge rush. I want to find the right place."
  }

  if (message.toLowerCase().includes("feature") || message.toLowerCase().includes("looking for")) {
    return `I'm looking for ${propertyPreferences}. ${specialRequirements ? `Also, ${specialRequirements}.` : ""}`
  }

  // Generic responses based on personality
  const isAnalytical = personalityTraits.includes("analytical")
  const isSkeptical = personalityTraits.includes("skeptical")

  if (isAnalytical) {
    return "That's interesting. Can you provide more specific details about the properties in that area? I'd like to see some data on price per square foot and recent sales."
  } else if (isSkeptical) {
    return "I'm not entirely convinced. What makes you think this property would be a good fit for my needs? I've heard mixed things about that neighborhood."
  } else {
    return "That sounds promising! I'd love to hear more about the properties you have in mind. When can we schedule a viewing?"
  }
}

