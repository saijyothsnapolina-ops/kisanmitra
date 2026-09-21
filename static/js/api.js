/**
 * KisanMitra API Client
 * Clean abstraction layer for network requests to backend services.
 */

const API_BASE = '/api';

export const api = {
  /**
   * Fetch current farmer profile
   */
  async getProfile() {
    const res = await fetch(`${API_BASE}/profile`);
    if (!res.ok) {
      throw new Error(`Failed to load profile (${res.status})`);
    }
    return res.json();
  },

  /**
   * Save or update farmer profile
   */
  async saveProfile(profileData) {
    const res = await fetch(`${API_BASE}/profile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profileData)
    });
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to save profile');
    }
    return res.json();
  },

  /**
   * Reset profile to uncompleted state (for testing)
   */
  async resetProfile() {
    const res = await fetch(`${API_BASE}/profile/reset`, { method: 'POST' });
    if (!res.ok) {
      throw new Error('Failed to reset profile');
    }
    return res.json();
  },

  /**
   * Send user message to AI assistant
   */
  async sendChat({ message, image = null, action = null, profile = null, location = null, lang = 'en', conversation_id = null }) {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, image, action, profile, location, lang, conversation_id })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Assistant service is temporarily unavailable');
    }
    return res.json();
  },

  /**
   * Send user message to AI assistant with live streaming SSE response
   */
  async sendChatStream({ message, image = null, action = null, profile = null, location = null, lang = 'en', conversation_id = null, onChunk, onDone, onError }) {
    try {
      const res = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, image, action, profile, location, lang, conversation_id })
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Assistant streaming is temporarily unavailable');
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith('data:')) continue;
          const dataStr = trimmed.slice(5).trim();
          if (dataStr === '[DONE]') break;
          try {
            const parsed = JSON.parse(dataStr);
            if (parsed.done) {
              if (onDone) onDone(parsed);
            } else if (parsed.chunk && onChunk) {
              onChunk(parsed.chunk, parsed.conversation_id);
            }
          } catch (e) {
            // Keep parsing next lines
          }
        }
      }
    } catch (err) {
      if (onError) onError(err);
      else throw err;
    }
  },

  /**
   * Fetch mandi market benchmark rates
   */
  async getMarketPrices(crop = '', location = '', date = '', variety = '') {
    const params = new URLSearchParams();
    if (crop) params.append('crop', crop);
    if (location) params.append('location', location);
    if (date) params.append('date', date);
    if (variety) params.append('variety', variety);
    const queryString = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/market${queryString}`);
    if (!res.ok) {
      throw new Error('Failed to load market prices');
    }
    return res.json();
  },

  /**
   * Fetch latest available market prices (with today vs latest date handling)
   */
  async getLatestMarketPrices(crop = 'Chilli', variety = '', location = '') {
    const params = new URLSearchParams();
    if (crop) params.append('crop', crop);
    if (variety) params.append('variety', variety);
    if (location) params.append('location', location);
    const queryString = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/market/latest${queryString}`);
    if (!res.ok) throw new Error('Failed to load latest market prices');
    return res.json();
  },

  /**
   * Fetch market prices by specific date
   */
  async getMarketPricesByDate(crop = 'Chilli', date = 'Yesterday', variety = '', location = '') {
    return this.getMarketPrices(crop, location, date, variety);
  },

  /**
   * Fetch highest price market for crop and variety
   */
  async getHighestPriceMarket(crop = 'Chilli', variety = '', date = 'Yesterday') {
    const params = new URLSearchParams();
    if (crop) params.append('crop', crop);
    if (variety) params.append('variety', variety);
    if (date) params.append('date', date);
    const queryString = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/market/highest${queryString}`);
    if (!res.ok) throw new Error('Failed to load highest market price');
    return res.json();
  },

  /**
   * Compare market prices across compatible mandis
   */
  async compareMarketPrices(crop = 'Chilli', variety = '', date = 'Yesterday') {
    const params = new URLSearchParams();
    if (crop) params.append('crop', crop);
    if (variety) params.append('variety', variety);
    if (date) params.append('date', date);
    const queryString = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/market/compare${queryString}`);
    if (!res.ok) throw new Error('Failed to compare market prices');
    return res.json();
  },

  /**
   * Get market price spread
   */
  async getMarketPriceSpread(crop = 'Chilli', variety = '', date = 'Yesterday') {
    const params = new URLSearchParams();
    if (crop) params.append('crop', crop);
    if (variety) params.append('variety', variety);
    if (date) params.append('date', date);
    const queryString = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/market/spread${queryString}`);
    if (!res.ok) throw new Error('Failed to load market price spread');
    return res.json();
  },

  /**
   * Fetch market price history (7D, 30D, 3M, 1Y)
   */
  async getMarketPriceHistory(crop = 'Chilli', variety = '', range = '7D') {
    const params = new URLSearchParams();
    if (crop) params.append('crop', crop);
    if (variety) params.append('variety', variety);
    if (range) params.append('range', range);
    const queryString = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/market/history${queryString}`);
    if (!res.ok) throw new Error('Failed to load market price history');
    return res.json();
  },

  /**
   * Fetch weather forecast and agricultural advisory
   */
  async getWeather(location = '') {
    const query = location ? `?location=${encodeURIComponent(location)}` : '';
    const res = await fetch(`${API_BASE}/weather${query}`);
    if (!res.ok) {
      throw new Error('Failed to load weather data');
    }
    return res.json();
  },

  /**
   * Fetch crop health and stage advisories
   */
  async getCropAdvisories(crop = '') {
    const query = crop ? `?crop=${encodeURIComponent(crop)}` : '';
    const res = await fetch(`${API_BASE}/crops${query}`);
    if (!res.ok) {
      throw new Error('Failed to load crop advisories');
    }
    return res.json();
  },

  /**
   * Fetch local Wi-Fi and public HTTPS endpoints for mobile phone access
   */
  async getNetworkInfo() {
    const res = await fetch(`${API_BASE}/network-info`);
    if (!res.ok) {
      throw new Error('Failed to load network access information');
    }
    return res.json();
  },

  /**
   * Resolve GPS coordinates to district and nearest APMC mandi
   */
  async resolveLocation({ latitude, longitude, accuracy = null }) {
    const res = await fetch(`${API_BASE}/location/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ latitude, longitude, accuracy })
    });
    if (!res.ok) {
      throw new Error('Failed to resolve GPS coordinates');
    }
    return res.json();
  },

  /**
   * Fetch nearby APMC mandis ordered by road distance
   */
  async getNearbyMarkets(latitude, longitude, crop = 'Chilli', max_km = 150) {
    const params = new URLSearchParams({
      latitude: latitude.toString(),
      longitude: longitude.toString(),
      crop: crop || 'Chilli',
      max_km: max_km.toString()
    });
    const res = await fetch(`${API_BASE}/market/nearby?${params.toString()}`);
    if (!res.ok) {
      throw new Error('Failed to load nearby mandis');
    }
    return res.json();
  }
};

