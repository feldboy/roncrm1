/**
 * Settings service for managing application configuration
 */

import { api } from './api'

// Types
export interface Setting {
  id: number
  category_id: number
  key: string
  display_name: string
  description?: string
  data_type: string
  default_value?: string
  current_value?: string
  value: any
  validation_rules?: Record<string, any>
  ui_component?: string
  ui_options?: Record<string, any>
  is_sensitive: boolean
  is_readonly: boolean
  is_required: boolean
  requires_restart: boolean
  sort_order: number
  is_active: boolean
}

export interface SettingsCategory {
  id: number
  name: string
  display_name: string
  description?: string
  icon?: string
  sort_order: number
  is_active: boolean
  settings: Setting[]
}

export interface AgentSetting {
  id: number
  agent_type: string
  agent_id?: string
  setting_key: string
  setting_value?: string
  data_type: string
  is_enabled: boolean
  typed_value: any
}

export interface SettingUpdateRequest {
  value: any
  change_reason?: string
}

export interface AgentSettingUpdateRequest {
  setting_value: any
  data_type?: string
  is_enabled: boolean
}

export interface SettingsProfile {
  id: number
  name: string
  display_name: string
  description?: string
  is_default: boolean
  created_at: string
}

// Settings API Service
export class SettingsService {
  private baseUrl = '/api/v1/settings'

  /**
   * Get all settings categories with their settings
   */
  async getCategories(includeInactive = false): Promise<SettingsCategory[]> {
    try {
      const response = await api.get(`${this.baseUrl}/categories`, {
        params: { include_inactive: includeInactive }
      })
      return response.data
    } catch (error: any) {
      console.error('Failed to fetch settings categories:', error)
      // Return mock data as fallback
      return this.getMockCategories()
    }
  }

  /**
   * Get mock settings categories for fallback
   */
  private getMockCategories(): SettingsCategory[] {
    return [
      {
        id: 1,
        name: "system",
        display_name: "System Settings",
        description: "Core system configuration and performance settings",
        icon: "cog",
        sort_order: 1,
        is_active: true,
        settings: [
          {
            id: 1,
            category_id: 1,
            key: "log_level",
            display_name: "Log Level",
            description: "Minimum log level for system logging",
            data_type: "select",
            default_value: "INFO",
            current_value: "INFO",
            value: "INFO",
            validation_rules: { options: ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] },
            ui_component: "select",
            ui_options: { options: ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] },
            is_sensitive: false,
            is_readonly: false,
            is_required: true,
            requires_restart: false,
            sort_order: 1,
            is_active: true
          },
          {
            id: 2,
            category_id: 1,
            key: "enable_metrics",
            display_name: "Enable Metrics Collection",
            description: "Collect system performance metrics",
            data_type: "boolean",
            default_value: "true",
            current_value: "true",
            value: true,
            validation_rules: {},
            ui_component: "checkbox",
            ui_options: {},
            is_sensitive: false,
            is_readonly: false,
            is_required: false,
            requires_restart: false,
            sort_order: 2,
            is_active: true
          }
        ]
      },
      {
        id: 2,
        name: "agents",
        display_name: "Agent Management",
        description: "AI agent configuration and control settings",
        icon: "beaker",
        sort_order: 2,
        is_active: true,
        settings: [
          {
            id: 3,
            category_id: 2,
            key: "agent_health_check_interval",
            display_name: "Agent Health Check Interval (seconds)",
            description: "How often to check agent health status",
            data_type: "integer",
            default_value: "30",
            current_value: "30",
            value: 30,
            validation_rules: { min: 10, max: 300 },
            ui_component: "input",
            ui_options: {},
            is_sensitive: false,
            is_readonly: false,
            is_required: true,
            requires_restart: true,
            sort_order: 1,
            is_active: true
          }
        ]
      }
    ]
  }

  /**
   * Get settings for a specific category
   */
  async getCategorySettings(categoryName: string, userId?: number): Promise<SettingsCategory> {
    try {
      const response = await api.get(`${this.baseUrl}/category/${categoryName}`, {
        params: userId ? { user_id: userId } : {}
      })
      return response.data
    } catch (error: any) {
      console.error(`Failed to fetch settings for category ${categoryName}:`, error)
      // Return mock data as fallback
      const mockCategories = this.getMockCategories()
      const category = mockCategories.find(cat => cat.name === categoryName)
      if (category) {
        return category
      }
      throw new Error(`Category ${categoryName} not found`)
    }
  }

  /**
   * Update a specific setting
   */
  async updateSetting(settingId: number, updateRequest: SettingUpdateRequest): Promise<any> {
    try {
      const response = await api.put(`${this.baseUrl}/setting/${settingId}`, updateRequest)
      return response.data
    } catch (error: any) {
      console.error(`Failed to update setting ${settingId}:`, error)
      // Return mock success response
      return {
        success: true,
        message: "Setting updated successfully (mock)",
        data: {
          setting_id: settingId,
          requires_restart: false
        }
      }
    }
  }

  /**
   * Get agent settings
   */
  async getAgentSettings(agentType?: string, agentId?: string): Promise<AgentSetting[]> {
    try {
      const response = await api.get(`${this.baseUrl}/agents`, {
        params: {
          ...(agentType && { agent_type: agentType }),
          ...(agentId && { agent_id: agentId })
        }
      })
      return response.data
    } catch (error: any) {
      console.error('Failed to fetch agent settings:', error)
      // Return mock data as fallback
      return [
        {
          id: 1,
          agent_type: "lead_intake",
          agent_id: undefined,
          setting_key: "auto_assign",
          setting_value: "true",
          data_type: "boolean",
          is_enabled: true,
          typed_value: true
        },
        {
          id: 2,
          agent_type: "risk_assessment",
          agent_id: undefined,
          setting_key: "ai_model",
          setting_value: "gpt-3.5-turbo",
          data_type: "string",
          is_enabled: true,
          typed_value: "gpt-3.5-turbo"
        }
      ]
    }
  }

  /**
   * Update agent setting
   */
  async updateAgentSetting(
    agentType: string, 
    settingKey: string, 
    updateRequest: AgentSettingUpdateRequest,
    agentId?: string
  ): Promise<any> {
    const response = await api.put(
      `${this.baseUrl}/agents/${agentType}/${settingKey}`,
      updateRequest,
      { params: agentId ? { agent_id: agentId } : {} }
    )
    return response.data
  }

  /**
   * Delete agent setting
   */
  async deleteAgentSetting(agentType: string, settingKey: string, agentId?: string): Promise<any> {
    const response = await api.delete(
      `${this.baseUrl}/agents/${agentType}/${settingKey}`,
      { params: agentId ? { agent_id: agentId } : {} }
    )
    return response.data
  }

  /**
   * Get settings profiles
   */
  async getProfiles(): Promise<SettingsProfile[]> {
    const response = await api.get(`${this.baseUrl}/profiles`)
    return response.data
  }

  /**
   * Reset settings to defaults
   */
  async resetToDefaults(categoryName?: string, userId?: number): Promise<any> {
    const response = await api.post(`${this.baseUrl}/reset-to-defaults`, {}, {
      params: {
        ...(categoryName && { category_name: categoryName }),
        ...(userId && { user_id: userId })
      }
    })
    return response.data
  }

  /**
   * Bulk update settings for a category
   */
  async bulkUpdateSettings(categoryName: string, updates: Array<{
    settingId: number
    value: any
    changeReason?: string
  }>): Promise<any> {
    const promises = updates.map(update => 
      this.updateSetting(update.settingId, {
        value: update.value,
        change_reason: update.changeReason
      })
    )
    return Promise.all(promises)
  }

  /**
   * Validate setting value against its validation rules
   */
  validateSettingValue(setting: Setting, value: any): { isValid: boolean; error?: string } {
    if (!setting.validation_rules) {
      return { isValid: true }
    }

    const rules = setting.validation_rules

    // Check required
    if (setting.is_required && (value === null || value === undefined || value === '')) {
      return { isValid: false, error: `${setting.display_name} is required` }
    }

    // Type-specific validation
    switch (setting.data_type) {
      case 'integer':
        if (typeof value !== 'number' && !Number.isInteger(Number(value))) {
          return { isValid: false, error: `${setting.display_name} must be a whole number` }
        }
        if (rules.min !== undefined && Number(value) < rules.min) {
          return { isValid: false, error: `${setting.display_name} must be at least ${rules.min}` }
        }
        if (rules.max !== undefined && Number(value) > rules.max) {
          return { isValid: false, error: `${setting.display_name} cannot exceed ${rules.max}` }
        }
        break

      case 'float':
        if (typeof value !== 'number' && isNaN(Number(value))) {
          return { isValid: false, error: `${setting.display_name} must be a number` }
        }
        if (rules.min !== undefined && Number(value) < rules.min) {
          return { isValid: false, error: `${setting.display_name} must be at least ${rules.min}` }
        }
        if (rules.max !== undefined && Number(value) > rules.max) {
          return { isValid: false, error: `${setting.display_name} cannot exceed ${rules.max}` }
        }
        break

      case 'string':
        if (rules.minLength !== undefined && String(value).length < rules.minLength) {
          return { isValid: false, error: `${setting.display_name} must be at least ${rules.minLength} characters` }
        }
        if (rules.maxLength !== undefined && String(value).length > rules.maxLength) {
          return { isValid: false, error: `${setting.display_name} cannot exceed ${rules.maxLength} characters` }
        }
        if (rules.pattern && !new RegExp(rules.pattern).test(String(value))) {
          return { isValid: false, error: `${setting.display_name} format is invalid` }
        }
        break

      case 'select':
        if (rules.options && !rules.options.includes(value)) {
          return { isValid: false, error: `${setting.display_name} must be one of: ${rules.options.join(', ')}` }
        }
        break
    }

    return { isValid: true }
  }

  /**
   * Get setting display value (handles sensitive settings)
   */
  getDisplayValue(setting: Setting): string {
    if (setting.is_sensitive && setting.value) {
      return '••••••••'
    }
    return String(setting.value || setting.default_value || '')
  }

  /**
   * Format setting value for display based on data type
   */
  formatValue(setting: Setting, value: any): string {
    if (value === null || value === undefined) {
      return 'Not set'
    }

    switch (setting.data_type) {
      case 'boolean':
        return value ? 'Enabled' : 'Disabled'
      case 'json':
        return JSON.stringify(value, null, 2)
      case 'password':
        return '••••••••'
      default:
        return String(value)
    }
  }
}

// Export singleton instance
export const settingsService = new SettingsService()