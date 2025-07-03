# Frontend Documentation

This document provides comprehensive documentation for the Trading Signals Reader AI Bot frontend application. The frontend is built with Vue.js 3, TypeScript, and modern web technologies to provide a responsive and intuitive user interface.

## Table of Contents

1. [Frontend Overview](#frontend-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Core Components](#core-components)
5. [State Management](#state-management)
6. [Routing](#routing)
7. [UI/UX Design](#uiux-design)
8. [Real-time Features](#real-time-features)
9. [Charts and Visualization](#charts-and-visualization)
10. [Mobile Responsiveness](#mobile-responsiveness)
11. [Performance Optimization](#performance-optimization)
12. [Development Guide](#development-guide)

## Frontend Overview

The frontend application provides a comprehensive trading interface with the following key features:

- **Dashboard**: Real-time portfolio overview and market summary
- **Trading Interface**: Advanced order placement and position management
- **AI Chat**: Natural language trading commands and analysis
- **Charts**: Interactive price charts with technical indicators
- **Portfolio Management**: Detailed portfolio tracking and analytics
- **Market Analysis**: AI-powered market insights and signals
- **Settings**: User preferences and configuration
- **Mobile App**: React Native mobile application

## Technology Stack

### Core Technologies

- **Vue.js 3**: Progressive JavaScript framework with Composition API
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and development server
- **Pinia**: State management library for Vue.js
- **Vue Router**: Official router for Vue.js

### UI Framework

- **Vuetify 3**: Material Design component framework
- **Material Design Icons**: Comprehensive icon library
- **CSS3**: Modern styling with CSS Grid and Flexbox
- **SCSS**: Enhanced CSS with variables and mixins

### Charts and Visualization

- **Chart.js**: Flexible charting library
- **TradingView Charting Library**: Professional trading charts
- **D3.js**: Data-driven visualizations
- **ApexCharts**: Modern charting library

### Real-time Communication

- **Socket.io Client**: WebSocket communication
- **Server-Sent Events**: Real-time data streaming
- **WebRTC**: Peer-to-peer communication

### Development Tools

- **ESLint**: Code linting and quality
- **Prettier**: Code formatting
- **Vitest**: Unit testing framework
- **Cypress**: End-to-end testing
- **Storybook**: Component development and documentation

## Project Structure

```
frontend/
├── public/                 # Static assets
│   ├── favicon.ico
│   ├── manifest.json
│   └── robots.txt
├── src/
│   ├── assets/            # Images, fonts, and static resources
│   │   ├── images/
│   │   ├── icons/
│   │   └── styles/
│   ├── components/        # Reusable Vue components
│   │   ├── common/        # Generic components
│   │   ├── trading/       # Trading-specific components
│   │   ├── charts/        # Chart components
│   │   ├── ai/           # AI-related components
│   │   └── layout/        # Layout components
│   ├── views/            # Page components
│   │   ├── Dashboard.vue
│   │   ├── Trading.vue
│   │   ├── Portfolio.vue
│   │   ├── AIChat.vue
│   │   ├── Markets.vue
│   │   ├── Settings.vue
│   │   └── Auth/
│   ├── stores/           # Pinia stores
│   │   ├── auth.ts
│   │   ├── trading.ts
│   │   ├── portfolio.ts
│   │   ├── market.ts
│   │   ├── ai.ts
│   │   └── websocket.ts
│   ├── services/         # API and external services
│   │   ├── api.ts
│   │   ├── websocket.ts
│   │   ├── trading.ts
│   │   ├── ai.ts
│   │   └── market.ts
│   ├── types/            # TypeScript type definitions
│   │   ├── api.ts
│   │   ├── trading.ts
│   │   ├── user.ts
│   │   └── chart.ts
│   ├── utils/            # Utility functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── calculations.ts
│   │   └── constants.ts
│   ├── composables/      # Vue composition functions
│   │   ├── useAuth.ts
│   │   ├── useTrading.ts
│   │   ├── useWebSocket.ts
│   │   └── useChart.ts
│   ├── plugins/          # Vue plugins
│   │   ├── vuetify.ts
│   │   ├── router.ts
│   │   └── pinia.ts
│   ├── router/           # Vue Router configuration
│   │   ├── index.ts
│   │   └── guards.ts
│   ├── App.vue           # Root component
│   └── main.ts           # Application entry point
├── tests/                # Test files
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                 # Component documentation
├── package.json
├── vite.config.ts
├── tsconfig.json
├── eslint.config.js
└── README.md
```

## Core Components

### Layout Components

#### AppLayout.vue
Main application layout with navigation, sidebar, and content area.

**Features:**
- Responsive navigation drawer
- Top app bar with user menu
- Breadcrumb navigation
- Theme switching
- Notification center

#### NavigationDrawer.vue
Sidebar navigation with menu items and user information.

**Features:**
- Collapsible menu groups
- Active route highlighting
- User avatar and status
- Quick actions

### Trading Components

#### TradingInterface.vue
Comprehensive trading interface with order placement and management.

**Features:**
- Order form with validation
- Order book display
- Recent trades list
- Position management
- Risk management controls

```vue
<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" md="4">
        <OrderForm
          :trading-pair="selectedPair"
          :portfolio="portfolio"
          @order-placed="handleOrderPlaced"
        />
      </v-col>
      <v-col cols="12" md="4">
        <OrderBook
          :symbol="selectedPair.symbol"
          :exchange="selectedPair.exchange"
        />
      </v-col>
      <v-col cols="12" md="4">
        <RecentTrades
          :symbol="selectedPair.symbol"
          :exchange="selectedPair.exchange"
        />
      </v-col>
    </v-row>
  </v-container>
</template>
```

#### OrderForm.vue
Order placement form with advanced options.

**Features:**
- Order type selection (Market, Limit, Stop)
- Quantity and price inputs
- Balance validation
- Risk calculations
- AI signal integration

#### PositionCard.vue
Individual position display with P&L and management options.

**Features:**
- Real-time P&L updates
- Position size and entry price
- Stop loss and take profit
- Close position actions
- Performance metrics

### Chart Components

#### TradingChart.vue
Advanced trading chart with technical indicators.

**Features:**
- Candlestick and line charts
- Multiple timeframes
- Technical indicators overlay
- Drawing tools
- AI signal markers

```vue
<template>
  <div class="trading-chart">
    <ChartToolbar
      :timeframes="timeframes"
      :indicators="availableIndicators"
      @timeframe-changed="updateTimeframe"
      @indicator-toggled="toggleIndicator"
    />
    <div ref="chartContainer" class="chart-container" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useMarketStore } from '@/stores/market'
import { createChart } from 'lightweight-charts'

const props = defineProps<{
  symbol: string
  exchange: string
  timeframe: string
}>()

const chartContainer = ref<HTMLElement>()
const marketStore = useMarketStore()

let chart: any = null

onMounted(() => {
  initializeChart()
  loadMarketData()
})

const initializeChart = () => {
  chart = createChart(chartContainer.value!, {
    width: chartContainer.value!.clientWidth,
    height: 400,
    layout: {
      backgroundColor: '#ffffff',
      textColor: '#333333',
    },
    grid: {
      vertLines: { color: '#f0f0f0' },
      horzLines: { color: '#f0f0f0' },
    },
  })
}
</script>
```

### AI Components

#### AIChat.vue
Conversational AI interface for trading commands and analysis.

**Features:**
- Natural language input
- Message history
- AI response formatting
- Quick action buttons
- Voice input support

#### SignalCard.vue
AI-generated trading signal display.

**Features:**
- Signal strength indicator
- Entry and target prices
- Risk/reward ratio
- Confidence score
- One-click trading

#### MarketAnalysis.vue
AI-powered market analysis and insights.

**Features:**
- Market sentiment analysis
- Technical analysis summary
- News impact assessment
- Trend predictions
- Risk alerts

## State Management

### Pinia Stores

The application uses Pinia for centralized state management with the following stores:

#### Auth Store (auth.ts)
Manages user authentication and session state.

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials } from '@/types/user'
import { authService } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => user.value?.role || 'USER')

  const login = async (credentials: LoginCredentials) => {
    isLoading.value = true
    try {
      const response = await authService.login(credentials)
      token.value = response.access_token
      user.value = response.user
      localStorage.setItem('token', response.access_token)
      return response
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return {
    user,
    token,
    isLoading,
    isAuthenticated,
    userRole,
    login,
    logout
  }
})
```

#### Trading Store (trading.ts)
Manages trading operations, orders, and positions.

```typescript
export const useTradingStore = defineStore('trading', () => {
  const orders = ref<Order[]>([])
  const positions = ref<Position[]>([])
  const portfolio = ref<Portfolio | null>(null)
  const selectedPair = ref<TradingPair | null>(null)

  const activeOrders = computed(() => 
    orders.value.filter(order => ['PENDING', 'OPEN'].includes(order.status))
  )

  const openPositions = computed(() => 
    positions.value.filter(position => position.status === 'OPEN')
  )

  const totalPnL = computed(() => 
    positions.value.reduce((sum, pos) => sum + pos.unrealized_pnl, 0)
  )

  return {
    orders,
    positions,
    portfolio,
    selectedPair,
    activeOrders,
    openPositions,
    totalPnL
  }
})
```

#### Market Store (market.ts)
Manages market data, prices, and technical indicators.

#### AI Store (ai.ts)
Manages AI commands, responses, and trading signals.

#### WebSocket Store (websocket.ts)
Manages real-time data connections and subscriptions.

## Routing

### Route Configuration

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/trading',
    name: 'Trading',
    component: () => import('@/views/Trading.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/portfolio',
    name: 'Portfolio',
    component: () => import('@/views/Portfolio.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ai-chat',
    name: 'AIChat',
    component: () => import('@/views/AIChat.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/markets',
    name: 'Markets',
    component: () => import('@/views/Markets.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/auth/login',
    name: 'Login',
    component: () => import('@/views/Auth/Login.vue')
  },
  {
    path: '/auth/register',
    name: 'Register',
    component: () => import('@/views/Auth/Register.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/auth/login')
  } else {
    next()
  }
})

export default router
```

## UI/UX Design

### Design System

The application follows Material Design principles with custom theming:

#### Color Palette
- **Primary**: #1976D2 (Blue)
- **Secondary**: #424242 (Grey)
- **Accent**: #82B1FF (Light Blue)
- **Success**: #4CAF50 (Green)
- **Warning**: #FF9800 (Orange)
- **Error**: #F44336 (Red)

#### Typography
- **Font Family**: 'Roboto', sans-serif
- **Headings**: Roboto Medium
- **Body Text**: Roboto Regular
- **Code**: 'Roboto Mono', monospace

#### Spacing
- **Base Unit**: 8px
- **Small**: 4px
- **Medium**: 16px
- **Large**: 24px
- **Extra Large**: 32px

### Component Design

#### Cards
Consistent card design with elevation and rounded corners:

```scss
.trading-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
  background: white;
  
  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    transition: box-shadow 0.3s ease;
  }
}
```

#### Buttons
Custom button styles for different actions:

```scss
.btn-buy {
  background: linear-gradient(45deg, #4CAF50, #66BB6A);
  color: white;
  
  &:hover {
    background: linear-gradient(45deg, #388E3C, #4CAF50);
  }
}

.btn-sell {
  background: linear-gradient(45deg, #F44336, #EF5350);
  color: white;
  
  &:hover {
    background: linear-gradient(45deg, #D32F2F, #F44336);
  }
}
```

## Real-time Features

### WebSocket Integration

Real-time data updates using WebSocket connections:

```typescript
import { io, Socket } from 'socket.io-client'
import { useAuthStore } from '@/stores/auth'

class WebSocketService {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  connect() {
    const authStore = useAuthStore()
    
    this.socket = io(import.meta.env.VITE_WS_URL, {
      auth: {
        token: authStore.token
      },
      transports: ['websocket']
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
    })

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected')
      this.handleReconnect()
    })

    this.socket.on('market_data', (data) => {
      this.handleMarketData(data)
    })

    this.socket.on('order_update', (data) => {
      this.handleOrderUpdate(data)
    })

    this.socket.on('trading_signal', (data) => {
      this.handleTradingSignal(data)
    })
  }

  subscribe(channel: string, params: any) {
    this.socket?.emit('subscribe', { channel, ...params })
  }

  unsubscribe(channel: string, params: any) {
    this.socket?.emit('unsubscribe', { channel, ...params })
  }
}
```

### Real-time Data Updates

- **Market Data**: Live price updates and order book changes
- **Portfolio**: Real-time P&L and balance updates
- **Orders**: Order status and execution updates
- **AI Signals**: New trading signal notifications
- **News**: Breaking news and market alerts

## Charts and Visualization

### TradingView Integration

Professional trading charts with advanced features:

```typescript
import { widget } from 'charting_library'

class TradingViewChart {
  private widget: any

  constructor(container: HTMLElement, symbol: string) {
    this.widget = new widget({
      symbol: symbol,
      interval: '1H',
      container: container,
      library_path: '/charting_library/',
      locale: 'en',
      disabled_features: ['use_localstorage_for_settings'],
      enabled_features: ['study_templates'],
      charts_storage_url: 'https://saveload.tradingview.com',
      charts_storage_api_version: '1.1',
      client_id: 'tradingview.com',
      user_id: 'public_user_id',
      fullscreen: false,
      autosize: true,
      studies_overrides: {},
      theme: 'light'
    })
  }

  setSymbol(symbol: string) {
    this.widget.chart().setSymbol(symbol)
  }

  addStudy(study: string, inputs: any) {
    this.widget.chart().createStudy(study, false, false, inputs)
  }
}
```

### Chart.js Integration

Custom charts for portfolio and performance visualization:

```typescript
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

const createPortfolioChart = (canvas: HTMLCanvasElement, data: any) => {
  return new Chart(canvas, {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [{
        label: 'Portfolio Value',
        data: data.values,
        borderColor: '#1976D2',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Portfolio Performance'
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          ticks: {
            callback: (value) => `$${value.toLocaleString()}`
          }
        }
      }
    }
  })
}
```

## Mobile Responsiveness

### Responsive Design

The application is fully responsive with mobile-first design:

```scss
// Mobile-first breakpoints
$breakpoints: (
  xs: 0,
  sm: 600px,
  md: 960px,
  lg: 1264px,
  xl: 1904px
);

// Responsive mixins
@mixin mobile {
  @media (max-width: 599px) {
    @content;
  }
}

@mixin tablet {
  @media (min-width: 600px) and (max-width: 959px) {
    @content;
  }
}

@mixin desktop {
  @media (min-width: 960px) {
    @content;
  }
}

// Component responsive styles
.trading-interface {
  @include mobile {
    .order-form {
      margin-bottom: 16px;
    }
    
    .chart-container {
      height: 300px;
    }
  }
  
  @include desktop {
    .chart-container {
      height: 500px;
    }
  }
}
```

### Mobile Navigation

Optimized navigation for mobile devices:

- Bottom navigation bar
- Swipe gestures
- Touch-friendly buttons
- Collapsible sections

## Performance Optimization

### Code Splitting

Lazy loading of routes and components:

```typescript
// Route-based code splitting
const routes = [
  {
    path: '/trading',
    component: () => import('@/views/Trading.vue')
  }
]

// Component-based code splitting
const HeavyChart = defineAsyncComponent(() => 
  import('@/components/charts/HeavyChart.vue')
)
```

### Virtual Scrolling

Efficient rendering of large lists:

```vue
<template>
  <VirtualList
    :items="orders"
    :item-height="60"
    :container-height="400"
  >
    <template #default="{ item }">
      <OrderItem :order="item" />
    </template>
  </VirtualList>
</template>
```

### Caching Strategy

- **API Response Caching**: Cache frequently accessed data
- **Image Optimization**: WebP format with fallbacks
- **Bundle Optimization**: Tree shaking and minification
- **Service Worker**: Offline functionality and caching

## Development Guide

### Setup and Installation

```bash
# Clone repository
git clone https://github.com/your-org/trading-signals-reader-ai-bot.git
cd trading-signals-reader-ai-bot/frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Run linting
npm run lint
```

### Environment Configuration

```env
# .env.development
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=Trading Bot Dev

# .env.production
VITE_API_URL=https://api.trading-signals-bot.com/api/v1
VITE_WS_URL=wss://api.trading-signals-bot.com/ws
VITE_APP_NAME=Trading Signals Reader AI Bot
```

### Component Development

Best practices for component development:

```vue
<template>
  <div class="component-name">
    <!-- Template content -->
  </div>
</template>

<script setup lang="ts">
// Imports
import { ref, computed, onMounted } from 'vue'
import type { ComponentProps } from '@/types'

// Props
interface Props {
  required: string
  optional?: number
}

const props = withDefaults(defineProps<Props>(), {
  optional: 0
})

// Emits
interface Emits {
  update: [value: string]
  change: [event: Event]
}

const emit = defineEmits<Emits>()

// Reactive state
const state = ref('')

// Computed properties
const computedValue = computed(() => {
  return state.value.toUpperCase()
})

// Lifecycle hooks
onMounted(() => {
  // Initialization logic
})

// Methods
const handleClick = () => {
  emit('update', state.value)
}
</script>

<style scoped lang="scss">
.component-name {
  // Component styles
}
</style>
```

### Testing

```typescript
// Component test example
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import OrderForm from '@/components/trading/OrderForm.vue'

describe('OrderForm', () => {
  it('validates order quantity', async () => {
    const wrapper = mount(OrderForm, {
      props: {
        tradingPair: mockTradingPair,
        portfolio: mockPortfolio
      }
    })

    const quantityInput = wrapper.find('[data-testid="quantity-input"]')
    await quantityInput.setValue('0')
    
    expect(wrapper.find('.error-message').text())
      .toBe('Quantity must be greater than 0')
  })
})
```

---

*This frontend documentation provides comprehensive coverage of the user interface architecture, components, and development practices for the Trading Signals Reader AI Bot application.*