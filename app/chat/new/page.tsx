"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Textarea } from "@/components/ui/textarea"
import { zodResolver } from "@hookform/resolvers/zod"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { z } from "zod"

const clientParametersSchema = z.object({
  clientName: z.string().min(2, { message: "Client name must be at least 2 characters." }),
  clientType: z.string().min(1, { message: "Please select a client type." }),
  budgetMin: z.number().min(50000, { message: "Minimum budget must be at least $50,000." }),
  budgetMax: z.number().min(50000, { message: "Maximum budget must be at least $50,000." }),
  urgencyLevel: z.number().min(1).max(10),
  personalityTraits: z.array(z.string()).min(1, { message: "Select at least one personality trait." }),
  propertyPreferences: z.string().optional(),
  specialRequirements: z.string().optional(),
})

type ClientParametersFormValues = z.infer<typeof clientParametersSchema>

const defaultValues: Partial<ClientParametersFormValues> = {
  clientName: "",
  clientType: "",
  budgetMin: 300000,
  budgetMax: 500000,
  urgencyLevel: 5,
  personalityTraits: ["analytical"],
  propertyPreferences: "",
  specialRequirements: "",
}

export default function NewChatPage() {
  const router = useRouter()
  const form = useForm<ClientParametersFormValues>({
    resolver: zodResolver(clientParametersSchema),
    defaultValues,
  })

  function onSubmit(data: ClientParametersFormValues) {
    console.log(data)
    // In a real app, we would save this to Supabase and get the session  {
    console.log(data)
    // In a real app, we would save this to Supabase and get the session
    const sessionId = "new-session-" + Date.now()
    router.push(`/chat/${sessionId}`)
  }

  const personalityOptions = [
    { value: "analytical", label: "Analytical" },
    { value: "emotional", label: "Emotional" },
    { value: "skeptical", label: "Skeptical" },
    { value: "decisive", label: "Decisive" },
    { value: "cautious", label: "Cautious" },
  ]

  return (
    <div className="container py-10">
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Create New Practice Session</CardTitle>
            <CardDescription>
              Configure your virtual client's parameters to customize your practice experience
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <FormField
                  control={form.control}
                  name="clientName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Client Name</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. Sarah Johnson" {...field} />
                      </FormControl>
                      <FormDescription>
                        Give your virtual client a name to make the practice more realistic.
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="clientType"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Client Type</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select client type" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="first-time-buyer">First-time Buyer</SelectItem>
                          <SelectItem value="investor">Investor</SelectItem>
                          <SelectItem value="downsizer">Downsizer</SelectItem>
                          <SelectItem value="luxury-buyer">Luxury Buyer</SelectItem>
                          <SelectItem value="family-home">Family Home</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormDescription>The type of client you want to practice with.</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormField
                    control={form.control}
                    name="budgetMin"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Minimum Budget</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            min={50000}
                            step={10000}
                            {...field}
                            onChange={(e) => field.onChange(Number(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="budgetMax"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Maximum Budget</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            min={50000}
                            step={10000}
                            {...field}
                            onChange={(e) => field.onChange(Number(e.target.value))}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="urgencyLevel"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Urgency Level: {field.value}</FormLabel>
                      <FormControl>
                        <Slider
                          min={1}
                          max={10}
                          step={1}
                          defaultValue={[field.value]}
                          onValueChange={(vals) => field.onChange(vals[0])}
                        />
                      </FormControl>
                      <FormDescription>
                        How urgently is the client looking to buy? (1 = Just browsing, 10 = Need to move immediately)
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="personalityTraits"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Personality Traits</FormLabel>
                      <div className="flex flex-wrap gap-2">
                        {personalityOptions.map((option) => (
                          <Button
                            type="button"
                            key={option.value}
                            variant={field.value?.includes(option.value) ? "default" : "outline"}
                            onClick={() => {
                              const currentValues = new Set(field.value || [])
                              if (currentValues.has(option.value)) {
                                currentValues.delete(option.value)
                              } else {
                                currentValues.add(option.value)
                              }
                              field.onChange(Array.from(currentValues))
                            }}
                            className="mr-2 mb-2"
                          >
                            {option.label}
                          </Button>
                        ))}
                      </div>
                      <FormDescription>Select personality traits for your virtual client.</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="propertyPreferences"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Property Preferences</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="e.g. 3 bedrooms, 2 bathrooms, modern kitchen, close to schools"
                          {...field}
                        />
                      </FormControl>
                      <FormDescription>Describe what kind of property the client is looking for.</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="specialRequirements"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Special Requirements</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="e.g. Must have a home office, needs to be wheelchair accessible"
                          {...field}
                        />
                      </FormControl>
                      <FormDescription>Any special requirements or deal-breakers for the client.</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Button type="submit" className="w-full">
                  Start Practice Session
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

