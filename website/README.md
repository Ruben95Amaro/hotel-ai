# Grand Ocean Hotel - Website

Modern hotel website built with React 18, Vite, and Tailwind CSS. Integrates with the Hotel AI Assistant backend API.

## Features

- 🏨 **Home Page** - Hero with booking search, features, stats
- 🛏️ **Rooms & Suites** - Interactive room catalog with availability checking
- 🍽️ **Services** - Dining, spa, concierge, pool, business, family services
- ℹ️ **About** - Hotel story, values, team, contact form
- 📅 **Booking** - Multi-step booking flow (dates → guest info → payment → confirmation)
- 📋 **My Bookings** - View, manage, cancel reservations
- 💝 **Special Requests** - Submit and track special requests
- 🤖 **AI Chat** - Integrated AI concierge assistant
- 👤 **Profile** - Manage profile and preferences
- 🔐 **Authentication** - Login/Register with social options

## Tech Stack

- **React 18** with Hooks
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **React Router v6** for navigation
- **React Hook Form** for form handling
- **Axios** for API requests
- **React Hot Toast** for notifications
- **Lucide React** for icons
- **Date-fns** for date formatting

## Getting Started

### Prerequisites

- Node.js 18+
- Backend API running on `http://localhost:8000`

### Installation

```bash
cd website
npm install
```

### Development

```bash
npm run dev
```

Opens at `http://localhost:3000` with API proxy to `http://localhost:8000`

### Build

```bash
npm run build
```

Output in `dist/` folder

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
website/
├── public/
│   └── hero-pattern.svg
├── src/
│   ├── components/
│   │   └── Layout.jsx
│   ├── context/
│   │   └── AuthContext.jsx
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── Rooms.jsx
│   │   ├── Services.jsx
│   │   ├── About.jsx
│   │   ├── Booking.jsx
│   │   ├── Bookings.jsx
│   │   ├── Requests.jsx
│   │   ├── Chat.jsx
│   │   ├── Profile.jsx
│   │   ├── Login.jsx
│   │   └── Register.jsx
│   ├── services/
│   │   └── api.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── .gitignore
```

## API Integration

The website connects to the Hotel AI Assistant backend:

- **Base URL**: `/api` (proxied to `http://localhost:8000`)
- **Auth**: JWT tokens in localStorage
- **API Key**: `dev-key-12345` (development)

### Endpoints Used

```
GET    /hotel/info
GET    /hotel/services
GET    /hotel/rooms
POST   /hotel/availability
POST   /auth/login
POST   /auth/register
GET    /auth/profile
POST   /bookings
GET    /bookings
GET    /bookings/:id
POST   /bookings/:id/cancel
PUT    /bookings/:id
POST   /special-requests
GET    /special-requests
POST   /chat
```

## Customization

### Hotel Branding

Update in `tailwind.config.js`:
- Colors (primary, accent)
- Fonts (Inter, Playfair Display)

### Hotel Info

Update in components/pages:
- Hotel name, location, contact
- Room types, pricing, amenities
- Services and features

## Deployment

### Static Hosting (Netlify, Vercel, GitHub Pages)

```bash
npm run build
# Deploy dist/ folder
```

### Docker

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

## Environment Variables

Create `.env.local` for local development:

```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=dev-key-12345
```

## License

MIT