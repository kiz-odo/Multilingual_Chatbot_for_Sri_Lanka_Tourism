# 🔧 Environment Variables Setup

## Required: Create `.env.local` file

Create a file named `.env.local` in the `frontend` directory with:

```env
# Backend API URL (REQUIRED)
# Default is http://localhost:8001 if not set
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## Optional Environment Variables

```env
# WebSocket URL (for real-time chat features)
NEXT_PUBLIC_WS_URL=ws://localhost:8001/ws

# Google Analytics ID
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX

# Sentry DSN (for error tracking)
NEXT_PUBLIC_SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx

# Environment
NODE_ENV=development
```


## How to Create

1. Navigate to `frontend` directory
2. Create new file: `.env.local`
3. Copy the content above
4. Update `NEXT_PUBLIC_API_URL` with your backend URL
5. Restart dev server: `npm run dev`

## Note

- `.env.local` is gitignored (won't be committed)
- Use `.env.local` for local development
- Use platform environment variables for production






