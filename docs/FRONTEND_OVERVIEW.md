# 🎨 Frontend Overview - Sri Lanka Tourism AI Chatbot

## **Project Summary**

A modern, accessible, and multilingual **Next.js 16** web application for the Sri Lanka Tourism AI Chatbot platform. Built with React 19, TypeScript, and Tailwind CSS v4, featuring a tropical-themed design and production-ready architecture.

---

## **🌟 Key Features**

### **Design & User Experience**
- 🎨 **Modern Tropical UI**: Clean, tropical-themed design with soft colors (teal, ocean blue, green, sand)
- 📱 **Fully Responsive**: Mobile-first approach, works seamlessly on all devices
- ♿ **WCAG 2.1 AA Compliant**: Full accessibility with ARIA labels, keyboard navigation, and screen reader support
- 🌓 **Dark/Light Theme**: Toggleable theme support
- 🎭 **Smooth Animations**: Professional transitions and micro-interactions

### **Multilingual Support**
- 🌍 **7 Languages**: English, Sinhala (සිංහල), Tamil (தமிழ்), German, French, Chinese, Japanese
- 🔄 **Real-time Translation**: Seamless language switching via navbar dropdown
- 🗣️ **Native Language Understanding**: Not just translation - true multilingual experience

### **Core Functionalities**
- 💬 **Real-time Chat**: AI-powered chatbot with WebSocket support
- 🎤 **Voice Input**: Speech-to-text integration (Web Speech API)
- 📸 **Image Upload**: Landmark recognition and image-based queries
- 🗺️ **Map Integration**: Interactive maps with location services
- 📅 **Itinerary Planning**: AI-generated personalized trip plans
- 🏛️ **Tourism Discovery**: Attractions, hotels, restaurants, events
- 🚨 **Emergency SOS**: Quick access to emergency contacts and safety features
- 🔐 **Authentication**: JWT-based auth with OAuth support and MFA/2FA
- 📊 **Analytics Dashboard**: User insights and trip statistics

---

## **🏗️ Tech Stack**

### **Core Technologies**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 16.1.1 | React framework with App Router |
| **React** | 19.2.3 | UI library |
| **TypeScript** | 5.x | Type safety |
| **Tailwind CSS** | 4.x | Utility-first styling |
| **Zustand** | 5.0.9 | State management |
| **TanStack Query** | 5.90.16 | Data fetching & caching |
| **React Hook Form** | 7.69.0 | Form management |
| **Zod** | 4.3.4 | Schema validation |
| **Axios** | 1.13.2 | HTTP client |
| **Socket.io Client** | 4.8.3 | WebSocket communication |
| **Lucide React** | 0.562.0 | Icon library |
| **Recharts** | 3.6.0 | Data visualization |
| **date-fns** | 4.1.0 | Date utilities |

### **Development Tools**
- **ESLint** - Code linting
- **Cross-env** - Environment variables management
- **TypeScript** - Static type checking

---

## **📁 Project Structure**

```
frontend/
├── app/                          # Next.js 16 App Router
│   ├── auth/                    # Authentication pages
│   │   ├── login/              # Login page
│   │   ├── register/           # Registration page
│   │   ├── forgot-password/    # Password reset
│   │   └── verify-email/       # Email verification
│   ├── chat/                    # Chat interface
│   ├── explore/                 # Tourism discovery
│   │   ├── attractions/        # Attraction listings
│   │   ├── hotels/             # Hotel search
│   │   ├── restaurants/        # Restaurant search
│   │   └── events/             # Events & festivals
│   ├── planner/                 # Itinerary planning
│   │   ├── create/             # Create new itinerary
│   │   ├── my-trips/           # User's saved trips
│   │   └── [id]/               # Individual trip details
│   ├── safety/                  # Safety & emergency
│   │   ├── emergency/          # Emergency contacts
│   │   ├── sos/                # SOS feature
│   │   └── tips/               # Safety tips
│   ├── dashboard/               # User dashboard
│   │   ├── settings/           # User settings
│   │   │   ├── profile/        # Profile settings
│   │   │   ├── security/       # Security settings
│   │   │   └── mfa/            # MFA/2FA setup
│   │   ├── bookmarks/          # Saved places
│   │   └── history/            # Trip history
│   ├── forum/                   # Community forum
│   ├── recommendations/         # Personalized recommendations
│   ├── weather/                 # Weather information
│   ├── transport/               # Transport information
│   ├── currency/                # Currency converter
│   ├── challenges/              # Gamification challenges
│   ├── admin/                   # Admin panel
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Homepage
│   ├── globals.css             # Global styles
│   ├── loading.tsx             # Loading state
│   ├── error.tsx               # Error boundary
│   └── not-found.tsx           # 404 page
│
├── components/                  # React components
│   ├── ui/                     # Reusable UI components
│   │   ├── button.tsx          # Button component
│   │   ├── input.tsx           # Input field
│   │   ├── card.tsx            # Card component
│   │   ├── modal.tsx           # Modal dialog
│   │   ├── tabs.tsx            # Tabs component
│   │   ├── select.tsx          # Select dropdown
│   │   ├── textarea.tsx        # Text area
│   │   ├── badge.tsx           # Badge component
│   │   ├── rating.tsx          # Rating stars
│   │   ├── slider.tsx          # Slider component
│   │   ├── loading.tsx         # Loading spinner
│   │   ├── accordion.tsx       # Accordion component
│   │   ├── date-picker.tsx     # Date picker
│   │   └── image-gallery.tsx   # Image gallery
│   ├── features/               # Feature-specific components
│   │   ├── voice-input.tsx     # Voice input component
│   │   ├── image-upload.tsx    # Image upload component
│   │   ├── map-view.tsx        # Map integration
│   │   ├── weather-widget.tsx  # Weather widget
│   │   └── currency-converter.tsx # Currency converter
│   ├── layout/                 # Layout components
│   │   ├── navbar.tsx          # Navigation bar
│   │   ├── footer.tsx          # Footer
│   │   └── sidebar.tsx         # Sidebar
│   ├── providers.tsx           # React Query provider
│   ├── theme-provider.tsx      # Theme provider
│   ├── theme-toggle.tsx        # Theme switcher
│   └── analytics.tsx           # Analytics component
│
├── lib/                         # Utilities & helpers
│   ├── api-client.ts           # Axios API client
│   ├── i18n.ts                 # Internationalization
│   ├── utils.ts                # Utility functions
│   ├── analytics.ts            # Analytics tracking
│   ├── error-tracking.ts       # Error tracking (Sentry)
│   ├── theme-config.ts         # Theme configuration
│   └── lazy-load.tsx           # Lazy loading utility
│
├── store/                       # Zustand state stores
│   ├── auth-store.ts           # Authentication state
│   ├── language-store.ts       # Language state
│   └── theme-store.ts          # Theme state
│
├── types/                       # TypeScript types
│   └── index.ts                # Type definitions
│
├── public/                      # Static assets
│   ├── images/                 # Images
│   ├── icons/                  # Icons
│   └── fonts/                  # Custom fonts
│
├── hooks/                       # Custom React hooks
│   ├── useAuth.ts              # Authentication hook
│   ├── useLanguage.ts          # Language hook
│   ├── useTheme.ts             # Theme hook
│   └── useChat.ts              # Chat hook
│
└── src/                         # Additional source files
```

---

## **🎨 Design System**

### **Color Palette**
```css
Primary (Teal):     #14b8a6  /* Main brand color */
Ocean Blue:         #3b82f6  /* Accent color */
Green:              #22c55e  /* Success states */
Sand:               #78716c  /* Neutral/text */
Background Light:   #ffffff
Background Dark:    #1a1a1a
```

### **Typography**
- **Font Family**: Geist Sans (with system fallbacks)
- **Headings**: Bold, tracking-tight
- **Body Text**: Regular weight, optimized readability
- **Font Sizes**: Responsive scaling with Tailwind

### **Components**
All components follow:
- ✅ **Accessibility best practices** (ARIA labels, keyboard navigation)
- ✅ **Responsive design** (mobile-first)
- ✅ **Consistent styling** (design tokens)
- ✅ **Reusability** (composition pattern)

---

## **🔌 API Integration**

### **Backend Integration**
- **Base URL**: `http://localhost:8000` (configurable via `.env.local`)
- **Authentication**: JWT tokens with automatic refresh
- **Error Handling**: Centralized error interceptors
- **Caching**: TanStack Query with smart cache invalidation

### **Integrated API Endpoints**

#### **Authentication**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/verify-email` - Email verification
- `POST /api/v1/auth/forgot-password` - Password reset
- `POST /api/v1/auth/setup-mfa` - MFA setup
- `POST /api/v1/auth/verify-mfa` - MFA verification

#### **Chat**
- `POST /api/v1/chat/send` - Send message
- `GET /api/v1/chat/conversations` - Get conversations
- `POST /api/v1/chat/conversations` - Create conversation
- `DELETE /api/v1/chat/conversations/{id}` - Delete conversation
- `WebSocket /ws/chat` - Real-time chat

#### **Tourism**
- `GET /api/v1/attractions` - List attractions
- `GET /api/v1/attractions/{id}` - Get attraction details
- `GET /api/v1/hotels` - Search hotels
- `GET /api/v1/restaurants` - Search restaurants
- `GET /api/v1/events` - List events

#### **Itinerary**
- `POST /api/v1/itinerary/generate` - Generate itinerary
- `GET /api/v1/itinerary/my-trips` - Get user trips
- `POST /api/v1/itinerary/save` - Save trip
- `GET /api/v1/itinerary/{id}/pdf` - Export to PDF
- `GET /api/v1/itinerary/{id}/calendar` - Export to calendar

#### **Maps**
- `POST /api/v1/maps/geocode` - Geocode address
- `POST /api/v1/maps/reverse-geocode` - Reverse geocode
- `GET /api/v1/maps/search-places` - Search places
- `GET /api/v1/maps/place/{id}` - Place details
- `POST /api/v1/maps/directions` - Get directions
- `GET /api/v1/maps/nearby-attractions` - Nearby attractions

#### **Safety**
- `GET /api/v1/safety/tips` - Safety tips
- `GET /api/v1/emergency/contacts` - Emergency contacts
- `POST /api/v1/emergency/sos` - Send SOS alert

#### **User**
- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update profile
- `GET /api/v1/users/bookmarks` - Get bookmarks
- `POST /api/v1/users/bookmarks` - Add bookmark

#### **Weather & Currency**
- `GET /api/v1/weather/{location}` - Get weather
- `GET /api/v1/currency/convert` - Convert currency

---

## **🚀 Getting Started**

### **Prerequisites**
- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### **Installation**

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Create environment file
cp ENV_SETUP.md .env.local
# Edit .env.local and add:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# 4. Run development server
npm run dev

# 5. Open browser
# Navigate to http://localhost:3000
```

### **Available Scripts**

```bash
# Development
npm run dev                  # Start dev server (normal)
npm run dev:low-memory      # Start dev server (low memory mode)
npm run dev:simple          # Start dev server (simple mode)

# Production
npm run build               # Build for production
npm run build:low-memory    # Build (low memory mode)
npm run build:simple        # Build (simple mode)
npm run start               # Start production server

# Code Quality
npm run lint                # Run ESLint
```

---

## **📱 Pages & Routes**

### **Public Pages**
| Route | Page | Description |
|-------|------|-------------|
| `/` | Homepage | Landing page with hero section |
| `/auth/login` | Login | User authentication |
| `/auth/register` | Register | New user registration |
| `/auth/forgot-password` | Forgot Password | Password reset |
| `/auth/verify-email` | Email Verification | Verify email address |

### **Protected Pages** (Require Authentication)
| Route | Page | Description |
|-------|------|-------------|
| `/chat` | Chat Interface | AI chatbot interface |
| `/explore` | Explore | Tourism discovery hub |
| `/explore/attractions` | Attractions | Browse attractions |
| `/explore/hotels` | Hotels | Search hotels |
| `/explore/restaurants` | Restaurants | Find restaurants |
| `/explore/events` | Events | Cultural events |
| `/planner` | Trip Planner | Itinerary planning |
| `/planner/create` | Create Trip | New itinerary |
| `/planner/my-trips` | My Trips | Saved trips |
| `/dashboard` | Dashboard | User dashboard |
| `/dashboard/settings` | Settings | User settings |
| `/dashboard/settings/mfa` | MFA Setup | Two-factor authentication |
| `/dashboard/bookmarks` | Bookmarks | Saved places |
| `/safety` | Safety | Safety information |
| `/safety/emergency` | Emergency | Emergency contacts |
| `/safety/sos` | SOS | Emergency SOS |
| `/forum` | Forum | Community forum |
| `/recommendations` | Recommendations | Personalized suggestions |
| `/weather` | Weather | Weather information |
| `/transport` | Transport | Transport info |
| `/currency` | Currency | Currency converter |

### **Admin Pages** (Require Admin Role)
| Route | Page | Description |
|-------|------|-------------|
| `/admin` | Admin Dashboard | Admin control panel |
| `/admin/users` | User Management | Manage users |
| `/admin/content` | Content Management | Manage content |

---

## **💾 State Management**

### **Zustand Stores**

#### **1. Auth Store** (`store/auth-store.ts`)
```typescript
- user: User | null
- token: string | null
- isAuthenticated: boolean
- login(credentials)
- logout()
- refreshToken()
```

#### **2. Language Store** (`store/language-store.ts`)
```typescript
- language: string
- supportedLanguages: string[]
- setLanguage(lang)
- translations: Record<string, string>
```

#### **3. Theme Store** (`store/theme-store.ts`)
```typescript
- theme: 'light' | 'dark'
- toggleTheme()
- setTheme(theme)
```

---

## **🎯 Key Features Implementation**

### **1. Voice Input** 🎤
- **Location**: `components/features/voice-input.tsx`
- **Technology**: Web Speech API
- **Features**:
  - Speech-to-text conversion
  - Real-time transcription
  - Language-aware recognition
  - Browser compatibility fallbacks

### **2. Image Upload** 📸
- **Location**: `components/features/image-upload.tsx`
- **Features**:
  - Drag & drop support
  - Image preview
  - File size validation (max 10MB)
  - Format validation (JPG, PNG, GIF, WebP)
  - Landmark recognition integration

### **3. Map Integration** 🗺️
- **Location**: `components/features/map-view.tsx`
- **Features**:
  - Interactive map display
  - Location markers
  - Directions
  - Nearby places search
  - Geolocation support

### **4. Weather Widget** 🌤️
- **Location**: `components/features/weather-widget.tsx`
- **Features**:
  - Current weather display
  - 7-day forecast
  - Location-based weather
  - Weather icons & animations

### **5. Currency Converter** 💱
- **Location**: `components/features/currency-converter.tsx`
- **Features**:
  - Real-time exchange rates
  - Multiple currency support
  - Amount calculation
  - Recent conversions history

### **6. MFA/2FA Setup** 🔐
- **Location**: `app/dashboard/settings/mfa`
- **Features**:
  - QR code generation
  - TOTP authentication
  - Backup codes
  - Recovery options

---

## **♿ Accessibility Features**

### **WCAG 2.1 AA Compliance**
- ✅ **Semantic HTML**: Proper heading hierarchy, landmarks
- ✅ **ARIA Labels**: All interactive elements labeled
- ✅ **Keyboard Navigation**: Full keyboard support (Tab, Enter, Escape, Arrow keys)
- ✅ **Focus Management**: Visible focus indicators, focus trapping in modals
- ✅ **Screen Reader Support**: Descriptive text for screen readers
- ✅ **Color Contrast**: Minimum 4.5:1 contrast ratio
- ✅ **Responsive Text**: Scalable fonts, readable at 200% zoom
- ✅ **Alternative Text**: Images have descriptive alt text
- ✅ **Error Messages**: Clear, descriptive error messages
- ✅ **Form Labels**: All form inputs properly labeled

### **Keyboard Shortcuts**
| Key | Action |
|-----|--------|
| `Tab` | Navigate forward |
| `Shift + Tab` | Navigate backward |
| `Enter` | Activate/Submit |
| `Escape` | Close modal/dialog |
| `Arrow Keys` | Navigate lists/menus |
| `/` | Focus search |

---

## **🌍 Internationalization (i18n)**

### **Supported Languages**
1. **English** (en) - Default
2. **Sinhala** (සිංහල) (si)
3. **Tamil** (தமிழ்) (ta)
4. **German** (de)
5. **French** (fr)
6. **Chinese** (中文) (zh)
7. **Japanese** (日本語) (ja)

### **Implementation**
- **Location**: `lib/i18n.ts`
- **Features**:
  - Automatic language detection
  - Browser language preference
  - Persistent language selection
  - RTL support (future)
  - Dynamic content translation

---

## **📊 Performance Optimization**

### **Optimization Techniques**
- ✅ **Code Splitting**: Automatic with Next.js App Router
- ✅ **Lazy Loading**: Components and routes loaded on demand
- ✅ **Image Optimization**: Next.js Image component with automatic optimization
- ✅ **API Response Caching**: TanStack Query with intelligent cache management
- ✅ **Bundle Size Optimization**: Tree shaking, minification
- ✅ **Server-Side Rendering**: SSR for critical pages
- ✅ **Static Generation**: ISR for static content
- ✅ **Font Optimization**: Next.js font optimization

### **Performance Metrics**
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Time to Interactive**: < 3.5s
- **Cumulative Layout Shift**: < 0.1

---

## **🔒 Security Features**

### **Authentication & Authorization**
- JWT token-based authentication
- Secure token storage (httpOnly cookies)
- Automatic token refresh
- OAuth 2.0 integration (Google, Facebook)
- MFA/2FA support (TOTP)

### **Data Protection**
- HTTPS enforcement
- XSS protection
- CSRF protection
- Input validation (Zod schemas)
- Sanitized user inputs
- Secure headers (CSP, HSTS)

---

## **🧪 Testing**

### **Testing Checklist**
See [TESTING_GUIDE.md](../frontend/TESTING_GUIDE.md) for detailed testing procedures:

- ✅ Voice input functionality
- ✅ Image upload & recognition
- ✅ MFA setup flow
- ✅ Real-time chat
- ✅ Map integration
- ✅ Language switching
- ✅ Theme toggling
- ✅ Form validation
- ✅ Error handling
- ✅ Responsive design

---

## **🌐 Browser Support**

| Browser | Version | Support |
|---------|---------|---------|
| Chrome | Latest | ✅ Full |
| Firefox | Latest | ✅ Full |
| Safari | Latest | ✅ Full |
| Edge | Latest | ✅ Full |
| Chrome Mobile | Latest | ✅ Full |
| Safari Mobile | Latest | ✅ Full |

---

## **📈 Analytics & Monitoring**

### **Integrated Analytics**
- **Google Analytics**: User behavior tracking
- **Error Tracking**: Sentry integration (optional)
- **Performance Monitoring**: Web Vitals tracking
- **Custom Events**: User interaction tracking

### **Tracked Metrics**
- Page views
- User sessions
- Chat interactions
- Search queries
- Itinerary creations
- Booking clicks
- Error rates
- Performance metrics

---

## **🎮 Special Features**

### **Gamification**
- **Challenges**: `/challenges` - Tourism challenges
- **Achievements**: User badges and rewards
- **Progress Tracking**: Trip milestones

### **Community**
- **Forum**: `/forum` - Community discussions
- **Reviews**: User-generated content
- **Recommendations**: Social sharing

### **Personalization**
- **AI Recommendations**: Based on user preferences
- **Saved Places**: Bookmark favorite locations
- **Trip History**: View past itineraries
- **Preferences**: Customizable user settings

---

## **🚧 Development Status**

### ✅ **Completed Features**
- ✅ Authentication & authorization
- ✅ Chat interface with WebSocket
- ✅ Voice input integration
- ✅ Image upload & recognition
- ✅ MFA/2FA setup
- ✅ Map integration
- ✅ Weather widget
- ✅ Currency converter
- ✅ Multilingual support
- ✅ Theme switching
- ✅ Responsive design
- ✅ Accessibility features
- ✅ API integration
- ✅ State management

### 🚧 **In Progress**
- 🚧 Admin panel enhancements
- 🚧 Advanced analytics dashboard
- 🚧 Social media integration
- 🚧 Payment gateway integration
- 🚧 Push notifications

### 📋 **Planned Features**
- 📋 Mobile app (React Native)
- 📋 PWA support
- 📋 Offline mode
- 📋 Voice assistant (full conversation)
- 📋 AR/VR experiences
- 📋 Advanced gamification

---

## **📚 Documentation**

### **Frontend Documentation**
- **README.md** - Project overview
- **TESTING_GUIDE.md** - Testing procedures
- **ENV_SETUP.md** - Environment setup
- **FRONTEND_OVERVIEW.md** - This document

### **Related Documentation**
- **Backend API Docs**: `backend/API_DOCUMENTATION.md`
- **Architecture Docs**: `backend/ARCHITECTURE.md`
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`

---

## **🤝 Contributing**

### **Development Guidelines**
1. Follow the existing code style
2. Ensure TypeScript types are properly defined
3. Add proper accessibility attributes
4. Test on multiple devices and browsers
5. Update documentation for new features
6. Follow component naming conventions
7. Use Tailwind CSS for styling
8. Implement responsive design

### **Code Style**
- **Component Names**: PascalCase
- **File Names**: kebab-case
- **Variable Names**: camelCase
- **Constants**: UPPER_SNAKE_CASE
- **CSS Classes**: Tailwind utility classes

---

## **📞 Frontend Information**

- **Version**: 0.1.0
- **Framework**: Next.js 16.1.1
- **React Version**: 19.2.3
- **TypeScript Version**: 5.x
- **Styling**: Tailwind CSS 4.x
- **License**: MIT
- **Status**: Active Development

---

**Built with ❤️ for Sri Lanka Tourism**

*Modern, Accessible, and Multilingual Frontend Experience*
