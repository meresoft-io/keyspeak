import { cn } from "@/lib/utils"
import { describe, it, expect } from "vitest"

describe("cn utility function", () => {
  it("merges class names correctly", () => {
    const result = cn("class1", "class2")
    expect(result).toBe("class1 class2")
  })

  it("handles conditional class names", () => {
    const condition = true
    const result = cn("base", condition ? "active" : "inactive")
    expect(result).toBe("base active")
  })

  it("handles undefined and null values", () => {
    const result = cn("base", undefined, null, "valid")
    expect(result).toBe("base valid")
  })

  it("merges tailwind classes correctly", () => {
    const result = cn("p-4 bg-red-500", "p-6 text-white")
    expect(result).toBe("p-6 bg-red-500 text-white")
  })
})

