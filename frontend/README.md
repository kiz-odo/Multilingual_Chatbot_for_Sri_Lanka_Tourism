# Sri Lanka Tourism AI Chatbot - Frontend

A modern, accessible, and multilingual Next.js web application for the Sri Lanka Tourism AI Chatbot platform.

## Features

- 🎨 **Modern UI/UX**: Clean, tropical-themed design with soft colors (teal, ocean blue, green, sand)
- 🌍 **Multilingual Support**: English, Sinhala, Tamil, and more
- ♿ **Accessibility**: WCAG compliant with ARIA labels, keyboard navigation, and screen reader support
- 📱 **Responsive Design**: Mobile-first approach, works on all devices
- 💬 **Real-time Chat**: AI-powered chatbot interface
- 🗺️ **Map Integration**: Location services and maps
- 📅 **Itinerary Planning**: AI-generated trip plans
- 🏛️ **Tourism Discovery**: Attractions, hotels, restaurants, events
- 🚨 **Safety Features**: Emergency SOS, contacts, and safety tips
- 🔐 **Authentication**: JWT-based auth with OAuth support

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS v4
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod
- **Icons**: Lucide React
- **Type Safety**: TypeScript

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:

```bash
npm install
```

2. Create a `.env.local` file in the `frontend` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the development server:

```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── auth/              # Authentication pages
│   ├── chat/              # Chat interface
│   ├── explore/           # Tourism discovery
│   ├── planner/           # Itinerary planning
│   ├── safety/            # Safety & emergency
│   ├── dashboard/         # User dashboard
│   └── layout.tsx         # Root layout
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   └── layout/           # Layout components
├── lib/                  # Utilities and helpers
│   ├── api-client.ts    # API client
│   ├── i18n.ts          # Internationalization
│   └── utils.ts         # Utility functions
├── store/                # Zustand stores
│   ├── auth-store.ts    # Authentication state
│   └── language-store.ts # Language state
└── types/                # TypeScript types
```

## API Integration

The frontend integrates with all backend endpoints:

- **Authentication**: `/api/v1/auth/*`
- **Chat**: `/api/v1/chat/*`
- **Attractions**: `/api/v1/attractions/*`
- **Hotels**: `/api/v1/hotels/*`
- **Restaurants**: `/api/v1/restaurants/*`
- **Itinerary**: `/api/v1/itinerary/*`
- **Safety**: `/api/v1/safety/*`
- **Emergency**: `/api/v1/emergency/*`
- And more...

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Design System

### Colors

- **Primary (Teal)**: `#14b8a6`
- **Ocean Blue**: `#3b82f6`
- **Green**: `#22c55e`
- **Sand**: `#78716c`

### Typography

- **Font**: Geist Sans (system fallback)
- **Headings**: Bold, tracking-tight
- **Body**: Regular weight

### Components

All components follow accessibility best practices:
- Proper ARIA labels
- Keyboard navigation
- Focus management
- Screen reader support

## Internationalization

The app supports multiple languages:
- English (en)
- Sinhala (si)
- Tamil (ta)
- German (de)
- French (fr)
- Chinese (zh)
- Japanese (ja)

Language can be switched via the navbar dropdown.

## Accessibility

- WCAG 2.1 AA compliant
- Keyboard navigation
- Screen reader support
- Focus management
- ARIA labels
- Semantic HTML

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow the existing code style
2. Ensure accessibility standards
3. Add proper TypeScript types
4. Test on multiple devices
5. Update documentation

## License

See the main project LICENSE file.
