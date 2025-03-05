import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { formatDistanceToNow } from "date-fns"
import Link from "next/link"

const mockSessions = [
  {
    id: "1",
    clientName: "Sarah Johnson",
    clientType: "First-time Buyer",
    budget: "$450,000 - $500,000",
    date: new Date(2025, 2, 3),
    duration: "15 minutes",
    messageCount: 24,
  },
  {
    id: "2",
    clientName: "Michael Chen",
    clientType: "Investor",
    budget: "$600,000 - $800,000",
    date: new Date(2025, 2, 2),
    duration: "22 minutes",
    messageCount: 31,
  },
  {
    id: "3",
    clientName: "Emma Rodriguez",
    clientType: "Downsizer",
    budget: "$350,000 - $400,000",
    date: new Date(2025, 2, 1),
    duration: "18 minutes",
    messageCount: 27,
  },
  {
    id: "4",
    clientName: "David Wilson",
    clientType: "Luxury Buyer",
    budget: "$1,200,000+",
    date: new Date(2025, 1, 28),
    duration: "25 minutes",
    messageCount: 33,
  },
  {
    id: "5",
    clientName: "Olivia Taylor",
    clientType: "Family Home",
    budget: "$550,000 - $650,000",
    date: new Date(2025, 1, 25),
    duration: "20 minutes",
    messageCount: 29,
  },
]

export function PracticeHistory() {
  return (
    <div className="space-y-4">
      {mockSessions.map((session) => (
        <div key={session.id} className="flex items-center justify-between p-4 border rounded-lg">
          <div className="flex items-center gap-4">
            <Avatar>
              <AvatarFallback>
                {session.clientName
                  .split(" ")
                  .map((n) => n[0])
                  .join("")}
              </AvatarFallback>
            </Avatar>
            <div>
              <div className="font-medium">{session.clientName}</div>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="outline">{session.clientType}</Badge>
                <span className="text-xs text-muted-foreground">
                  {formatDistanceToNow(session.date, { addSuffix: true })}
                </span>
              </div>
              <div className="text-sm text-muted-foreground mt-1">
                Budget: {session.budget} • {session.duration} • {session.messageCount} messages
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <Link href={`/chat/${session.id}`}>
              <Button variant="outline" size="sm">
                View
              </Button>
            </Link>
            <Link href={`/chat/new?clone=${session.id}`}>
              <Button size="sm">Retry</Button>
            </Link>
          </div>
        </div>
      ))}
    </div>
  )
}

