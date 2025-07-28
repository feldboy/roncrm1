import { io, Socket } from 'socket.io-client'

class WebSocketService {
  private socket: Socket | null = null

  connect() {
    if (this.socket?.connected) return

    const token = localStorage.getItem('auth_token')
    this.socket = io('/', {
      auth: {
        token
      },
      transports: ['websocket']
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
    })

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected')
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
    })
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  on(event: string, callback: (...args: any[]) => void) {
    if (this.socket) {
      this.socket.on(event, callback)
    }
  }

  off(event: string, callback?: (...args: any[]) => void) {
    if (this.socket) {
      this.socket.off(event, callback)
    }
  }

  emit(event: string, data?: any) {
    if (this.socket) {
      this.socket.emit(event, data)
    }
  }

  get connected() {
    return this.socket?.connected || false
  }
}

export const wsService = new WebSocketService()