"use client"

import type React from "react"

import { useEffect, useRef, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Save, Send } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { useClientStore } from "@/lib/store/client-store"
import { useChatStore } from "@/lib/store/chat-store"
import type { ClientParameters } from "@/types"
import { cn } from "@/lib/utils"

export default function ChatPage() {
  const params = useParams()
  const router = useRouter()
  const [input, setInput] = useState("")
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const { client } = useClientStore()
  const { messages, addMessage, isTyping, setIsTyping } = useChatStore()

  // Mock client data - in a real app, this would come from Supabase
  useEffect(() => {
    // This would be a fetch from Supabase in a real app
    const mockClient: ClientParameters = {
      id: params.id as string,
      clientName: "Sarah Johnson",
      clientType: "first-time-buyer",
      budgetMin: 450000,
      budgetMax: 500000,
      urgencyLevel: 7,
      personalityTraits: ["analytical", "cautious"],
      propertyPreferences: "3 bedrooms, 2 bathrooms, modern kitchen, close to schools",
      specialRequirements: "Must have a home office",
    }

    useClientStore.getState().setClient(mockClient)

    // If this is a new chat, add the initial AI message
    if (messages.length === 0) {
      const initialMessage = {
        id: Date.now().toString(),
        role: "assistant",
        content: `Hi there! I'm ${mockClient.clientName}. I'm looking for a ${mockClient.propertyPreferences}. My budget is between $${mockClient.budgetMin.toLocaleString()} and $${mockClient.budgetMax.toLocaleString()}. Can you help me find something suitable?`,
        timestamp: new Date(),
      }
      addMessage(initialMessage)
    }
  }, [params.id, addMessage, messages.length])

  useEffect(() => {
    // Scroll to bottom when messages change
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!input.trim()) return

    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    }

    addMessage(userMessage)
    setInput("")

    // Simulate AI thinking
    setIsTyping(true)

    // Focus the input again
    if (inputRef.current) {
      inputRef.current.focus()
    }

    // In a real app, this would be a call to the AI API
    setTimeout(
      () => {
        // Mock AI response based on client parameters
        let response = ""

        if (input.toLowerCase().includes("price") || input.toLowerCase().includes("budget")) {
          response = `My budget is between $${client?.budgetMin.toLocaleString()} and $${client?.budgetMax.toLocaleString()}. I'm hoping to find something on the lower end of that range, but I can be flexible for the right property.`
        } else if (input.toLowerCase().includes("location") || input.toLowerCase().includes("area")) {
          response =
            "I'm primarily interested in the downtown area, but I'm also open to the western suburbs if there are good schools nearby."
        } else if (input.toLowerCase().includes("timeline") || input.toLowerCase().includes("when")) {
          response =
            client?.urgencyLevel > 7
              ? "I need to move within the next month. My current lease is ending soon."
              : "I'm hoping to move within the next 3-4 months, but I'm not in a huge rush. I want to find the right place."
        } else if (input.toLowerCase().includes("feature") || input.toLowerCase().includes("looking for")) {
          response = `I'm looking for ${client?.propertyPreferences}. ${client?.specialRequirements ? `Also, ${client?.specialRequirements}.` : ""}`
        } else {
          // Generic responses based on personality
          const isAnalytical = client?.personalityTraits.includes("analytical")
          const isSkeptical = client?.personalityTraits.includes("skeptical")

          if (isAnalytical) {
            response =
              "That's interesting. Can you provide more specific details about the properties in that area? I'd like to see some data on price per square foot and recent sales."
          } else if (isSkeptical) {
            response =
              "I'm not entirely convinced. What makes you think this property would be a good fit for my needs? I've heard mixed things about that neighborhood."
          } else {
            response =
              "That sounds promising! I'd love to hear more about the properties you have in mind. When can we schedule a viewing?"
          }
        }

        const aiMessage = {
          id: Date.now().toString(),
          role: "assistant",
          content: response,
          timestamp: new Date(),
        }

        addMessage(aiMessage)
        setIsTyping(false)
      },
      1500 + Math.random() * 1500,
    ) // Random delay between 1.5-3s
  }

  if (!client) {
    return <div className="container py-10">Loading...</div>
  }

  return (
    <div className="container py-6 h-[calc(100vh-4rem)] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <Button variant="ghost" size="icon" onClick={() => router.push("/dashboard")}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex items-center">
          <Avatar className="h-8 w-8 mr-2">
            <AvatarFallback>
              {client.clientName
                .split(" ")
                .map((n) => n[0])
                .join("")}
            </AvatarFallback>
          </Avatar>
          <div>
            <div className="font-medium text-sm">{client.clientName}</div>
            <Badge variant="outline" className="text-xs">
              {client.clientType
                .split("-")
                .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                .join(" ")}
            </Badge>
          </div>
        </div>
        <Button variant="ghost" size="icon">
          <Save className="h-5 w-5" />
        </Button>
      </div>

      <Card className="flex-1 flex flex-col">
        <CardHeader className="py-3">
          <CardTitle className="text-lg">Practice Session</CardTitle>
          <CardDescription>
            Budget: ${client.budgetMin.toLocaleString()} - ${client.budgetMax.toLocaleString()} • Urgency:{" "}
            {client.urgencyLevel}/10
          </CardDescription>
        </CardHeader>
        <Separator />
        <CardContent className="flex-1 p-0 overflow-hidden">
          <ScrollArea className="h-full p-4" ref={scrollAreaRef}>
            <div className="space-y-4">
              {messages.map((message) => (
                <div key={message.id} className={cn("flex", message.role === "user" ? "justify-end" : "justify-start")}>
                  <div
                    className={cn(
                      "max-w-[80%] rounded-lg p-3",
                      message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted",
                    )}
                  >
                    {message.content}
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] rounded-lg p-3 bg-muted">
                    <div className="flex space-x-1">
                      <div className="h-2 w-2 rounded-full bg-current animate-bounce" />
                      <div className="h-2 w-2 rounded-full bg-current animate-bounce [animation-delay:0.2s]" />
                      <div className="h-2 w-2 rounded-full bg-current animate-bounce [animation-delay:0.4s]" />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
        <Separator />
        <CardFooter className="p-3">
          <form onSubmit={handleSendMessage} className="flex w-full gap-2">
            <Input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1"
              disabled={isTyping}
            />
            <Button type="submit" size="icon" disabled={!input.trim() || isTyping}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </CardFooter>
      </Card>
    </div>
  )
}

