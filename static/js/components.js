import { translations, cropTranslations } from './translations.js';


export function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export function formatTime(date = new Date()) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/**
 * User chat message
 */
export function createUserBubble(text, image = null) {
  const row = document.createElement('div');
  row.className = 'message-row user-row';

  let imageHtml = '';
  if (image) {
    imageHtml = `
      <div class="message-attachment">
        <img src="${image}" alt="Attached plant photo" class="attachment-preview">
      </div>
    `;
  }

  row.innerHTML = `
    <div class="message-bubble user-bubble">
      ${imageHtml}
      <div class="message-text">${escapeHtml(text)}</div>
      <div class="message-meta">${formatTime()}</div>
    </div>
  `;
  return row;
}

/**
 * Assistant chat response with farm context tag, suggestions, and audio replay
 */
export function createBotBubble(
  text,
  contextApplied = null,
  suggestedActions = [],
  onActionClick = null,
  spokenText = null,
  onReplayClick = null,
  currentLang = 'en'
) {
  const row = document.createElement('div');
  row.className = 'message-row bot-row';

  let contextHtml = '';
  if (contextApplied) {
    contextHtml = `
      <div class="farm-context-pill">
        <span class="context-icon">🌾</span>
        <span class="context-label">${escapeHtml(contextApplied.farmer || 'Farmer')} • ${escapeHtml(contextApplied.location || '')} • ${escapeHtml(contextApplied.crop || '')} (${escapeHtml(contextApplied.farm_size || '')})</span>
      </div>
    `;
  }

  let suggestionsContainer = null;
  if (suggestedActions && suggestedActions.length > 0) {
    suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'suggestions-container';

    suggestedActions.forEach(actionText => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'suggestion-chip';
      btn.textContent = actionText;
      if (onActionClick) {
        btn.addEventListener('click', () => onActionClick(actionText));
      }
      suggestionsContainer.appendChild(btn);
    });
  }

  const bubble = document.createElement('div');
  bubble.className = 'message-bubble bot-bubble';

  const t = translations[currentLang] || translations.en;
  const replayLabel = t.voiceReplay || 'Replay Audio';

  let voiceActionHtml = '';
  if (onReplayClick && (spokenText || text)) {
    voiceActionHtml = `
      <div class="msg-voice-action-wrap">
        <button type="button" class="msg-replay-btn" title="${escapeHtml(replayLabel)}">
          <span>🔊</span> <span>${escapeHtml(replayLabel)}</span>
        </button>
      </div>
    `;
  }

  bubble.innerHTML = `
    ${contextHtml}
    <div class="message-body">${formatMarkdown(text)}</div>
    <div class="message-meta">
      <span>${formatTime()}</span>
      ${voiceActionHtml}
    </div>
  `;

  if (suggestionsContainer) {
    bubble.insertBefore(suggestionsContainer, bubble.querySelector('.message-meta'));
  }

  const replayBtn = bubble.querySelector('.msg-replay-btn');
  if (replayBtn && onReplayClick) {
    replayBtn.addEventListener('click', () => {
      onReplayClick(spokenText || text, replayBtn);
    });
  }

  const avatar = document.createElement('div');
  avatar.className = 'bot-avatar-badge';
  avatar.innerHTML = '🌾';
  avatar.title = 'KisanMitra Companion';

  row.appendChild(avatar);
  row.appendChild(bubble);
  return row;
}

/**
 * Typing indicator
 */
export function createTypingIndicator() {
  const row = document.createElement('div');
  row.className = 'message-row bot-row typing-row';
  row.id = 'typing-indicator';
  row.innerHTML = `
    <div class="bot-avatar-badge" title="KisanMitra">🌾</div>
    <div class="message-bubble bot-bubble typing-bubble">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>
  `;
  return row;
}

/**
 * Interactive SVG Historical Price Chart
 * Clean grid, minimal labels, smooth curve, tooltip on hover (Date, Market, Price)
 */
export function renderPriceChart(historyPoints, container, marketName = 'APMC Benchmark') {
  if (!container || !historyPoints || historyPoints.length === 0) return;

  const width = container.clientWidth || (container.parentElement ? container.parentElement.clientWidth : 340) || 340;
  const height = 180;
  const padding = { top: 20, right: 20, bottom: 30, left: 45 };

  const prices = historyPoints.map(p => p.price);
  const minPrice = Math.min(...prices) * 0.96;
  const maxPrice = Math.max(...prices) * 1.04;
  const priceRange = maxPrice - minPrice || 1;

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  // Calculate coordinates
  const coords = historyPoints.map((pt, i) => {
    const x = padding.left + (i / (historyPoints.length - 1 || 1)) * plotWidth;
    const y = padding.top + plotHeight - ((pt.price - minPrice) / priceRange) * plotHeight;
    return { x, y, pt };
  });

  // SVG Path generator (smooth bezier)
  let pathD = `M ${coords[0].x},${coords[0].y}`;
  for (let i = 0; i < coords.length - 1; i++) {
    const p0 = coords[i];
    const p1 = coords[i + 1];
    const mx = (p0.x + p1.x) / 2;
    pathD += ` C ${mx},${p0.y} ${mx},${p1.y} ${p1.x},${p1.y}`;
  }

  // Gradient area path
  const areaD = `${pathD} L ${coords[coords.length - 1].x},${height - padding.bottom} L ${coords[0].x},${height - padding.bottom} Z`;

  // Grid lines & labels (3 horizontal levels)
  const gridLevels = [
    { label: `₹${Math.round(minPrice + priceRange * 0.2)}`, y: padding.top + plotHeight * 0.8 },
    { label: `₹${Math.round(minPrice + priceRange * 0.5)}`, y: padding.top + plotHeight * 0.5 },
    { label: `₹${Math.round(minPrice + priceRange * 0.8)}`, y: padding.top + plotHeight * 0.2 },
  ];

  let gridSvg = gridLevels.map(g => `
    <line x1="${padding.left}" y1="${g.y}" x2="${width - padding.right}" y2="${g.y}" stroke="var(--color-border)" stroke-dasharray="3,3" stroke-width="1" />
    <text x="${padding.left - 6}" y="${g.y + 4}" font-size="10" fill="var(--color-ink-subtle)" text-anchor="end">${g.label}</text>
  `).join('');

  // X-axis date labels
  const xLabelsSvg = coords.map((c, i) => {
    if (i === 0 || i === Math.floor(coords.length / 2) || i === coords.length - 1) {
      return `<text x="${c.x}" y="${height - 10}" font-size="10.5" fill="var(--color-ink-muted)" text-anchor="middle">${c.pt.date}</text>`;
    }
    return '';
  }).join('');

  // Interactive dots
  const dotsSvg = coords.map((c, i) => `
    <circle cx="${c.x}" cy="${c.y}" r="4.5" fill="var(--color-surface)" stroke="var(--color-forest)" stroke-width="2.5" class="chart-point" data-index="${i}" />
  `).join('');

  container.innerHTML = `
    <div class="chart-wrapper" style="position: relative;">
      <div class="chart-tooltip" id="chart-tooltip" style="display: none; position: absolute; background: var(--color-surface); border: 1px solid var(--color-border); padding: 6px 10px; border-radius: 6px; font-size: 11.5px; box-shadow: var(--shadow-md); pointer-events: none; z-index: 10; min-width: 130px;"></div>
      <svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}" style="overflow: visible;">
        <defs>
          <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="var(--color-forest)" stop-opacity="0.22" />
            <stop offset="100%" stop-color="var(--color-forest)" stop-opacity="0.0" />
          </linearGradient>
        </defs>
        ${gridSvg}
        <path d="${areaD}" fill="url(#chartGrad)" />
        <path d="${pathD}" fill="none" stroke="var(--color-forest)" stroke-width="2.5" stroke-linecap="round" />
        ${dotsSvg}
        ${xLabelsSvg}
      </svg>
    </div>
  `;

  // Attach tooltips displaying Date, Market, and Price
  const tooltip = container.querySelector('#chart-tooltip');
  const points = container.querySelectorAll('.chart-point');
  points.forEach(point => {
    point.addEventListener('mouseenter', () => {
      const idx = point.getAttribute('data-index');
      const dataPoint = coords[idx].pt;
      const mktName = dataPoint.market || marketName || 'APMC Benchmark';
      tooltip.style.display = 'block';
      tooltip.style.left = `${Math.max(10, Math.min(width - 145, coords[idx].x - 60))}px`;
      tooltip.style.top = `${Math.max(10, coords[idx].y - 58)}px`;
      tooltip.innerHTML = `
        <div style="font-weight:700; color:var(--color-forest); font-size:13px;">₹${dataPoint.price.toLocaleString('en-IN')}/q</div>
        <div style="font-size:11px; color:var(--color-ink-main); margin: 2px 0;">📍 ${escapeHtml(mktName)}</div>
        <div style="font-size:10px; color:var(--color-ink-muted);">📅 ${escapeHtml(dataPoint.date)}</div>
      `;
    });
    point.addEventListener('mouseleave', () => {
      tooltip.style.display = 'none';
    });
  });
}

/**
/**
 * Render Horizontal Bar Chart for Market Price Comparison
 * STRICTLY SORTED FROM HIGHEST PRICE TO LOWEST PRICE.
 */
export function renderHorizontalBarChart(items, container, varietyLabel = '', currentLang = 'en') {
  const t = translations[currentLang] || translations.en;
  if (!container) return;
  if (!items || items.length === 0) {
    container.innerHTML = `<div class="chart-empty-state" style="padding:16px; text-align:center; color:var(--color-ink-muted);">${t.noMarketsFound}</div>`;
    return;
  }

  // Strictly sort descending by modal_price
  const sorted = [...items].sort((a, b) => (b.modal_price || 0) - (a.modal_price || 0));
  const maxPrice = Math.max(...sorted.map(s => s.modal_price || 1));

  const rowsHtml = sorted.map((item, idx) => {
    const pct = Math.max(20, Math.min(100, Math.round(((item.modal_price || 0) / maxPrice) * 100)));
    const rankBadge = idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${idx + 1}`;
    const isTop = idx === 0;
    const vTag = item.variety || varietyLabel || '';

    return `
      <div class="hbar-item ${isTop ? 'hbar-top-ranked' : ''}">
        <div class="hbar-meta-row">
          <div class="hbar-market-identity">
            <span class="hbar-rank-badge ${isTop ? 'gold' : ''}">${rankBadge}</span>
            <span class="hbar-market-name">${escapeHtml(item.market)}</span>
            <span class="hbar-district-name">(${escapeHtml(item.district || '')})</span>
            ${vTag ? `<span class="hbar-variety-tag">${escapeHtml(vTag)}</span>` : ''}
          </div>
          <div class="hbar-price-col">
            <strong class="hbar-price-val">₹${(item.modal_price || 0).toLocaleString('en-IN')}<span class="hbar-unit">${t.quintalShort}</span></strong>
          </div>
        </div>
        <div class="hbar-track-wrap">
          <div class="hbar-track">
            <div class="hbar-fill ${isTop ? 'hbar-fill-highest' : ''}" style="width: ${pct}%;">
              <span class="hbar-fill-label">₹${(item.modal_price || 0).toLocaleString('en-IN')}</span>
            </div>
          </div>
        </div>
        <div class="hbar-sub-row">
          <span class="hbar-sub-info">${t.rangeTag} ₹${(item.min_price || item.modal_price).toLocaleString('en-IN')} – ₹${(item.max_price || item.modal_price).toLocaleString('en-IN')}</span>
          <span class="hbar-sub-arrivals">${t.arrivalsTag} ${escapeHtml(item.arrivals || '—')}</span>
        </div>
      </div>
    `;
  }).join('');

  container.innerHTML = `
    <div class="horizontal-bar-chart-card">
      <div class="hbar-list">
        ${rowsHtml}
      </div>
    </div>
  `;
}


/**
 * Render Complete Market Intelligence Page
 * Implements the exact 9 sections in order:
 * 1. Market header
 * 2. Crop selector + Date selector + Variety dropdown (Chilli variety aware) + Compare Varieties toggle
 * 3. Current/latest price summary card (CHILLI — 341 aware)
 * 4. Yesterday's market ranking (HIGHEST REPORTED PRICE highlight + copy + ranked list with explicit variety labeling)
 * 5. Price difference between markets (Spread cards)
 * 6. Price history graph (SVG line chart filtered to specific variety)
 * 7. Yesterday price graph (Horizontal bar chart strictly sorted highest -> lowest)
 * 8. Market-by-market detailed table (sortable + variety tags)
 * 9. Clear source/date information
 */
export function renderMarketPage(...args) {
  let opts = {};
  if (args.length === 1 && typeof args[0] === 'object' && args[0].container) {
    opts = args[0];
  } else {
    opts = {
      marketPayload: args[0],
      container: args[1],
      currentCrop: args[2],
      currentRange: args[3],
      onSelectCrop: args[4],
      onSelectRange: args[5],
      onSelectDate: args[6],
      onSelectVariety: args[7],
      onSearch: args[8],
      onSort: args[9]
    };
  }

  const {
    marketPayload,
    container,
    currentCrop = 'Tomato',
    currentRange = '7D',
    currentDate = 'Yesterday',
    currentVariety = 'all',
    currentLang = 'en',
    searchQuery = '',
    sortCol = 'modal_price',
    sortDir = 'desc',
    showVarietyCompare = false,
    onToggleVarietyCompare,
    onSelectCrop,
    onSelectRange,
    onSelectDate,
    onSelectVariety,
    onSearch,
    onSort
  } = opts;

  if (!container) return;
  const t = translations[currentLang] || translations.en;
  const cropNames = cropTranslations[currentLang] || cropTranslations.en;
  const payload = marketPayload || {};
  const crop = currentCrop || payload.crop || 'Tomato';
  const isChilli = crop.toLowerCase() === 'chilli' || crop.toLowerCase() === 'mirchi';
  const localizedCropName = cropNames[crop] || crop;
  const range = currentRange || '7D';
  const dateSelected = currentDate || payload.date_selected || 'Yesterday';
  const localizedDateSelected = dateSelected === 'Yesterday' ? t.dateYesterday : (dateSelected === 'Today' ? t.dateToday : (dateSelected === 'Last 7 Days' ? t.dateLast7Days : dateSelected));
  const variety = currentVariety || payload.variety_selected || 'all';
  const isSpecificVariety = variety && variety.toLowerCase() !== 'all' && variety.toLowerCase() !== 'all chilli' && variety.toLowerCase() !== 'all varieties';

  // Available crops list
  const availableCrops = [
    { name: 'Tomato', icon: '🍅' },
    { name: 'Chilli', icon: '🌶️' },
    { name: 'Cotton', icon: '☁️' },
    { name: 'Paddy', icon: '🌾' },
    { name: 'Onion', icon: '🧅' },
    { name: 'Maize', icon: '🌽' },
    { name: 'Groundnut', icon: '🥜' }
  ];

  // Available varieties supported by available data
  const varietyList = payload.varieties && payload.varieties.length > 0
    ? payload.varieties
    : (isChilli ? ['341', 'Teja', 'Wonder Hot', 'Byadgi', 'Guntur Sannam', 'Dry Chilli', 'Local / Other'] : []);

  // Records directly from backend payload (already filtered & sorted modal_price desc)
  let rankedRecords = Array.isArray(payload.data) ? [...payload.data] : [];

  // Zero fabrication rule: check if specific variety has no records
  const isVarietyUnavailable = Boolean(payload.variety_unavailable) || (isSpecificVariety && rankedRecords.length === 0);
  const hasRecords = rankedRecords.length > 0 && !isVarietyUnavailable;

  const highestItem = hasRecords ? rankedRecords[0] : null;
  const lowestItem = hasRecords ? rankedRecords[rankedRecords.length - 1] : null;
  const primaryItem = hasRecords ? (rankedRecords.find(m => m.market && m.market.toLowerCase().includes('guntur')) || rankedRecords[0]) : null;

  const spreadData = (payload.spread && payload.spread.highest_price) ? payload.spread : (hasRecords ? {
    highest_price: highestItem.modal_price,
    highest_market: highestItem.market,
    highest_district: highestItem.district,
    lowest_price: lowestItem.modal_price,
    lowest_market: lowestItem.market,
    lowest_district: lowestItem.district,
    difference: highestItem.modal_price - lowestItem.modal_price,
    percentage_difference: lowestItem.modal_price ? (((highestItem.modal_price - lowestItem.modal_price) / lowestItem.modal_price) * 100).toFixed(2) : 0
  } : {
    highest_price: 0,
    highest_market: null,
    highest_district: null,
    lowest_price: 0,
    lowest_market: null,
    lowest_district: null,
    difference: 0,
    percentage_difference: 0
  });

  // Display Title (e.g. "టమోటా" or "మిర్చి — 341")
  const displayTitle = payload.display_title || (isSpecificVariety ? `${localizedCropName.toUpperCase()} — ${variety.toUpperCase()}` : `${localizedCropName.toUpperCase()}`);

  // Filtered records for Table (search query)
  let tableRecords = [...rankedRecords];
  if (searchQuery && searchQuery.trim()) {
    const q = searchQuery.trim().toLowerCase();
    tableRecords = tableRecords.filter(m =>
      (m.market && m.market.toLowerCase().includes(q)) ||
      (m.district && m.district.toLowerCase().includes(q)) ||
      (m.variety && m.variety.toLowerCase().includes(q))
    );
  }

  // Sort records for table
  const sortedTableRecords = [...tableRecords].sort((a, b) => {
    let valA = a[sortCol];
    let valB = b[sortCol];
    if (valA === undefined || valA === null) valA = '';
    if (valB === undefined || valB === null) valB = '';
    if (typeof valA === 'string') valA = valA.toLowerCase();
    if (typeof valB === 'string') valB = valB.toLowerCase();
    if (valA < valB) return sortDir === 'asc' ? -1 : 1;
    if (valA > valB) return sortDir === 'asc' ? 1 : -1;
    return 0;
  });

  // Historical data for Section 6 (variety specific)
  const historyData = payload.history ? (payload.history[range] || payload.history['7D']) : [];

  // Helper for sort indicators
  const getSortIndicator = (col) => {
    if (sortCol !== col) return '<span class="sort-icon inactive">⇅</span>';
    return sortDir === 'asc' ? '<span class="sort-icon active">▲</span>' : '<span class="sort-icon active">▼</span>';
  };

  container.innerHTML = `
    <!-- ============================================== -->
    <!-- 1. MARKET HEADER                               -->
    <!-- ============================================== -->
    <div class="market-page-header">
      <div class="market-header-titles">
        <h2 class="market-title">${t.marketHeaderTitle}</h2>
        <p class="market-subtitle">${t.marketHeaderSub}</p>
      </div>
      <div class="market-header-badges">
        <span class="mandi-source-pill">${t.sourcePill}</span>
        <span class="mandi-freshness-pill">${t.freshnessPill}</span>
      </div>
    </div>

    <!-- ============================================== -->
    <!-- 2. COMPACT CONTROLS BAR                        -->
    <!-- ============================================== -->
    <div class="market-controls-card">
      <!-- Crop selector pills -->
      <div class="market-crop-bar">
        <div class="crop-pill-chips">
          ${availableCrops.map(c => `
            <button type="button" class="crop-select-pill ${c.name.toLowerCase() === crop.toLowerCase() ? 'active' : ''}" data-crop="${c.name}">
              ${c.icon} ${cropNames[c.name] || c.name}
            </button>
          `).join('')}
        </div>
      </div>

      <!-- Second controls row: Search, Date Selector, Variety Dropdown, and Compare Button -->
      <div class="market-filters-row">
        <div class="search-input-wrapper" id="search-input-wrapper">
          <span class="search-icon">🔍</span>
          <input 
            type="search" 
            class="market-search-input" 
            placeholder="${t.searchPlaceholder}" 
            value="${escapeHtml(searchQuery)}"
            id="market-search-input"
            aria-label="Search markets"
            autocomplete="off"
          >
          <button type="button" class="search-clear-btn" id="market-search-clear" title="Clear search" style="${searchQuery ? 'display:flex;' : 'display:none;'}">✕</button>
        </div>

        <div class="market-date-toggle-group">
          <span class="filter-label-inline">${t.dateLabel}</span>
          <div class="date-toggle-pills">
            <button type="button" class="date-pill ${dateSelected === 'Yesterday' ? 'active' : ''}" data-date="Yesterday">${t.dateYesterday}</button>
            <button type="button" class="date-pill ${dateSelected === 'Today' ? 'active' : ''}" data-date="Today">${t.dateToday}</button>
            <button type="button" class="date-pill ${dateSelected === 'Last 7 Days' ? 'active' : ''}" data-date="Last 7 Days">${t.dateLast7Days}</button>
          </div>
        </div>

        <div class="market-variety-wrapper">
          <span class="filter-label-inline">${isChilli ? t.chilliVarietyLabel : `${escapeHtml(localizedCropName)} ${t.varietyFilterLabel}`}</span>
          <select class="market-variety-select" id="market-variety-select" aria-label="Select variety">
            <option value="all" ${(!isSpecificVariety) ? 'selected' : ''}>${isChilli ? t.allChilli : t.allVarieties}</option>
            ${varietyList.map(v => `
              <option value="${escapeHtml(v)}" ${isSpecificVariety && variety.toLowerCase() === v.toLowerCase() ? 'selected' : ''}>${escapeHtml(v)}</option>
            `).join('')}
          </select>
        </div>

        ${isChilli ? `
          <button type="button" class="variety-compare-toggle-btn ${showVarietyCompare ? 'active' : ''}" id="toggle-variety-compare-btn" title="${t.compareChilliBtn}">
            ${showVarietyCompare ? t.hideComparisonBtn : t.compareChilliBtn}
          </button>
        ` : ''}
      </div>
    </div>

    <!-- ============================================== -->
    <!-- OPTIONAL: SIDE-BY-SIDE VARIETY COMPARISON      -->
    <!-- ============================================== -->
    ${(isChilli && showVarietyCompare && payload.varieties_comparison && payload.varieties_comparison.length > 0) ? `
      <div class="market-card-block variety-comparison-panel" id="variety-comparison-panel">
        <div class="block-title-row">
          <div>
            <h3 class="block-title">${t.compareTitleChilli} ${escapeHtml(localizedDateSelected)}</h3>
            <p class="block-subtitle">${t.compareSubChilli}</p>
          </div>
        </div>
        <div class="variety-compare-grid">
          ${payload.varieties_comparison.map(vc => {
            const isCardActive = isSpecificVariety && variety.toLowerCase() === vc.variety.toLowerCase();
            return `
              <div class="variety-compare-card ${isCardActive ? 'active-variety-card' : ''}">
                <div class="vcard-top">
                  <span class="vcard-tag">${escapeHtml(vc.variety)}</span>
                  ${isCardActive ? '<span class="vcard-badge">Selected</span>' : ''}
                </div>
                <div class="vcard-price">
                  <span class="vcard-num">₹${(vc.modal_price || 0).toLocaleString('en-IN')}</span>
                  <span class="vcard-unit">${t.quintalShort}</span>
                </div>
                <div class="vcard-mkt">📍 <strong>${escapeHtml(vc.market)}</strong></div>
                <div class="vcard-sub">${escapeHtml(vc.district || '')} • ${t.arrivalsTag} ${escapeHtml(vc.arrivals || '—')}</div>
                <div class="vcard-range">${t.rangeTag} ₹${(vc.min_price || vc.modal_price).toLocaleString('en-IN')} – ₹${(vc.max_price || vc.modal_price).toLocaleString('en-IN')}</div>
                <div class="vcard-date">📅 ${escapeHtml(vc.date || localizedDateSelected)}</div>
                <button type="button" class="btn-select-variety ${isCardActive ? 'selected' : ''}" data-variety="${escapeHtml(vc.variety)}">
                  ${isCardActive ? t.btnViewingVariety + ' ' + escapeHtml(vc.variety) : t.btnSelectVariety + ' ' + escapeHtml(vc.variety) + ' →'}
                </button>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    ` : ''}

    <!-- ZERO FABRICATION BANNER (IF VARIETY UNAVAILABLE) -->
    ${(!hasRecords) ? `
      <div class="market-card-block variety-unavailable-card">
        <div class="unavailable-icon">⚠️</div>
        <div class="unavailable-details">
          <h3 class="unavailable-title">${isSpecificVariety ? escapeHtml(variety) : localizedCropName} ${t.dataNotAvailable}</h3>
          <p class="unavailable-copy">“${isSpecificVariety ? escapeHtml(variety) + (isChilli ? ' chilli' : '') : localizedCropName} ${t.varietyUnavailableNotice}”</p>
          <p class="unavailable-sub">${t.zeroFabDisclaimer} <strong>${isChilli ? t.allChilli : t.allVarieties}</strong>.</p>
        </div>
      </div>
    ` : `
      <!-- ============================================== -->
      <!-- 3. TODAY'S / LATEST MIRCHI PRICE EXPERIENCE   -->
      <!-- ============================================== -->
      <div class="market-hero-card">
        ${(dateSelected.toLowerCase() === 'today' && primaryItem.date_label && primaryItem.date_label.toLowerCase() !== 'today') ? `
          <div class="today-pending-notice-banner">
            <span class="notice-icon">ℹ️</span>
            <span class="notice-text"><strong>${t.latestAvailableNotice} — ${escapeHtml(primaryItem.date)}</strong> (${t.todayNotPublishedNotice})</span>
          </div>
        ` : ''}
        <div class="market-hero-header">
          <div>
            <div class="hero-crop-badge">
              <span class="hero-crop-name">${escapeHtml(displayTitle)}</span>
              <span class="hero-variety-tag">${escapeHtml(primaryItem.variety || (isSpecificVariety ? variety : t.allVarieties))}</span>
              <span class="hero-date-badge">${primaryItem.date_label === 'Today' ? t.dateToday : `${t.latestAvailablePriceTag}: ${escapeHtml(primaryItem.date || localizedDateSelected)}`}</span>
            </div>
            <div class="hero-price-line">
              <div class="hero-modal-block">
                <span class="hero-price-label">${t.modalPriceLabel}</span>
                <div class="hero-price-val-wrap">
                  <span class="hero-price-val">₹${(primaryItem.modal_price || 0).toLocaleString('en-IN')}</span>
                  <span class="hero-price-unit">${t.quintalUnit}</span>
                </div>
              </div>
            </div>

            <!-- Clearly Distinguish Min, Modal, Max Prices & Arrivals -->
            <div class="hero-price-subgrid">
              <div class="subgrid-col">
                <span class="subgrid-label">${t.minPriceLabel}</span>
                <span class="subgrid-val">₹${(primaryItem.min_price || primaryItem.modal_price).toLocaleString('en-IN')}<small>${t.quintalShort}</small></span>
              </div>
              <div class="subgrid-col">
                <span class="subgrid-label">${t.modalPriceLabel}</span>
                <span class="subgrid-val highlight-modal">₹${(primaryItem.modal_price || 0).toLocaleString('en-IN')}<small>${t.quintalShort}</small></span>
              </div>
              <div class="subgrid-col">
                <span class="subgrid-label">${t.maxPriceLabel}</span>
                <span class="subgrid-val">₹${(primaryItem.max_price || primaryItem.modal_price).toLocaleString('en-IN')}<small>${t.quintalShort}</small></span>
              </div>
              <div class="subgrid-col">
                <span class="subgrid-label">${t.arrivalsTag}</span>
                <span class="subgrid-val">${escapeHtml(primaryItem.arrivals || '—')}</span>
              </div>
            </div>

            <div class="hero-meta-line">
              <span>📍 <strong>${escapeHtml(primaryItem.market)}</strong> (${escapeHtml(primaryItem.district || 'AP')}, ${escapeHtml(primaryItem.state || 'Andhra Pradesh')})</span>
              <span class="meta-dot">•</span>
              <span>📅 ${t.reportingDateLabel}: <strong>${escapeHtml(primaryItem.date || localizedDateSelected)}</strong></span>
              <span class="meta-dot">•</span>
              <span>🕒 ${t.updatedLabel}: <strong>${escapeHtml(primaryItem.updated || 'Daily APMC Close')}</strong></span>
            </div>
            <div class="hero-source-row">
              <span class="source-caption">📜 ${escapeHtml(primaryItem.source || t.sourceHeroLabel)}</span>
            </div>
          </div>

          <div class="hero-right-col">
            <div class="hero-change-badge ${primaryItem.trend === 'down' ? 'negative' : (primaryItem.trend === 'steady' ? 'steady' : 'positive')}">
              <span class="change-amount">${escapeHtml(primaryItem.change || '+₹300')}</span>
              <span class="change-percent">${escapeHtml(primaryItem.change_pct || '+1.5%')}</span>
              <span class="change-prev">${t.vsPrevReport}</span>
            </div>
            <span class="freshness-badge-pill">${t.freshnessPill}</span>
          </div>
        </div>
      </div>

      <!-- ============================================== -->
      <!-- 4. YESTERDAY'S MARKET RANKING                  -->
      <!-- ============================================== -->
      <div class="market-card-block ranking-block">
        <div class="block-title-row">
          <div>
            <h3 class="block-title">${escapeHtml(localizedDateSelected)} — ${localizedCropName}${isSpecificVariety ? ' ' + escapeHtml(variety) + ' ' : ' '}${t.pricesHeader}</h3>
            <p class="block-subtitle">${t.rankingSubTitle} ${localizedCropName}${isSpecificVariety ? ' (' + escapeHtml(variety) + ')' : ''}</p>
          </div>
        </div>

        <!-- Prominent Highlight at top: HIGHEST REPORTED PRICE -->
        <div class="highest-price-highlight-card">
          <div class="highlight-badge-row">
            <span class="highest-price-badge">${t.highestReportedBadge}${isSpecificVariety ? ' — ' + escapeHtml(variety.toUpperCase()) : ''}</span>
            <span class="highlight-date-badge">${escapeHtml(highestItem.date_label || localizedDateSelected)} (${escapeHtml(highestItem.date || '')})</span>
          </div>
          <div class="highlight-main-row">
            <div class="highlight-identity">
              <h4 class="highlight-market-title">${escapeHtml(highestItem.market)}</h4>
              <div class="highlight-district">${escapeHtml(highestItem.district || '')} District, ${escapeHtml(highestItem.state || 'Andhra Pradesh')}</div>
              <div class="highlight-variety-sub">${t.varietyTag} <strong class="highlight-variety-chip">${escapeHtml(highestItem.variety || variety)}</strong> • ${t.arrivalsTag} <strong>${escapeHtml(highestItem.arrivals || '—')}</strong></div>
            </div>
            <div class="highlight-price-wrap">
              <div class="highlight-price-num">₹${(highestItem.modal_price || 0).toLocaleString('en-IN')}<span class="highlight-unit">${t.quintalShort}</span></div>
              <div class="highlight-range-caption">${t.rangeTag} ₹${(highestItem.min_price || highestItem.modal_price).toLocaleString('en-IN')} – ₹${(highestItem.max_price || highestItem.modal_price).toLocaleString('en-IN')}</div>
            </div>
          </div>

          <!-- Mandatory Copy & Disclaimer -->
          <div class="mandatory-ranking-copy">
            <p class="reported-price-statement">${t.highestStatement}</p>
            <p class="market-ranking-disclaimer">${t.rankingDisclaimer}</p>
          </div>
        </div>

        <!-- Ranked List of Markets -->
        <div class="ranked-markets-container">
          <div class="ranked-list-title">${t.allReportingMandis} (${rankedRecords.length}) — ${t.strictlySortedModal}</div>
          <div class="ranked-market-list">
            ${rankedRecords.map((m, idx) => {
              const rankIcon = idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `${idx + 1}`;
              const isFirst = idx === 0;
              return `
                <div class="ranked-market-item ${isFirst ? 'is-top-rank' : ''}">
                  <div class="ranked-rank-num ${isFirst ? 'medal-gold' : ''}">${rankIcon}</div>
                  <div class="ranked-market-detail">
                    <div class="ranked-mkt-name">
                      <strong>${escapeHtml(m.market)}</strong>
                      <span class="ranked-mkt-district">${escapeHtml(m.district)}</span>
                      <span class="ranked-variety-pill">${escapeHtml(m.variety || variety)}</span>
                    </div>
                    <div class="ranked-mkt-sub">${t.varietyTag} <strong>${escapeHtml(m.variety || variety)}</strong> • ${t.arrivalsTag} ${escapeHtml(m.arrivals || '—')}</div>
                  </div>
                  <div class="ranked-rate-col">
                    <div class="ranked-rate-val">₹${(m.modal_price || 0).toLocaleString('en-IN')}<small>${t.quintalShort}</small></div>
                    <div class="ranked-trend-indicator ${m.trend === 'up' ? 'rising' : (m.trend === 'down' ? 'falling' : 'steady')}">
                      ${m.trend === 'up' ? '▲ ' + (m.change || '+₹300') : (m.trend === 'down' ? '▼ ' + (m.change || '-₹100') : '● ' + (m.change || '₹0'))}
                    </div>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      </div>

      <!-- ============================================== -->
      <!-- 5. PRICE DIFFERENCE BETWEEN MARKETS (SPREAD)   -->
      <!-- ============================================== -->
      <div class="market-card-block spread-block">
        <div class="block-title-row">
          <div>
            <h3 class="block-title">${t.spreadTitle}</h3>
            <p class="block-subtitle">${t.spreadSub} ${localizedCropName}${isSpecificVariety ? ' (' + escapeHtml(variety) + ')' : ''}</p>
          </div>
        </div>

        <div class="market-spread-grid">
          <div class="spread-stat-card highest-card">
            <div class="stat-label">${t.highestReported}</div>
            <div class="stat-value text-forest">₹${(spreadData.highest_price || 0).toLocaleString('en-IN')}<span class="stat-unit">${t.quintalShort}</span></div>
            <div class="stat-mkt-name">📍 ${escapeHtml(spreadData.highest_market || '')}</div>
            <div class="stat-sub">${escapeHtml(spreadData.highest_district || '')} District</div>
          </div>

          <div class="spread-stat-card lowest-card">
            <div class="stat-label">${t.lowestReported}</div>
            <div class="stat-value text-ink">₹${(spreadData.lowest_price || 0).toLocaleString('en-IN')}<span class="stat-unit">${t.quintalShort}</span></div>
            <div class="stat-mkt-name">📍 ${escapeHtml(spreadData.lowest_market || '')}</div>
            <div class="stat-sub">${escapeHtml(spreadData.lowest_district || '')} District</div>
          </div>

          <div class="spread-stat-card diff-card">
            <div class="stat-label">${t.marketPriceDiff}</div>
            <div class="stat-value text-amber">₹${(spreadData.difference || 0).toLocaleString('en-IN')}<span class="stat-unit">${t.quintalShort}</span></div>
            <div class="stat-mkt-name">${t.spreadBetweenYards}</div>
            <div class="stat-sub">${t.spreadVariation}</div>
          </div>

          <div class="spread-stat-card pct-card">
            <div class="stat-label">${t.spreadPercentage}</div>
            <div class="stat-value text-forest">+${spreadData.percentage_difference || 0}%</div>
            <div class="stat-mkt-name">${t.spreadPremium}</div>
            <div class="stat-sub">${t.spreadTransport}</div>
          </div>
        </div>

        <div class="spread-note-footer">
          ℹ️ ${t.spreadNoteFooter}
        </div>
      </div>

      <!-- ============================================== -->
      <!-- 6. PRICE HISTORY GRAPH                         -->
      <!-- ============================================== -->
      <div class="market-card-block chart-block">
        <div class="block-title-row">
          <div>
            <h3 class="block-title">${isSpecificVariety ? escapeHtml(variety) : localizedCropName} ${t.priceTrendTitle}</h3>
            <p class="block-subtitle">${t.historicalBenchmarkSub}</p>
          </div>
          <div class="chart-range-selector">
            <button type="button" class="range-btn ${range === '7D' ? 'active' : ''}" data-range="7D">7D</button>
            <button type="button" class="range-btn ${range === '30D' ? 'active' : ''}" data-range="30D">30D</button>
            <button type="button" class="range-btn ${range === '3M' ? 'active' : ''}" data-range="3M">3M</button>
            <button type="button" class="range-btn ${range === '1Y' ? 'active' : ''}" data-range="1Y">1Y</button>
          </div>
        </div>
        <div id="price-history-chart-mount" style="margin-top: 10px;"></div>
      </div>

      <!-- ============================================== -->
      <!-- 7. YESTERDAY PRICE GRAPH (HORIZONTAL BAR)      -->
      <!-- ============================================== -->
      <div class="market-card-block horizontal-chart-block">
        <div class="block-title-row">
          <div>
            <h3 class="block-title">${escapeHtml(localizedDateSelected)} — ${localizedCropName}${isSpecificVariety ? ' ' + escapeHtml(variety) : ''} ${t.pricesByMarketTitle}</h3>
            <p class="block-subtitle">${t.horizontalSub}</p>
          </div>
        </div>
        <div id="market-horizontal-bar-mount"></div>
      </div>

      <!-- ============================================== -->
      <!-- 8. MARKET-BY-MARKET DETAILED TABLE             -->
      <!-- ============================================== -->
      <div class="market-card-block table-block">
        <div class="block-title-row">
          <div>
            <h3 class="block-title">${t.tableTitle} ${localizedCropName}${isSpecificVariety ? ' — ' + escapeHtml(variety) : ''} (${escapeHtml(localizedDateSelected)})</h3>
            <p class="block-subtitle" id="market-table-count">${sortedTableRecords.length} ${t.showingMandiYards}</p>
          </div>
        </div>

        <div class="table-wrapper">
          <table class="standard-table market-interactive-table">
            <thead>
              <tr>
                <th class="sortable-th" data-sort="rank">${t.thRank} ${getSortIndicator('rank')}</th>
                <th class="sortable-th" data-sort="market">${t.thMarket} ${getSortIndicator('market')}</th>
                <th class="sortable-th" data-sort="district">${t.thDistrict} ${getSortIndicator('district')}</th>
                <th class="sortable-th" data-sort="crop">${t.thCrop} ${getSortIndicator('crop')}</th>
                <th class="sortable-th" data-sort="variety">${t.thVariety} ${getSortIndicator('variety')}</th>
                <th class="sortable-th" data-sort="min_price">${t.thMinPrice} ${getSortIndicator('min_price')}</th>
                <th class="sortable-th" data-sort="max_price">${t.thMaxPrice} ${getSortIndicator('max_price')}</th>
                <th class="sortable-th" data-sort="modal_price">${t.thModalPrice} ${getSortIndicator('modal_price')}</th>
                <th class="sortable-th" data-sort="arrivals">${t.thArrivals} ${getSortIndicator('arrivals')}</th>
                <th class="sortable-th" data-sort="date">${t.thDate} ${getSortIndicator('date')}</th>
              </tr>
            </thead>
            <tbody id="market-table-body">
              ${sortedTableRecords.length === 0 ? `
                <tr class="no-search-results-row">
                  <td colspan="10" style="text-align:center; padding:24px; color:var(--color-ink-muted);">
                    ${t.noMarketsFound}
                  </td>
                </tr>
              ` : sortedTableRecords.map((it, idx) => {
                const rankIdx = it.rank || (rankedRecords.findIndex(r => r.market === it.market) + 1);
                const isTop = rankIdx === 1;
                const searchMetadata = `${it.market || ''} ${it.district || ''} ${it.crop || ''} ${it.variety || ''}`.toLowerCase();
                return `
                  <tr class="${isTop ? 'table-row-top' : ''}" data-market-row="true" data-search-text="${escapeHtml(searchMetadata)}">
                    <td data-label="${t.thRank}"><span class="table-rank-badge ${isTop ? 'gold' : ''}">${rankIdx || idx + 1}</span></td>
                    <td data-label="${t.thMarket}"><strong>${escapeHtml(it.market)}</strong></td>
                    <td data-label="${t.thDistrict}">${escapeHtml(it.district || '—')}</td>
                    <td data-label="${t.thCrop}">${escapeHtml(cropNames[it.crop] || it.crop)}</td>
                    <td data-label="${t.thVariety}"><span class="variety-chip-mini">${escapeHtml(it.variety || variety)}</span></td>
                    <td data-label="${t.thMinPrice}">₹${(it.min_price || 0).toLocaleString('en-IN')}</td>
                    <td data-label="${t.thMaxPrice}">₹${(it.max_price || 0).toLocaleString('en-IN')}</td>
                    <td data-label="${t.thModalPrice}" class="table-modal-price"><strong>₹${(it.modal_price || 0).toLocaleString('en-IN')}</strong>${t.quintalShort}</td>
                    <td data-label="${t.thArrivals}">${escapeHtml(it.arrivals || '—')}</td>
                    <td data-label="${t.thDate}"><small style="color:var(--color-ink-muted);">${escapeHtml(it.date || localizedDateSelected)}</small></td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `}

    <!-- ============================================== -->
    <!-- 9. CLEAR SOURCE / DATE INFORMATION             -->
    <!-- ============================================== -->
    <div class="market-card-block source-info-block">
      <div class="source-info-header">
        <span class="source-icon">🏛️</span>
        <div>
          <h4 class="source-info-title">${t.sourceBlockTitle}</h4>
          <p class="source-info-sub">${t.sourceBlockSub}</p>
        </div>
      </div>
      <div class="source-info-body">
        <div class="source-meta-grid">
          <div class="source-meta-item">
            <span class="source-meta-label">${t.primarySourceLabel}</span>
            <strong class="source-meta-val">Agmarknet APMC Daily Report (Demo)</strong>
          </div>
          <div class="source-meta-item">
            <span class="source-meta-label">${t.reportDateLabel}</span>
            <strong class="source-meta-val">${escapeHtml((highestItem && highestItem.date) || '22 Sep 2026')}</strong>
          </div>
          <div class="source-meta-item">
            <span class="source-meta-label">${t.lastSyncLabel}</span>
            <strong class="source-meta-val">${t.syncTimeVal}</strong>
          </div>
          <div class="source-meta-item">
            <span class="source-meta-label">${t.benchmarkVerificationLabel}</span>
            <span class="freshness-tag-inline">${t.freshnessPill}</span>
          </div>
        </div>
        <p class="source-info-disclaimer">
          ${t.sourceLongDisclaimer}
        </p>
      </div>
    </div>
  `;

  if (hasRecords) {
    // Mount Section 6: SVG Price History Line Chart
    const lineChartMount = container.querySelector('#price-history-chart-mount');
    if (lineChartMount) {
      renderPriceChart(historyData, lineChartMount, (primaryItem && primaryItem.market) || 'APMC Benchmark');
    }

    // Mount Section 7: Horizontal Bar Chart (strictly sorted highest -> lowest)
    const barChartMount = container.querySelector('#market-horizontal-bar-mount');
    if (barChartMount) {
      renderHorizontalBarChart(rankedRecords, barChartMount, isSpecificVariety ? variety : '', currentLang);
    }
  }


  // Attach Event Listeners:
  // 1. Crop pills
  container.querySelectorAll('.crop-select-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      const selected = btn.getAttribute('data-crop');
      if (onSelectCrop) onSelectCrop(selected);
    });
  });

  // 2. Date toggle pills
  container.querySelectorAll('.date-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      const selDate = btn.getAttribute('data-date');
      if (onSelectDate) onSelectDate(selDate);
    });
  });

  // 3. Variety dropdown
  const varietySelect = container.querySelector('#market-variety-select');
  if (varietySelect) {
    varietySelect.addEventListener('change', (e) => {
      if (onSelectVariety) onSelectVariety(e.target.value);
    });
  }

  // 4. Compare Variety Toggle button
  const compareToggleBtn = container.querySelector('#toggle-variety-compare-btn');
  if (compareToggleBtn) {
    compareToggleBtn.addEventListener('click', () => {
      if (onToggleVarietyCompare) onToggleVarietyCompare();
    });
  }

  // 5. Select variety buttons inside comparison panel
  container.querySelectorAll('.btn-select-variety').forEach(btn => {
    btn.addEventListener('click', () => {
      const varName = btn.getAttribute('data-variety');
      if (varName && onSelectVariety) onSelectVariety(varName);
    });
  });

  // 6. Search input & In-Place Filtering
  const searchInput = container.querySelector('#market-search-input');
  const searchClear = container.querySelector('#market-search-clear');
  const searchWrap = container.querySelector('#search-input-wrapper');
  const tableBody = container.querySelector('#market-table-body');
  const tableCount = container.querySelector('#market-table-count');

  if (searchWrap && searchInput) {
    searchWrap.addEventListener('click', (e) => {
      if (e.target !== searchClear) {
        searchInput.focus();
      }
    });
  }

  function filterTableInPlace(q) {
    const term = (q || '').trim().toLowerCase();
    if (searchClear) {
      searchClear.style.display = term ? 'flex' : 'none';
    }
    if (onSearch) {
      onSearch(q, false); // Persist search query without wiping out DOM
    }

    if (!tableBody) return;

    let visibleCount = 0;
    const rows = tableBody.querySelectorAll('tr[data-market-row]');
    rows.forEach(row => {
      const rowText = (row.getAttribute('data-search-text') || '').toLowerCase();
      if (!term || rowText.includes(term)) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });

    let noResultsRow = tableBody.querySelector('.no-search-results-row');
    if (visibleCount === 0) {
      if (!noResultsRow) {
        noResultsRow = document.createElement('tr');
        noResultsRow.className = 'no-search-results-row';
        noResultsRow.innerHTML = `<td colspan="10" style="text-align:center; padding:24px; color:var(--color-ink-muted);">${t.noMarketsFound}</td>`;
        tableBody.appendChild(noResultsRow);
      } else {
        noResultsRow.style.display = '';
      }
    } else if (noResultsRow) {
      noResultsRow.style.display = 'none';
    }

    if (tableCount) {
      tableCount.textContent = `${visibleCount} ${t.showingMandiYards}`;
    }
  }

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      filterTableInPlace(e.target.value);
    });
  }

  if (searchClear && searchInput) {
    searchClear.addEventListener('click', (e) => {
      e.stopPropagation();
      searchInput.value = '';
      filterTableInPlace('');
      searchInput.focus();
    });
  }

  // 7. Range buttons for line chart
  container.querySelectorAll('.range-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const selRange = btn.getAttribute('data-range');
      if (onSelectRange) onSelectRange(selRange);
    });
  });

  // 8. Sortable table headers
  container.querySelectorAll('.sortable-th').forEach(th => {
    th.addEventListener('click', () => {
      const col = th.getAttribute('data-sort');
      if (onSort) onSort(col);
    });
  });
}

/**
 * Render Weather View
 */
export function renderWeatherView(weatherPayload, elements, currentLang = 'en') {
  const t = translations[currentLang] || translations.en;
  const current = weatherPayload.data;
  elements.location.textContent = weatherPayload.location;
  elements.temp.textContent = current.temp;
  elements.condition.textContent = current.condition;
  elements.humidity.textContent = current.humidity;
  elements.rain.textContent = current.rain_chance;
  elements.wind.textContent = current.wind;
  elements.advisory.textContent = current.advisory;

  const dayMap = {
    'Today': t.dayToday,
    'Tomorrow': t.dayTomorrow,
    'Day 3': t.day3,
    'Day 4': t.day4,
    'Day 5': t.day5
  };

  elements.forecastContainer.innerHTML = '';
  weatherPayload.forecast_5_days.forEach(item => {
    const card = document.createElement('div');
    card.className = 'forecast-card';
    const dayName = dayMap[item.day] || item.day;
    card.innerHTML = `
      <div class="forecast-day">${escapeHtml(dayName)}</div>
      <div class="forecast-icon" style="font-size: 20px; margin: 2px 0;">${item.icon || '⛅'}</div>
      <div class="forecast-temp">${escapeHtml(item.temp)}</div>
      <div class="forecast-condition">${escapeHtml(item.condition)}</div>
      <div class="forecast-rain">${t.rainLabel}: ${escapeHtml(item.rain)}</div>
    `;
    elements.forecastContainer.appendChild(card);
  });
}

/**
 * Render My Crops (Real Farm Management Section)
 */
export function renderCropCards(crops, container, currentLang = 'en') {
  const t = translations[currentLang] || translations.en;
  const cropNames = cropTranslations[currentLang] || cropTranslations.en;
  container.innerHTML = '';
  crops.forEach(item => {
    const card = document.createElement('div');
    card.className = 'farm-crop-card';

    const isHealthy = item.health_status === 'Healthy';
    const statusText = isHealthy ? t.statusHealthy : t.statusNeedsAttention;
    const statusClass = isHealthy ? 'status-tag healthy' : 'status-tag attention';
    const locCrop = cropNames[item.crop] || item.crop;

    card.innerHTML = `
      <div class="crop-card-top-row">
        <div class="crop-badge-group">
          <span class="crop-avatar-icon">${item.icon || '🌱'}</span>
          <div>
            <h3 class="crop-title-name">${escapeHtml(locCrop)}</h3>
            <span class="crop-variety-sub">${escapeHtml(item.variety || 'Standard')} • ${escapeHtml(item.area || '1 Acre')}</span>
          </div>
        </div>
        <div class="crop-badges-right">
          <span class="stage-tag">${escapeHtml(item.growth_stage || 'Active')}</span>
          <span class="${statusClass}">${escapeHtml(statusText)}</span>
        </div>
      </div>

      <div class="crop-card-body-metrics">
        <div class="crop-metric-line">
          <span class="metric-key">${t.plantingDateLabel}</span>
          <span class="metric-val">${escapeHtml(item.planting_date || '45 days ago')}</span>
        </div>
        <div class="crop-metric-line">
          <span class="metric-key">${t.currentGuidanceLabel}</span>
          <span class="metric-val alert-note">${escapeHtml(item.current_alert)}</span>
        </div>
        <div class="crop-metric-line">
          <span class="metric-key">${t.irrigationPlanLabel}</span>
          <span class="metric-val">${escapeHtml(item.irrigation)}</span>
        </div>
        <div class="crop-metric-line">
          <span class="metric-key">${t.fertilizerScheduleLabel}</span>
          <span class="metric-val">${escapeHtml(item.nutrients)}</span>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}


/**
 * Clean markdown formatter
 */
export function formatMarkdown(text) {
  if (!text) return '';
  let str = text;

  // Headings
  str = str.replace(/^### (.*$)/gim, '<h4 class="md-h4">$1</h4>');
  str = str.replace(/^## (.*$)/gim, '<h3 class="md-h3">$1</h3>');

  // Bold & Italic
  str = str.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  str = str.replace(/\*(.*?)\*/g, '<em>$1</em>');

  // Bullet points
  str = str.replace(/^- (.*$)/gim, '<li class="md-li">$1</li>');
  str = str.replace(/(<li class="md-li">.*<\/li>)/gims, '<ul class="md-ul">$1</ul>');

  // Line breaks
  str = str.replace(/\n\n+/g, '<p class="md-p"></p>');

  return str;
}
