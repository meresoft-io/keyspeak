"use client"

import { render, screen, fireEvent } from "@testing-library/react"
import NewChatPage from "@/app/chat/new/page"
import { useRouter } from "next/navigation"

// Mock the next/navigation module
jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
}))

describe("Client Parameters Form", () => {
  beforeEach(() => {
    // Setup router mock
    const mockRouter = {
      push: jest.fn(),
    }
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
  })

  it("renders the form with all fields", () => {
    render(<NewChatPage />)

    // Check for form elements
    expect(screen.getByText("Create New Practice Session")).toBeInTheDocument()
    expect(screen.getByLabelText("Client Name")).toBeInTheDocument()
    expect(screen.getByLabelText("Client Type")).toBeInTheDocument()
    expect(screen.getByLabelText("Minimum Budget")).toBeInTheDocument()
    expect(screen.getByLabelText("Maximum Budget")).toBeInTheDocument()
    expect(screen.getByText(/Urgency Level/)).toBeInTheDocument()
    expect(screen.getByText("Personality Traits")).toBeInTheDocument()
    expect(screen.getByLabelText("Property Preferences")).toBeInTheDocument()
    expect(screen.getByLabelText("Special Requirements")).toBeInTheDocument()
    expect(screen.getByText("Start Practice Session")).toBeInTheDocument()
  })

  it("validates required fields", async () => {
    render(<NewChatPage />)

    // Submit the form without filling required fields
    fireEvent.click(screen.getByText("Start Practice Session"))

    // Check for validation errors
    expect(await screen.findByText("Client name must be at least 2 characters.")).toBeInTheDocument()
    expect(await screen.findByText("Please select a client type.")).toBeInTheDocument()
  })

  it("submits the form with valid data", async () => {
    render(<NewChatPage />)

    // Fill out the form
    fireEvent.change(screen.getByLabelText("Client Name"), { target: { value: "John Doe" } })

    // Select client type
    fireEvent.click(screen.getByText("Select client type"))
    fireEvent.click(screen.getByText("First-time Buyer"))

    // Set budgets
    fireEvent.change(screen.getByLabelText("Minimum Budget"), { target: { value: "300000" } })
    fireEvent.change(screen.getByLabelText("Maximum Budget"), { target: { value: "400000" } })

    // Set property preferences
    fireEvent.change(screen.getByLabelText("Property Preferences"), {
      target: { value: "3 bedrooms, 2 bathrooms" },
    })

    // Submit the form
    fireEvent.click(screen.getByText("Start Practice Session"))

    // Check if router.push was called
    const router = useRouter()
    expect(router.push).toHaveBeenCalled()
  })
})

