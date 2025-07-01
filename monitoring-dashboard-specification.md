# Monitoring Dashboard Specification

## Overview
Comprehensive monitoring dashboard for the AI-Powered Crypto Trading Bot system, providing real-time insights into microservices health, user activity, trading performance, and system metrics.

## Dashboard Architecture

### 1. Dashboard Types

#### A. Admin Dashboard
- **Purpose**: System administration and monitoring
- **Access**: Admin users only
- **Features**: Full system control and monitoring

#### B. User Dashboard
- **Purpose**: Personal trading and portfolio management
- **Access**: Authenticated users
- **Features**: Personal data and trading controls

#### C. Public Dashboard
- **Purpose**: System status and basic metrics
- **Access**: Public (limited data)
- **Features**: System uptime and basic health

### 2. Technology Stack

```yaml
Frontend:
  - Vue.js 3 with Composition API
  - Vuetify 3 (Material Design)
  - Chart.js / ApexCharts for visualizations
  - Socket.io for real-time updates
  - Pinia for state management

Backend:
  - FastAPI for dashboard API
  - WebSocket for real-time data
  - Redis for caching and pub/sub
  - PostgreSQL for data storage
  - Prometheus for metrics collection

Deployment:
  - Docker containers
  - Azure Container Apps
  - Azure Application Gateway
  - Azure Monitor integration
```

## Admin Dashboard Components

### 1. System Overview Panel

```vue
<!-- SystemOverview.vue -->
<template>
  <v-container fluid>
    <v-row>
      <!-- System Health Cards -->
      <v-col cols="12" md="3" v-for="service in services" :key="service.name">
        <v-card :color="getHealthColor(service.status)" dark>
          <v-card-title>
            <v-icon left>{{ getServiceIcon(service.name) }}</v-icon>
            {{ service.name }}
          </v-card-title>
          <v-card-text>
            <div class="text-h4">{{ service.status }}</div>
            <div class="text-caption">
              Uptime: {{ formatUptime(service.uptime) }}
            </div>
            <div class="text-caption">
              Response: {{ service.responseTime }}ms
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Real-time Metrics Charts -->
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>CPU Usage</v-card-title>
          <v-card-text>
            <apexchart
              type="line"
              :options="cpuChartOptions"
              :series="cpuSeries"
              height="300"
            />
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Memory Usage</v-card-title>
          <v-card-text>
            <apexchart
              type="area"
              :options="memoryChartOptions"
              :series="memorySeries"
              height="300"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Service Details Table -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            Microservices Status
            <v-spacer></v-spacer>
            <v-btn @click="refreshServices" icon>
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-card-title>
          <v-data-table
            :headers="serviceHeaders"
            :items="services"
            :loading="loading"
            class="elevation-1"
          >
            <template v-slot:item.status="{ item }">
              <v-chip :color="getHealthColor(item.status)" dark small>
                {{ item.status }}
              </v-chip>
            </template>
            <template v-slot:item.actions="{ item }">
              <v-btn @click="viewServiceDetails(item)" icon small>
                <v-icon>mdi-eye</v-icon>
              </v-btn>
              <v-btn @click="restartService(item)" icon small color="warning">
                <v-icon>mdi-restart</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useMonitoringStore } from '@/stores/monitoring'
import { io } from 'socket.io-client'

const monitoringStore = useMonitoringStore()
const socket = ref(null)
const services = ref([])
const loading = ref(false)

const serviceHeaders = [
  { title: 'Service', value: 'name' },
  { title: 'Status', value: 'status' },
  { title: 'Version', value: 'version' },
  { title: 'Replicas', value: 'replicas' },
  { title: 'CPU %', value: 'cpuUsage' },
  { title: 'Memory %', value: 'memoryUsage' },
  { title: 'Response Time', value: 'responseTime' },
  { title: 'Actions', value: 'actions', sortable: false }
]

const cpuChartOptions = ref({
  chart: {
    type: 'line',
    animations: {
      enabled: true,
      easing: 'linear',
      dynamicAnimation: {
        speed: 1000
      }
    },
    toolbar: {
      show: false
    },
    zoom: {
      enabled: false
    }
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    curve: 'smooth'
  },
  title: {
    text: 'Real-time CPU Usage',
    align: 'left'
  },
  markers: {
    size: 0
  },
  xaxis: {
    type: 'datetime',
    range: 300000 // 5 minutes
  },
  yaxis: {
    max: 100,
    min: 0,
    title: {
      text: 'CPU Usage (%)'
    }
  },
  legend: {
    show: true
  }
})

const cpuSeries = ref([])
const memorySeries = ref([])

const getHealthColor = (status) => {
  switch (status) {
    case 'healthy': return 'success'
    case 'warning': return 'warning'
    case 'critical': return 'error'
    default: return 'grey'
  }
}

const getServiceIcon = (serviceName) => {
  const icons = {
    'api-gateway': 'mdi-gate',
    'trading-engine': 'mdi-chart-line',
    'ai-processor': 'mdi-brain',
    'telegram-bot': 'mdi-telegram',
    'portfolio-manager': 'mdi-wallet',
    'exchange-connector': 'mdi-swap-horizontal',
    'notification-service': 'mdi-bell',
    'user-service': 'mdi-account-group'
  }
  return icons[serviceName] || 'mdi-cog'
}

const formatUptime = (seconds) => {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${days}d ${hours}h ${minutes}m`
}

const refreshServices = async () => {
  loading.value = true
  try {
    await monitoringStore.fetchServiceHealth()
    services.value = monitoringStore.services
  } finally {
    loading.value = false
  }
}

const viewServiceDetails = (service) => {
  // Navigate to service detail view
  console.log('View details for:', service.name)
}

const restartService = async (service) => {
  try {
    await monitoringStore.restartService(service.name)
    await refreshServices()
  } catch (error) {
    console.error('Failed to restart service:', error)
  }
}

onMounted(async () => {
  // Initialize WebSocket connection
  socket.value = io('/monitoring', {
    auth: {
      token: localStorage.getItem('auth_token')
    }
  })

  // Listen for real-time updates
  socket.value.on('service_health_update', (data) => {
    const index = services.value.findIndex(s => s.name === data.name)
    if (index !== -1) {
      services.value[index] = { ...services.value[index], ...data }
    }
  })

  socket.value.on('metrics_update', (data) => {
    // Update charts with new metrics
    updateCharts(data)
  })

  // Initial data load
  await refreshServices()
})

onUnmounted(() => {
  if (socket.value) {
    socket.value.disconnect()
  }
})

const updateCharts = (metricsData) => {
  // Update CPU chart
  if (metricsData.cpu) {
    cpuSeries.value = metricsData.cpu.map(service => ({
      name: service.name,
      data: service.data
    }))
  }

  // Update memory chart
  if (metricsData.memory) {
    memorySeries.value = metricsData.memory.map(service => ({
      name: service.name,
      data: service.data
    }))
  }
}
</script>
```

### 2. User Analytics Panel

```vue
<!-- UserAnalytics.vue -->
<template>
  <v-container fluid>
    <!-- User Statistics Cards -->
    <v-row>
      <v-col cols="12" md="3">
        <v-card color="primary" dark>
          <v-card-title>
            <v-icon left>mdi-account-group</v-icon>
            Total Users
          </v-card-title>
          <v-card-text>
            <div class="text-h3">{{ userStats.total }}</div>
            <div class="text-caption">
              +{{ userStats.newToday }} today
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card color="success" dark>
          <v-card-title>
            <v-icon left>mdi-account-check</v-icon>
            Active Users
          </v-card-title>
          <v-card-text>
            <div class="text-h3">{{ userStats.active }}</div>
            <div class="text-caption">
              {{ userStats.activePercent }}% of total
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card color="info" dark>
          <v-card-title>
            <v-icon left>mdi-telegram</v-icon>
            Telegram Users
          </v-card-title>
          <v-card-text>
            <div class="text-h3">{{ userStats.telegram }}</div>
            <div class="text-caption">
              {{ userStats.telegramPercent }}% of total
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card color="warning" dark>
          <v-card-title>
            <v-icon left>mdi-chart-line</v-icon>
            Trading Users
          </v-card-title>
          <v-card-text>
            <div class="text-h3">{{ userStats.trading }}</div>
            <div class="text-caption">
              {{ userStats.tradingPercent }}% of total
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- User Activity Charts -->
    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>User Registration Trend</v-card-title>
          <v-card-text>
            <apexchart
              type="area"
              :options="registrationChartOptions"
              :series="registrationSeries"
              height="350"
            />
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>User Distribution</v-card-title>
          <v-card-text>
            <apexchart
              type="donut"
              :options="distributionChartOptions"
              :series="distributionSeries"
              height="350"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent User Activity -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            Recent User Activity
            <v-spacer></v-spacer>
            <v-text-field
              v-model="search"
              append-icon="mdi-magnify"
              label="Search users"
              single-line
              hide-details
              dense
            ></v-text-field>
          </v-card-title>
          <v-data-table
            :headers="userHeaders"
            :items="recentUsers"
            :search="search"
            :loading="loading"
            class="elevation-1"
          >
            <template v-slot:item.status="{ item }">
              <v-chip :color="item.isActive ? 'success' : 'grey'" small>
                {{ item.isActive ? 'Active' : 'Inactive' }}
              </v-chip>
            </template>
            <template v-slot:item.lastActivity="{ item }">
              {{ formatRelativeTime(item.lastActivity) }}
            </template>
            <template v-slot:item.actions="{ item }">
              <v-btn @click="viewUserDetails(item)" icon small>
                <v-icon>mdi-eye</v-icon>
              </v-btn>
              <v-btn @click="toggleUserStatus(item)" icon small>
                <v-icon>{{ item.isActive ? 'mdi-pause' : 'mdi-play' }}</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { formatRelativeTime } from '@/utils/dateUtils'

const userStore = useUserStore()
const loading = ref(false)
const search = ref('')

const userStats = ref({
  total: 0,
  active: 0,
  telegram: 0,
  trading: 0,
  newToday: 0,
  activePercent: 0,
  telegramPercent: 0,
  tradingPercent: 0
})

const recentUsers = ref([])

const userHeaders = [
  { title: 'Username', value: 'username' },
  { title: 'Email', value: 'email' },
  { title: 'Role', value: 'role' },
  { title: 'Status', value: 'status' },
  { title: 'Last Activity', value: 'lastActivity' },
  { title: 'Trades', value: 'tradeCount' },
  { title: 'Actions', value: 'actions', sortable: false }
]

const registrationChartOptions = ref({
  chart: {
    type: 'area',
    stacked: false,
    height: 350,
    zoom: {
      type: 'x',
      enabled: true,
      autoScaleYaxis: true
    },
    toolbar: {
      autoSelected: 'zoom'
    }
  },
  dataLabels: {
    enabled: false
  },
  markers: {
    size: 0
  },
  title: {
    text: 'User Registration Over Time',
    align: 'left'
  },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      inverseColors: false,
      opacityFrom: 0.5,
      opacityTo: 0,
      stops: [0, 90, 100]
    }
  },
  yaxis: {
    title: {
      text: 'Number of Users'
    }
  },
  xaxis: {
    type: 'datetime'
  },
  tooltip: {
    shared: false,
    y: {
      formatter: function (val) {
        return val + ' users'
      }
    }
  }
})

const registrationSeries = ref([])

const distributionChartOptions = ref({
  chart: {
    type: 'donut'
  },
  labels: ['Web Users', 'Telegram Users', 'Mobile Users'],
  responsive: [{
    breakpoint: 480,
    options: {
      chart: {
        width: 200
      },
      legend: {
        position: 'bottom'
      }
    }
  }]
})

const distributionSeries = ref([44, 55, 13])

const viewUserDetails = (user) => {
  // Navigate to user detail view
  console.log('View details for user:', user.username)
}

const toggleUserStatus = async (user) => {
  try {
    await userStore.toggleUserStatus(user.id)
    // Refresh user list
    await loadUserData()
  } catch (error) {
    console.error('Failed to toggle user status:', error)
  }
}

const loadUserData = async () => {
  loading.value = true
  try {
    const [stats, users, chartData] = await Promise.all([
      userStore.getUserStats(),
      userStore.getRecentUsers(),
      userStore.getRegistrationChartData()
    ])
    
    userStats.value = stats
    recentUsers.value = users
    registrationSeries.value = chartData
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUserData()
})
</script>
```

### 3. Trading Analytics Panel

```vue
<!-- TradingAnalytics.vue -->
<template>
  <v-container fluid>
    <!-- Trading Statistics -->
    <v-row>
      <v-col cols="12" md="3">
        <v-card color="success" dark>
          <v-card-title>
            <v-icon left>mdi-trending-up</v-icon>
            Total Trades
          </v-card-title>
          <v-card-text>
            <div class="text-h3">{{ tradingStats.totalTrades }}</div>
            <div class="text-caption">
              +{{ tradingStats.tradesToday }} today
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card color="primary" dark>
          <v-card-title>
            <v-icon left>mdi-currency-usd</v-icon>
            Total Volume
          </v-card-title>
          <v-card-text>
            <div class="text-h3">${{ formatNumber(tradingStats.totalVolume) }}</div>
            <div class="text-caption">
              24h: ${{ formatNumber(tradingStats.volume24h) }}
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card color="info" dark>
          <v-card-title>
            <v-icon left>mdi-robot</v-icon>
            AI Trades
          </v-card-title>
          <v-card-text>
            <div class="text-h3">{{ tradingStats.aiTrades }}</div>
            <div class="text-caption">
              {{ tradingStats.aiTradePercent }}% of total
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card color="warning" dark>
          <v-card-title>
            <v-icon left>mdi-percent</v-icon>
            Success Rate
          </v-card-title>
          <v-card-text>
            <div class="text-h3">{{ tradingStats.successRate }}%</div>
            <div class="text-caption">
              Profitable trades
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Trading Charts -->
    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>Trading Volume Over Time</v-card-title>
          <v-card-text>
            <apexchart
              type="line"
              :options="volumeChartOptions"
              :series="volumeSeries"
              height="400"
            />
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Trade Distribution</v-card-title>
          <v-card-text>
            <apexchart
              type="pie"
              :options="tradeDistributionOptions"
              :series="tradeDistributionSeries"
              height="400"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent Trades Table -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            Recent Trades
            <v-spacer></v-spacer>
            <v-select
              v-model="selectedExchange"
              :items="exchanges"
              label="Exchange"
              dense
              outlined
              hide-details
              style="max-width: 200px;"
            ></v-select>
          </v-card-title>
          <v-data-table
            :headers="tradeHeaders"
            :items="recentTrades"
            :loading="loading"
            class="elevation-1"
          >
            <template v-slot:item.side="{ item }">
              <v-chip :color="item.side === 'buy' ? 'success' : 'error'" small>
                {{ item.side.toUpperCase() }}
              </v-chip>
            </template>
            <template v-slot:item.status="{ item }">
              <v-chip :color="getStatusColor(item.status)" small>
                {{ item.status }}
              </v-chip>
            </template>
            <template v-slot:item.source="{ item }">
              <v-icon :color="getSourceColor(item.source)" small>
                {{ getSourceIcon(item.source) }}
              </v-icon>
              {{ item.source }}
            </template>
            <template v-slot:item.pnl="{ item }">
              <span :class="item.pnl >= 0 ? 'text-success' : 'text-error'">
                {{ item.pnl >= 0 ? '+' : '' }}${{ formatNumber(item.pnl) }}
              </span>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useTradingStore } from '@/stores/trading'
import { formatNumber } from '@/utils/numberUtils'

const tradingStore = useTradingStore()
const loading = ref(false)
const selectedExchange = ref('all')

const exchanges = ref([
  { title: 'All Exchanges', value: 'all' },
  { title: 'Binance', value: 'binance' },
  { title: 'Coinbase', value: 'coinbase' },
  { title: 'Kraken', value: 'kraken' }
])

const tradingStats = ref({
  totalTrades: 0,
  tradesToday: 0,
  totalVolume: 0,
  volume24h: 0,
  aiTrades: 0,
  aiTradePercent: 0,
  successRate: 0
})

const recentTrades = ref([])

const tradeHeaders = [
  { title: 'Time', value: 'timestamp' },
  { title: 'User', value: 'username' },
  { title: 'Symbol', value: 'symbol' },
  { title: 'Side', value: 'side' },
  { title: 'Quantity', value: 'quantity' },
  { title: 'Price', value: 'price' },
  { title: 'Status', value: 'status' },
  { title: 'Source', value: 'source' },
  { title: 'P&L', value: 'pnl' }
]

const volumeChartOptions = ref({
  chart: {
    type: 'line',
    height: 400,
    zoom: {
      enabled: true
    }
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    curve: 'smooth',
    width: 2
  },
  title: {
    text: 'Daily Trading Volume',
    align: 'left'
  },
  grid: {
    row: {
      colors: ['#f3f3f3', 'transparent'],
      opacity: 0.5
    }
  },
  xaxis: {
    type: 'datetime'
  },
  yaxis: {
    title: {
      text: 'Volume (USD)'
    },
    labels: {
      formatter: function (val) {
        return '$' + formatNumber(val)
      }
    }
  }
})

const volumeSeries = ref([])

const tradeDistributionOptions = ref({
  chart: {
    type: 'pie'
  },
  labels: ['Manual', 'AI', 'Signal', 'Bot'],
  responsive: [{
    breakpoint: 480,
    options: {
      chart: {
        width: 200
      },
      legend: {
        position: 'bottom'
      }
    }
  }]
})

const tradeDistributionSeries = ref([30, 40, 20, 10])

const getStatusColor = (status) => {
  switch (status) {
    case 'filled': return 'success'
    case 'pending': return 'warning'
    case 'cancelled': return 'grey'
    case 'failed': return 'error'
    default: return 'grey'
  }
}

const getSourceColor = (source) => {
  switch (source) {
    case 'ai': return 'purple'
    case 'manual': return 'blue'
    case 'signal': return 'orange'
    case 'bot': return 'green'
    default: return 'grey'
  }
}

const getSourceIcon = (source) => {
  switch (source) {
    case 'ai': return 'mdi-brain'
    case 'manual': return 'mdi-hand'
    case 'signal': return 'mdi-signal'
    case 'bot': return 'mdi-robot'
    default: return 'mdi-help'
  }
}

const loadTradingData = async () => {
  loading.value = true
  try {
    const [stats, trades, volumeData] = await Promise.all([
      tradingStore.getTradingStats(),
      tradingStore.getRecentTrades({ exchange: selectedExchange.value }),
      tradingStore.getVolumeChartData()
    ])
    
    tradingStats.value = stats
    recentTrades.value = trades
    volumeSeries.value = volumeData
  } finally {
    loading.value = false
  }
}

watch(selectedExchange, () => {
  loadTradingData()
})

onMounted(() => {
  loadTradingData()
})
</script>
```

## Real-time Data Integration

### WebSocket Service

```typescript
// services/websocket.ts
import { io, Socket } from 'socket.io-client'
import { useAuthStore } from '@/stores/auth'

class WebSocketService {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

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

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.handleReconnect()
    })

    // Subscribe to monitoring events
    this.socket.on('service_health_update', (data) => {
      this.handleServiceHealthUpdate(data)
    })

    this.socket.on('metrics_update', (data) => {
      this.handleMetricsUpdate(data)
    })

    this.socket.on('trade_update', (data) => {
      this.handleTradeUpdate(data)
    })

    this.socket.on('user_activity_update', (data) => {
      this.handleUserActivityUpdate(data)
    })

    return this.socket
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
        this.connect()
      }, this.reconnectDelay * this.reconnectAttempts)
    }
  }

  private handleServiceHealthUpdate(data: any) {
    // Update monitoring store
    const monitoringStore = useMonitoringStore()
    monitoringStore.updateServiceHealth(data)
  }

  private handleMetricsUpdate(data: any) {
    // Update metrics in monitoring store
    const monitoringStore = useMonitoringStore()
    monitoringStore.updateMetrics(data)
  }

  private handleTradeUpdate(data: any) {
    // Update trading store
    const tradingStore = useTradingStore()
    tradingStore.updateTrade(data)
  }

  private handleUserActivityUpdate(data: any) {
    // Update user store
    const userStore = useUserStore()
    userStore.updateUserActivity(data)
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  emit(event: string, data: any) {
    if (this.socket) {
      this.socket.emit(event, data)
    }
  }
}

export const websocketService = new WebSocketService()
```

## Monitoring Store (Pinia)

```typescript
// stores/monitoring.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { monitoringApi } from '@/api/monitoring'

export const useMonitoringStore = defineStore('monitoring', () => {
  const services = ref([])
  const metrics = ref({})
  const alerts = ref([])
  const systemHealth = ref('healthy')

  const healthyServices = computed(() => 
    services.value.filter(s => s.status === 'healthy').length
  )

  const criticalServices = computed(() => 
    services.value.filter(s => s.status === 'critical').length
  )

  const overallHealth = computed(() => {
    if (criticalServices.value > 0) return 'critical'
    if (services.value.some(s => s.status === 'warning')) return 'warning'
    return 'healthy'
  })

  const fetchServiceHealth = async () => {
    try {
      const response = await monitoringApi.getServiceHealth()
      services.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch service health:', error)
      throw error
    }
  }

  const fetchMetrics = async (timeRange = '1h') => {
    try {
      const response = await monitoringApi.getMetrics(timeRange)
      metrics.value = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch metrics:', error)
      throw error
    }
  }

  const restartService = async (serviceName: string) => {
    try {
      await monitoringApi.restartService(serviceName)
      // Refresh service health after restart
      setTimeout(() => fetchServiceHealth(), 2000)
    } catch (error) {
      console.error('Failed to restart service:', error)
      throw error
    }
  }

  const updateServiceHealth = (data: any) => {
    const index = services.value.findIndex(s => s.name === data.name)
    if (index !== -1) {
      services.value[index] = { ...services.value[index], ...data }
    } else {
      services.value.push(data)
    }
  }

  const updateMetrics = (data: any) => {
    metrics.value = { ...metrics.value, ...data }
  }

  const addAlert = (alert: any) => {
    alerts.value.unshift({
      ...alert,
      id: Date.now(),
      timestamp: new Date().toISOString()
    })
    
    // Keep only last 100 alerts
    if (alerts.value.length > 100) {
      alerts.value = alerts.value.slice(0, 100)
    }
  }

  const clearAlert = (alertId: number) => {
    const index = alerts.value.findIndex(a => a.id === alertId)
    if (index !== -1) {
      alerts.value.splice(index, 1)
    }
  }

  return {
    services,
    metrics,
    alerts,
    systemHealth,
    healthyServices,
    criticalServices,
    overallHealth,
    fetchServiceHealth,
    fetchMetrics,
    restartService,
    updateServiceHealth,
    updateMetrics,
    addAlert,
    clearAlert
  }
})
```

## Deployment Configuration

### Docker Compose for Development

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  monitoring-dashboard:
    build:
      context: ./frontend
      dockerfile: Dockerfile.monitoring
    ports:
      - "3001:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
      - VITE_WS_URL=ws://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - monitoring-api

  monitoring-api:
    build:
      context: ./backend
      dockerfile: Dockerfile.monitoring
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/trading_bot
      - REDIS_URL=redis://redis:6379
      - PROMETHEUS_URL=http://prometheus:9090
    depends_on:
      - postgres
      - redis
      - prometheus

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

volumes:
  prometheus_data:
  grafana_data:
```

### Azure Container Apps Configuration

```yaml
# azure-monitoring-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: monitoring-dashboard
  namespace: trading-bot
spec:
  replicas: 2
  selector:
    matchLabels:
      app: monitoring-dashboard
  template:
    metadata:
      labels:
        app: monitoring-dashboard
    spec:
      containers:
      - name: monitoring-dashboard
        image: tradingbot.azurecr.io/monitoring-dashboard:latest
        ports:
        - containerPort: 3000
        env:
        - name: VITE_API_URL
          value: "https://api.tradingbot.com"
        - name: VITE_WS_URL
          value: "wss://api.tradingbot.com"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: monitoring-dashboard-service
  namespace: trading-bot
spec:
  selector:
    app: monitoring-dashboard
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

## Security and Access Control

### Role-Based Access Control

```typescript
// middleware/rbac.ts
import { useAuthStore } from '@/stores/auth'
import { RouteLocationNormalized } from 'vue-router'

interface Permission {
  resource: string
  action: string
}

interface Role {
  name: string
  permissions: Permission[]
}

const roles: Record<string, Role> = {
  admin: {
    name: 'admin',
    permissions: [
      { resource: 'monitoring', action: 'read' },
      { resource: 'monitoring', action: 'write' },
      { resource: 'users', action: 'read' },
      { resource: 'users', action: 'write' },
      { resource: 'trading', action: 'read' },
      { resource: 'trading', action: 'write' },
      { resource: 'system', action: 'read' },
      { resource: 'system', action: 'write' }
    ]
  },
  moderator: {
    name: 'moderator',
    permissions: [
      { resource: 'monitoring', action: 'read' },
      { resource: 'users', action: 'read' },
      { resource: 'trading', action: 'read' },
      { resource: 'system', action: 'read' }
    ]
  },
  user: {
    name: 'user',
    permissions: [
      { resource: 'trading', action: 'read' },
      { resource: 'portfolio', action: 'read' },
      { resource: 'profile', action: 'write' }
    ]
  }
}

export const hasPermission = (resource: string, action: string): boolean => {
  const authStore = useAuthStore()
  const userRole = roles[authStore.user?.role || 'user']
  
  return userRole.permissions.some(
    p => p.resource === resource && p.action === action
  )
}

export const requirePermission = (resource: string, action: string) => {
  return (to: RouteLocationNormalized, from: RouteLocationNormalized, next: any) => {
    if (hasPermission(resource, action)) {
      next()
    } else {
      next({ name: 'Unauthorized' })
    }
  }
}

export const requireRole = (requiredRole: string) => {
  return (to: RouteLocationNormalized, from: RouteLocationNormalized, next: any) => {
    const authStore = useAuthStore()
    const userRole = authStore.user?.role
    
    if (userRole === requiredRole || userRole === 'admin') {
      next()
    } else {
      next({ name: 'Unauthorized' })
    }
  }
}
```

## Performance Optimization

### Chart Data Optimization

```typescript
// utils/chartOptimization.ts
export class ChartDataOptimizer {
  private maxDataPoints = 1000
  private compressionRatio = 0.1

  optimizeTimeSeriesData(data: any[], timeRange: string) {
    if (data.length <= this.maxDataPoints) {
      return data
    }

    // Calculate sampling interval based on time range
    const interval = this.calculateSamplingInterval(data.length, timeRange)
    
    // Apply data compression
    return this.compressData(data, interval)
  }

  private calculateSamplingInterval(dataLength: number, timeRange: string): number {
    const targetPoints = this.maxDataPoints
    return Math.ceil(dataLength / targetPoints)
  }

  private compressData(data: any[], interval: number): any[] {
    const compressed = []
    
    for (let i = 0; i < data.length; i += interval) {
      const chunk = data.slice(i, i + interval)
      
      // Use average for numerical values
      const compressed_point = {
        timestamp: chunk[0].timestamp,
        value: chunk.reduce((sum, point) => sum + point.value, 0) / chunk.length,
        min: Math.min(...chunk.map(p => p.value)),
        max: Math.max(...chunk.map(p => p.value))
      }
      
      compressed.push(compressed_point)
    }
    
    return compressed
  }

  // Real-time data buffer management
  manageRealTimeBuffer(buffer: any[], newData: any, maxSize = 1000): any[] {
    buffer.push(newData)
    
    if (buffer.length > maxSize) {
      // Remove oldest data points
      buffer.splice(0, buffer.length - maxSize)
    }
    
    return buffer
  }
}

export const chartOptimizer = new ChartDataOptimizer()
```

## Summary

This monitoring dashboard specification provides:

1. **Comprehensive Admin Dashboard** with real-time microservices monitoring
2. **User Analytics Panel** with registration trends and activity tracking
3. **Trading Analytics** with volume charts and trade distribution
4. **Real-time WebSocket Integration** for live updates
5. **Role-based Access Control** for security
6. **Performance Optimization** for handling large datasets
7. **Azure-ready Deployment** configurations
8. **Dark Mode Support** integrated throughout

The dashboard supports both development and production environments with Docker Compose and Azure Container Apps configurations, ensuring scalability and maintainability.