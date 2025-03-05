# KeySpeak

A revolutionary training platform for real estate agents to practice and perfect their sales conversations with AI-generated customers. KeySpeak provides a safe, realistic environment where agents can hone their communication skills, handle objections, and improve their sales techniques through interactive role-play scenarios.

## Features

- 🤖 AI-powered customer personas with realistic personalities and objections
- 🏠 Diverse real estate scenarios and property types
- 📊 Performance tracking and feedback
- 🎯 Practice common sales situations and objections
- 💬 Natural conversation flow with context-aware responses
- 📱 Modern, intuitive interface

## Tech Stack

- **Framework:** Next.js 14
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** Radix UI
- **State Management:** Zustand
- **Form Handling:** React Hook Form with Zod validation
- **Testing:** Vitest with Testing Library
- **Database:** Supabase

## Getting Started

### Prerequisites

- Node.js 18.x or later
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/keyspeak.git
cd keyspeak
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Create a `.env.local` file in the root directory and add your environment variables:
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

4. Start the development server:
```bash
npm run dev
# or
yarn dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser to see the result.

## Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build the production application
- `npm run start` - Start the production server
- `npm run lint` - Run ESLint
- `npm test` - Run tests

## Project Structure

```
keyspeak/
├── app/                 # Next.js app directory
├── components/          # React components
├── lib/                 # Utility functions and shared logic
├── public/             # Static assets
├── styles/             # Global styles
└── types/              # TypeScript type definitions
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Next.js](https://nextjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Radix UI](https://www.radix-ui.com/)
- [Supabase](https://supabase.com/) 