/**
 * KisanMitra Main Application Controller
 * Human-designed agricultural companion.
 * Features:
 * - Persistent Light/Dark theme manager
 * - Bottom navigation: [ Chat ] [ Market ] [ Weather ] [ My Crops ] [ Profile ]
 * - Chat-First deferred profile onboarding with query preservation
 * - Dynamic Market prices, interactive historical chart & farm crop management
 */

import { api } from './api.js';
import { translations, cropTranslations } from './translations.js';
import {
  createUserBubble,
  createBotBubble,
  createTypingIndicator,
  renderMarketPage,
  renderWeatherView,
  renderCropCards,
  formatMarkdown
} from './components.js';

// Application State
const state = {
  theme: localStorage.getItem('kisanmitra_theme') || 'light',
  lang: localStorage.getItem('kisanmitra_lang') || 'en',
  conversationId: localStorage.getItem('kisanmitra_conv_id') || ('km_' + Math.random().toString(36).substring(2, 11) + '_' + Date.now()),
  profileCompleted: false,
  profile: {
    name: '',
    location: '',
    crops: [],
    farm_size: '',
    crop_variety: '',
    soil_type: '',
    irrigation_type: '',
    growth_stage: ''
  },
  pendingMessage: null, // { text: string, image?: string, action?: string }
  location: null, // { latitude, longitude, accuracy, district, mandal, state, nearest_market, nearest_distance_km }
  activeTab: 'chat',
  selectedImageBase64: null,
  isRecordingVoice: false,
  marketCrop: 'Tomato',
  marketRange: '7D',
  marketDate: 'Yesterday',
  marketVariety: 'all',
  marketSearchQuery: '',
  marketSortCol: 'modal_price',
  marketSortDir: 'desc',
  marketDataCache: null,
  showVarietyCompare: false,
  weatherDataCache: null
};

// Popular visual crops for selection
const POPULAR_CROPS = [
  { name: "Tomato", icon: "🍅" },
  { name: "Chilli", icon: "🌶️" },
  { name: "Cotton", icon: "☁️" },
  { name: "Paddy", icon: "🌾" },
  { name: "Onion", icon: "🧅" },
  { name: "Maize", icon: "🌽" },
  { name: "Turmeric", icon: "🟡" },
  { name: "Potato", icon: "🥔" }
];

let dom = {};

function boot() {
  try {
    initTheme();
    cacheDOMElements();
    attachEventListeners();
    VoiceController.init();
    loadInitialState();
    setLanguage(state.lang);
  } catch (err) {
    console.error('KisanMitra initialization error:', err);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot);
} else {
  boot();
}

// -------------------------------------------------------------
// Theme Management (Light / Dark Mode with Persistence)
// -------------------------------------------------------------
function initTheme() {
  document.documentElement.setAttribute('data-theme', state.theme);
}

function toggleTheme() {
  state.theme = state.theme === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', state.theme);
  localStorage.setItem('kisanmitra_theme', state.theme);
  updateThemeToggleButtons();
}

function updateThemeToggleButtons() {
  const icon = state.theme === 'light' ? '🌙' : '☀️';
  const title = state.theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode';
  document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
    btn.textContent = icon;
    btn.title = title;
  });
}

function cacheDOMElements() {
  dom = {
    // Sidebar
    sidebar: document.getElementById('app-sidebar'),
    sidebarCloseBtn: document.getElementById('sidebar-close-btn'),
    mobileMenuBtn: document.getElementById('mobile-menu-btn'),
    sidebarBackdrop: document.getElementById('sidebar-backdrop'),
    themeToggleBtns: document.querySelectorAll('.theme-toggle-btn'),
    sidebarProfileBtn: document.getElementById('sidebar-profile-btn'),
    sidebarFarmerName: document.getElementById('sidebar-farmer-name'),
    sidebarProfileSub: document.getElementById('sidebar-profile-sub'),
    sidebarStatusDot: document.getElementById('sidebar-status-dot'),

    // Header Profile & Language Elements
    headerProfileBtn: document.getElementById('header-profile-btn') || document.getElementById('mobile-profile-btn'),
    headerFarmerName: document.getElementById('header-farmer-name') || document.getElementById('mobile-farmer-name'),
    headerStatusDot: document.getElementById('header-status-dot') || document.getElementById('mobile-status-dot'),
    headerLocationBtn: document.getElementById('header-location-btn'),
    headerLocationName: document.getElementById('header-location-name'),
    langPills: document.querySelectorAll('.lang-pill'),

    // Sidebar Navigation: [ Chat ] [ Market ] [ Weather ] [ My Crops ] [ Profile ]
    navTabs: document.querySelectorAll('.sidebar-nav-item'),
    tabPanes: document.querySelectorAll('.tab-view-pane'),

    // Chat
    chatStream: document.getElementById('chat-stream'),
    chatInput: document.getElementById('chat-input'),
    sendBtn: document.getElementById('chat-send-btn'),
    photoBtn: document.getElementById('chat-photo-btn'),
    photoInput: document.getElementById('chat-photo-input'),
    voiceBtn: document.getElementById('chat-voice-btn'),
    attachmentBar: document.getElementById('chat-attachment-bar'),
    attachmentPreview: document.getElementById('attachment-preview-img'),
    attachmentThumbClick: document.getElementById('attachment-thumb-click'),
    attachmentMainText: document.getElementById('attachment-main-text'),
    attachmentSizeBadge: document.getElementById('attachment-size-badge'),
    attachmentChangeBtn: document.getElementById('attachment-change-btn'),
    attachmentRemoveBtn: document.getElementById('attachment-remove-btn'),
    cameraCaptureInput: document.getElementById('chat-camera-capture-input'),
    compactActionBtns: document.querySelectorAll('.compact-action-btn'),

    // Camera & Photo Modals
    photoOptionsModal: document.getElementById('photo-options-modal'),
    photoOptionsCloseBtn: document.getElementById('photo-options-close-btn'),
    optCameraBtn: document.getElementById('opt-camera-btn'),
    optGalleryBtn: document.getElementById('opt-gallery-btn'),
    cameraModal: document.getElementById('camera-viewfinder-modal'),
    cameraVideo: document.getElementById('camera-video'),
    cameraCanvas: document.getElementById('camera-canvas'),
    cameraSnapshotPreview: document.getElementById('camera-snapshot-preview'),
    cameraShutterBtn: document.getElementById('camera-shutter-btn'),
    cameraShutterFlash: document.getElementById('camera-shutter-flash'),
    cameraRetakeBtn: document.getElementById('camera-retake-btn'),
    cameraConfirmBtn: document.getElementById('camera-confirm-btn'),
    cameraFlipBtn: document.getElementById('camera-flip-btn'),
    cameraModalCloseBtn: document.getElementById('camera-modal-close-btn'),
    cameraCaptureControls: document.getElementById('camera-capture-controls'),
    cameraReviewControls: document.getElementById('camera-review-controls'),
    chatDragOverlay: document.getElementById('chat-drag-overlay'),
    lightboxModal: document.getElementById('image-lightbox-modal'),
    lightboxImg: document.getElementById('lightbox-img'),
    lightboxCloseBtn: document.getElementById('lightbox-close-btn'),

    // Voice Assistant Elements
    voiceDock: document.getElementById('voice-dock-overlay'),
    voiceMicHalo: document.getElementById('voice-mic-halo'),
    voiceWaveform: document.getElementById('voice-waveform'),
    voiceStatusHeading: document.getElementById('voice-status-heading'),
    voiceTranscriptText: document.getElementById('voice-transcript-text'),
    voiceCountdownBar: document.getElementById('voice-countdown-bar'),
    voiceCountdownFill: document.getElementById('voice-countdown-fill'),
    voiceActionsRow: document.getElementById('voice-actions-row'),
    speakingStatusBar: document.getElementById('speaking-status-bar'),
    speakingStatusText: document.getElementById('speaking-status-text'),
    speakingPauseBtn: document.getElementById('speaking-pause-btn'),
    speakingStopBtn: document.getElementById('speaking-stop-btn'),

    // Market View Mount
    marketViewContainer: document.getElementById('market-content-mount'),

    // Weather View Elements
    weatherLocation: document.getElementById('weather-location-title'),
    weatherTemp: document.getElementById('weather-temp-display'),
    weatherCondition: document.getElementById('weather-condition-display'),
    weatherHumidity: document.getElementById('weather-humidity-display'),
    weatherRain: document.getElementById('weather-rain-display'),
    weatherWind: document.getElementById('weather-wind-display'),
    weatherAdvisory: document.getElementById('weather-advisory-text'),
    weatherForecastContainer: document.getElementById('weather-forecast-strip'),

    // My Crops View Mount
    cropsListContainer: document.getElementById('crops-list-mount'),

    // Profile View Elements
    profileDisplayName: document.getElementById('profile-display-name'),
    profileDisplayLocation: document.getElementById('profile-display-location'),
    profileDisplayCrops: document.getElementById('profile-display-crops'),
    profileDisplaySize: document.getElementById('profile-display-size'),
    profileDisplayVariety: document.getElementById('profile-display-variety'),
    profileDisplaySoil: document.getElementById('profile-display-soil'),
    profileDisplayIrrigation: document.getElementById('profile-display-irrigation'),
    profileDisplayStage: document.getElementById('profile-display-stage'),
    editProfileBtn: document.getElementById('edit-profile-btn'),
    resetProfileBtn: document.getElementById('reset-profile-btn'),

    // Profile Setup Modal
    modalBackdrop: document.getElementById('profile-modal-backdrop'),
    profileForm: document.getElementById('profile-form'),
    modalHeading: document.getElementById('modal-heading'),
    modalSubheading: document.getElementById('modal-subheading'),
    modalSubmitBtnText: document.getElementById('modal-submit-text'),
    preservedQueryNotice: document.getElementById('preserved-query-notice'),
    preservedQueryText: document.getElementById('preserved-query-text'),
    inputName: document.getElementById('input-farmer-name'),
    inputLocation: document.getElementById('input-farm-location'),
    detectGpsBtn: document.getElementById('detect-gps-btn'),
    gpsStatusHint: document.getElementById('gps-status-hint'),
    inputSize: document.getElementById('input-farm-size'),
    cropChipsContainer: document.getElementById('crop-chips-grid'),
    inputCustomCrops: document.getElementById('input-custom-crops'),
    inputVariety: document.getElementById('input-crop-variety'),
    inputSoil: document.getElementById('input-soil-type'),
    inputIrrigation: document.getElementById('input-irrigation-type'),
    inputStage: document.getElementById('input-growth-stage'),
    optionalToggleBtn: document.getElementById('optional-fields-toggle'),
    optionalFieldsContainer: document.getElementById('optional-fields-container'),
    modalCloseBtn: document.getElementById('modal-dismiss-btn'),

    // Mobile Phone Access Elements
    headerMobileShareBtn: document.getElementById('header-mobile-share-btn'),
    sidebarMobileShareBtn: document.getElementById('sidebar-mobile-share-btn'),
    mobileShareModal: document.getElementById('mobile-share-modal'),
    mobileShareCloseBtn: document.getElementById('mobile-share-close-btn'),
    mobileQrImg: document.getElementById('mobile-qr-img'),
    publicUrlInput: document.getElementById('public-url-input'),
    copyPublicUrlBtn: document.getElementById('copy-public-url-btn'),
    openPublicUrlBtn: document.getElementById('open-public-url-btn'),
    localUrlInput: document.getElementById('local-url-input'),
    copyLocalUrlBtn: document.getElementById('copy-local-url-btn'),
    openLocalUrlBtn: document.getElementById('open-local-url-btn')
  };

  updateThemeToggleButtons();
  renderCropChips([]);
}

function openSidebar() {
  if (dom.sidebar) dom.sidebar.classList.add('open');
  if (dom.sidebarBackdrop) dom.sidebarBackdrop.classList.add('active');
}

function closeSidebar() {
  if (dom.sidebar) dom.sidebar.classList.remove('open');
  if (dom.sidebarBackdrop) dom.sidebarBackdrop.classList.remove('active');
}

function attachEventListeners() {
  // Theme Toggles
  dom.themeToggleBtns.forEach(btn => {
    btn.addEventListener('click', toggleTheme);
  });

  // Mobile Drawer Open / Close
  if (dom.mobileMenuBtn) {
    dom.mobileMenuBtn.addEventListener('click', openSidebar);
  }
  if (dom.sidebarCloseBtn) {
    dom.sidebarCloseBtn.addEventListener('click', closeSidebar);
  }
  if (dom.sidebarBackdrop) {
    dom.sidebarBackdrop.addEventListener('click', closeSidebar);
  }

  // Sidebar Navigation Links: [ Chat ] [ Market ] [ Weather ] [ My Crops ] [ Profile ]
  dom.navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetView = tab.getAttribute('data-tab');
      navigateToView(targetView);
    });
  });

  // Profile Badges
  if (dom.sidebarProfileBtn) {
    dom.sidebarProfileBtn.addEventListener('click', () => {
      navigateToView('profile');
    });
  }
  if (dom.headerProfileBtn) {
    dom.headerProfileBtn.addEventListener('click', () => {
      navigateToView('profile');
    });
  }

  // Location Pill & GPS Button
  if (dom.headerLocationBtn) {
    dom.headerLocationBtn.addEventListener('click', () => {
      requestUserLocation(true);
    });
  }
  if (dom.detectGpsBtn) {
    dom.detectGpsBtn.addEventListener('click', () => {
      requestUserLocation(false);
    });
  }

  // Language Selector Pills
  if (dom.langPills) {
    dom.langPills.forEach(pill => {
      pill.addEventListener('click', () => {
        const lang = pill.getAttribute('data-lang');
        if (lang) setLanguage(lang);
      });
    });
  }

  // Chat message submit
  if (dom.chatInput) {
    dom.chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendInput();
      }
    });
    // On touch or tap, ensure smooth scroll into view without breaking keyboard
    dom.chatInput.addEventListener('focus', () => {
      setTimeout(() => {
        if (dom.chatStream) {
          dom.chatStream.scrollTop = dom.chatStream.scrollHeight;
        }
      }, 300);
    });
  }
  if (dom.sendBtn) {
    dom.sendBtn.addEventListener('click', (e) => {
      e.preventDefault();
      handleSendInput();
    });
  }

  // Compact Quick Action Buttons
  dom.compactActionBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const query = btn.getAttribute('data-query');
      const action = btn.getAttribute('data-action');
      if (action === 'crop_photo') {
        openPhotoOptionsModal();
        return;
      }
      handleInteraction({ text: query, image: null, action });
    });
  });

  // Photo & Camera Trigger Modal
  if (dom.photoBtn) {
    dom.photoBtn.addEventListener('click', (e) => {
      e.preventDefault();
      openPhotoOptionsModal();
    });
  }
  if (dom.photoOptionsCloseBtn) {
    dom.photoOptionsCloseBtn.addEventListener('click', (e) => {
      e.preventDefault();
      closePhotoOptionsModal();
    });
  }
  if (dom.photoOptionsModal) {
    dom.photoOptionsModal.addEventListener('click', (e) => {
      if (e.target === dom.photoOptionsModal) closePhotoOptionsModal();
    });
  }
  if (dom.optCameraBtn) {
    dom.optCameraBtn.addEventListener('click', (e) => {
      e.preventDefault();
      CameraController.openCamera();
    });
  }
  if (dom.optGalleryBtn) {
    dom.optGalleryBtn.addEventListener('click', (e) => {
      e.preventDefault();
      closePhotoOptionsModal();
      if (dom.photoInput) dom.photoInput.click();
    });
  }

  // Camera Viewfinder Modal Controls
  if (dom.cameraShutterBtn) {
    dom.cameraShutterBtn.addEventListener('click', () => CameraController.snapPhoto());
  }
  if (dom.cameraRetakeBtn) {
    dom.cameraRetakeBtn.addEventListener('click', () => CameraController.retake());
  }
  if (dom.cameraConfirmBtn) {
    dom.cameraConfirmBtn.addEventListener('click', () => CameraController.confirmPhoto());
  }
  if (dom.cameraFlipBtn) {
    dom.cameraFlipBtn.addEventListener('click', () => CameraController.flipCamera());
  }
  if (dom.cameraModalCloseBtn) {
    dom.cameraModalCloseBtn.addEventListener('click', () => CameraController.closeCamera());
  }

  // File Inputs (Gallery & Mobile Camera Direct)
  if (dom.photoInput) {
    dom.photoInput.addEventListener('change', handleFileSelected);
  }
  if (dom.cameraCaptureInput) {
    dom.cameraCaptureInput.addEventListener('change', handleFileSelected);
  }

  // Attachment Bar Controls
  if (dom.attachmentRemoveBtn) {
    dom.attachmentRemoveBtn.addEventListener('click', clearAttachment);
  }
  if (dom.attachmentChangeBtn) {
    dom.attachmentChangeBtn.addEventListener('click', openPhotoOptionsModal);
  }
  if (dom.attachmentThumbClick) {
    dom.attachmentThumbClick.addEventListener('click', () => {
      if (state.selectedImageBase64) openLightbox(state.selectedImageBase64);
    });
  }

  // Lightbox Close Controls
  if (dom.lightboxCloseBtn) {
    dom.lightboxCloseBtn.addEventListener('click', closeLightbox);
  }
  if (dom.lightboxModal) {
    dom.lightboxModal.addEventListener('click', (e) => {
      if (e.target === dom.lightboxModal) closeLightbox();
    });
  }

  // Drag & Drop & Paste Handlers
  setupDragAndDrop();

  // Voice Input Toggle & TTS Playback Controls
  if (dom.voiceBtn) {
    dom.voiceBtn.addEventListener('click', handleVoiceToggle);
  }
  if (dom.speakingPauseBtn) {
    dom.speakingPauseBtn.addEventListener('click', () => VoiceController.togglePauseSpeaking());
  }
  if (dom.speakingStopBtn) {
    dom.speakingStopBtn.addEventListener('click', () => VoiceController.stopSpeaking());
  }

  // Profile Modal
  dom.optionalToggleBtn.addEventListener('click', toggleOptionalFields);
  dom.profileForm.addEventListener('submit', handleProfileFormSubmit);
  if (dom.modalCloseBtn) {
    dom.modalCloseBtn.addEventListener('click', closeProfileModal);
  }

  // Profile View Actions
  dom.editProfileBtn.addEventListener('click', () => openProfileModal(true));
  dom.resetProfileBtn.addEventListener('click', handleResetProfile);

  // Mobile Phone Access Modal Controls
  if (dom.headerMobileShareBtn) {
    dom.headerMobileShareBtn.addEventListener('click', openMobileShareModal);
  }
  if (dom.sidebarMobileShareBtn) {
    dom.sidebarMobileShareBtn.addEventListener('click', openMobileShareModal);
  }
  if (dom.mobileShareCloseBtn) {
    dom.mobileShareCloseBtn.addEventListener('click', closeMobileShareModal);
  }
  if (dom.mobileShareModal) {
    dom.mobileShareModal.addEventListener('click', (e) => {
      if (e.target === dom.mobileShareModal) closeMobileShareModal();
    });
  }
  if (dom.copyPublicUrlBtn && dom.publicUrlInput) {
    dom.copyPublicUrlBtn.addEventListener('click', () => {
      copyToClipboard(dom.publicUrlInput.value, dom.copyPublicUrlBtn);
    });
  }
  if (dom.copyLocalUrlBtn && dom.localUrlInput) {
    dom.copyLocalUrlBtn.addEventListener('click', () => {
      copyToClipboard(dom.localUrlInput.value, dom.copyLocalUrlBtn);
    });
  }
}

// -------------------------------------------------------------
// State Initialization
// -------------------------------------------------------------
async function loadInitialState() {
  try {
    const profile = await api.getProfile().catch(() => null);
    if (profile && profile.completed) {
      state.profileCompleted = true;
      state.profile = profile;
      updateHeaderProfileUI(true);
      updateProfileViewUI();
      if (profile.location && dom.headerLocationName) {
        dom.headerLocationName.textContent = profile.location;
      }
    } else {
      state.profileCompleted = false;
      updateHeaderProfileUI(false);
    }
  } catch (err) {
    console.warn('Initial profile load error:', err);
    state.profileCompleted = false;
    updateHeaderProfileUI(false);
  }

  // Gracefully check if browser already allowed geolocation
  if (navigator.permissions && navigator.permissions.query) {
    navigator.permissions.query({ name: 'geolocation' }).then(result => {
      if (result.state === 'granted') {
        requestUserLocation(false);
      }
    }).catch(() => {});
  }
}

async function requestUserLocation(promptUser = false) {
  const t = translations[state.lang] || translations.en;

  if (!navigator.geolocation) {
    if (dom.gpsStatusHint) {
      dom.gpsStatusHint.textContent = t.gpsUnsupported || 'Geolocation is not supported in this browser.';
      dom.gpsStatusHint.style.color = '#dc2626';
      dom.gpsStatusHint.style.display = 'block';
    }
    return;
  }

  if (dom.gpsStatusHint) {
    dom.gpsStatusHint.textContent = t.gpsDetecting || 'Detecting exact GPS coordinates...';
    dom.gpsStatusHint.style.color = '#0284c7';
    dom.gpsStatusHint.style.display = 'block';
  }
  if (dom.headerLocationName) {
    dom.headerLocationName.textContent = 'Detecting...';
  }

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      try {
        const { latitude, longitude, accuracy } = position.coords;
        const res = await api.resolveLocation({ latitude, longitude, accuracy });

        state.location = {
          latitude,
          longitude,
          accuracy: Math.round(accuracy || 0),
          district: res.district,
          state: res.state,
          country: res.country || 'India',
          nearest_market: res.nearest_market,
          nearest_distance_km: res.nearest_distance_km,
          captured_at: res.captured_at
        };

        const locDisplay = res.display_name || `${res.district}, ${res.state}`;
        if (dom.inputLocation) {
          dom.inputLocation.value = locDisplay;
        }
        if (dom.headerLocationName) {
          dom.headerLocationName.textContent = res.nearest_market ? `${res.district} (${res.nearest_distance_km}km)` : res.district;
        }
        if (dom.headerLocationBtn) {
          dom.headerLocationBtn.classList.add('active');
          dom.headerLocationBtn.title = `Exact GPS: ${res.district} • Nearest Mandi: ${res.nearest_market} (${res.nearest_distance_km} km)`;
        }
        if (dom.gpsStatusHint) {
          dom.gpsStatusHint.textContent = `✓ ${res.display_name} • ${t.nearbyMandiLabel || 'Nearest APMC Mandi:'} ${res.nearest_market} (${res.nearest_distance_km} km)`;
          dom.gpsStatusHint.style.color = '#16a34a';
          dom.gpsStatusHint.style.display = 'block';
        }
      } catch (err) {
        console.warn('Location resolution failed:', err);
        if (dom.gpsStatusHint) {
          dom.gpsStatusHint.textContent = 'GPS captured. Could not resolve nearby mandi.';
          dom.gpsStatusHint.style.color = '#ea580c';
        }
      }
    },
    (err) => {
      console.warn('Geolocation error:', err.message);
      if (dom.gpsStatusHint) {
        dom.gpsStatusHint.textContent = t.gpsDenied || 'Location permission denied. You can enter manually.';
        dom.gpsStatusHint.style.color = '#dc2626';
        dom.gpsStatusHint.style.display = 'block';
      }
      if (dom.headerLocationName) {
        dom.headerLocationName.textContent = (state.profile && state.profile.location) ? state.profile.location : 'Detect Location';
      }
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 }
  );
}

function setLanguage(lang) {
  if (!translations[lang]) lang = 'en';
  state.lang = lang;
  localStorage.setItem('kisanmitra_lang', lang);

  // Update pills
  if (dom.langPills) {
    dom.langPills.forEach(p => {
      if (p.getAttribute('data-lang') === lang) {
        p.classList.add('active');
      } else {
        p.classList.remove('active');
      }
    });
  }

  const t = translations[lang];

  // Update Brand Taglines
  const brandSub = document.querySelector('.brand-sub');
  if (brandSub) brandSub.textContent = t.brandTagline;
  const headerTagline = document.querySelector('.header-tagline');
  if (headerTagline) headerTagline.textContent = `"${t.brandTagline}"`;

  // Update Welcome Card
  const welcomeBadge = document.querySelector('.welcome-badge-tag');
  if (welcomeBadge) welcomeBadge.textContent = t.welcomeBadge;
  const greetingEl = document.querySelector('.companion-greeting');
  if (greetingEl) greetingEl.textContent = t.welcomeTitle;
  const descEl = document.querySelector('.companion-description');
  if (descEl) descEl.textContent = t.welcomeSubtitle;
  const qaHeading = document.querySelector('.quick-actions-heading');
  if (qaHeading) qaHeading.textContent = t.quickActionsHeading;

  // Update Input placeholder & Voice labels
  if (dom.chatInput) dom.chatInput.placeholder = t.inputPlaceholder;
  if (dom.speakingStatusText && VoiceController.isSpeaking) {
    dom.speakingStatusText.textContent = t.voiceSpeaking || 'KisanMitra is speaking...';
  }
  if (dom.speakingPauseBtn) {
    dom.speakingPauseBtn.textContent = VoiceController.isPaused ? `▶️ ${t.voiceResume || 'Resume'}` : `⏸️ ${t.voicePause || 'Pause'}`;
  }
  if (dom.speakingStopBtn) {
    dom.speakingStopBtn.textContent = `⏹️ ${t.voiceStop || 'Stop'}`;
  }

  // Update Photo Options & Camera Viewfinder Labels
  const lblPhotoTitle = document.getElementById('lbl-photo-options-title');
  if (lblPhotoTitle) lblPhotoTitle.textContent = t.photoOptionsTitle;
  const lblPhotoSub = document.getElementById('lbl-photo-options-sub');
  if (lblPhotoSub) lblPhotoSub.textContent = t.photoOptionsSub;
  const lblOptCamera = document.getElementById('lbl-opt-camera');
  if (lblOptCamera) lblOptCamera.textContent = t.takePhoto;
  const lblOptCameraDesc = document.getElementById('lbl-opt-camera-desc');
  if (lblOptCameraDesc) lblOptCameraDesc.textContent = t.takePhotoDesc;
  const lblOptGallery = document.getElementById('lbl-opt-gallery');
  if (lblOptGallery) lblOptGallery.textContent = t.chooseGallery;
  const lblOptGalleryDesc = document.getElementById('lbl-opt-gallery-desc');
  if (lblOptGalleryDesc) lblOptGalleryDesc.textContent = t.chooseGalleryDesc;

  const cameraHeading = document.getElementById('camera-modal-heading');
  if (cameraHeading) cameraHeading.textContent = t.cameraModalHeading;
  const cameraFlipLbl = document.getElementById('lbl-camera-flip');
  if (cameraFlipLbl) cameraFlipLbl.textContent = t.cameraFlip;
  const viewfinderHint = document.getElementById('viewfinder-hint-text');
  if (viewfinderHint) viewfinderHint.textContent = t.cameraGuide;
  const shutterCaption = document.getElementById('lbl-shutter-caption');
  if (shutterCaption) shutterCaption.textContent = t.snapPhoto;
  const cameraRetakeLbl = document.getElementById('lbl-camera-retake');
  if (cameraRetakeLbl) cameraRetakeLbl.textContent = t.retakePhoto;
  const cameraUseLbl = document.getElementById('lbl-camera-use');
  if (cameraUseLbl) cameraUseLbl.textContent = t.usePhoto;

  const dragTitle = document.getElementById('lbl-drag-title');
  if (dragTitle) dragTitle.textContent = t.dragDropTitle;
  const dragSub = document.getElementById('lbl-drag-sub');
  if (dragSub) dragSub.textContent = t.dragDropSub;

  if (dom.attachmentMainText) dom.attachmentMainText.textContent = t.photoAttachedText;
  if (dom.attachmentChangeBtn) dom.attachmentChangeBtn.textContent = `🔄 ${t.changePhoto || 'Change'}`;

  // Update Quick Actions
  const actionMap = {
    market_prices: { label: t.marketPrices, query: t.qPromptMarketPrice },
    price_history: { label: t.priceHistory, query: t.qPromptPriceHistory },
    compare_markets: { label: t.compareMarkets, query: t.qPromptCompareMarkets },
    weather: { label: t.weather, query: t.qPromptWeather },
    crop_help: { label: t.cropHelp, query: t.qPromptCropHelp },
    crop_photo: { label: t.analyzePhoto, query: t.qPromptCropPhoto }
  };
  if (dom.compactActionBtns) {
    dom.compactActionBtns.forEach(btn => {
      const action = btn.getAttribute('data-action');
      const conf = actionMap[action];
      if (conf) {
        const labelSpan = btn.querySelector('.action-label');
        if (labelSpan) labelSpan.textContent = conf.label;
        btn.setAttribute('data-query', conf.query);
      }
    });
  }

  // Update Nav items
  const navMap = {
    chat: t.navChat,
    market: t.navMarket,
    weather: t.navWeather,
    crops: t.navCrops,
    profile: t.navProfile
  };
  if (dom.navTabs) {
    dom.navTabs.forEach(tab => {
      const tabName = tab.getAttribute('data-tab');
      const labelSpan = tab.querySelector('.nav-label');
      if (labelSpan && navMap[tabName]) {
        labelSpan.textContent = navMap[tabName];
      }
    });
  }

  // Sidebar Menu Heading & Appearance
  const navHeading = document.querySelector('.sidebar-nav-heading');
  if (navHeading) navHeading.textContent = t.menuHeading;
  const themeLabel = document.querySelector('.theme-row-label');
  if (themeLabel) themeLabel.textContent = t.appearance;

  // Attachment preview text
  const attachSpan = dom.attachmentBar ? dom.attachmentBar.querySelector('span') : null;
  if (attachSpan) attachSpan.textContent = t.photoAttachedText;

  // Preserved query box
  const pTitle = document.getElementById('preserved-query-title');
  if (pTitle) pTitle.textContent = t.preservedQueryTitle;
  const pCap = document.getElementById('preserved-query-caption');
  if (pCap) pCap.textContent = t.preservedQueryCaption;

  // Modal labels & placeholders
  const elLblName = document.getElementById('lbl-modal-name');
  if (elLblName) elLblName.textContent = t.modalName;
  const elLblNameReq = document.getElementById('lbl-modal-name-req');
  if (elLblNameReq) elLblNameReq.textContent = t.modalNameReq;
  if (dom.inputName) dom.inputName.placeholder = t.modalNamePlaceholder;

  const elLblLoc = document.getElementById('lbl-modal-location');
  if (elLblLoc) elLblLoc.textContent = t.modalLocation;
  const elLblLocReq = document.getElementById('lbl-modal-location-req');
  if (elLblLocReq) elLblLocReq.textContent = t.modalLocationReq;
  if (dom.inputLocation) dom.inputLocation.placeholder = t.modalLocationPlaceholder;

  const elLblCrops = document.getElementById('lbl-modal-crops');
  if (elLblCrops) elLblCrops.textContent = t.modalCrops;
  const elLblCropsReq = document.getElementById('lbl-modal-crops-req');
  if (elLblCropsReq) elLblCropsReq.textContent = t.modalCropsReq;
  if (dom.inputCustomCrops) dom.inputCustomCrops.placeholder = t.modalCustomCropsPlaceholder;

  const elLblSize = document.getElementById('lbl-modal-size');
  if (elLblSize) elLblSize.textContent = t.modalSize;
  const elLblSizeReq = document.getElementById('lbl-modal-size-req');
  if (elLblSizeReq) elLblSizeReq.textContent = t.modalSizeReq;
  if (dom.inputSize) dom.inputSize.placeholder = t.modalSizePlaceholder;

  const elLblOpt = document.getElementById('lbl-modal-optional-toggle');
  if (elLblOpt) elLblOpt.textContent = t.modalOptionalToggle;
  const elLblVar = document.getElementById('lbl-modal-variety');
  if (elLblVar) elLblVar.textContent = t.modalVariety;
  const elLblVarOpt = document.getElementById('lbl-modal-variety-opt');
  if (elLblVarOpt) elLblVarOpt.textContent = t.modalVarietyOpt;
  if (dom.inputVariety) dom.inputVariety.placeholder = t.modalVarietyPlaceholder;

  const elLblSoil = document.getElementById('lbl-modal-soil');
  if (elLblSoil) elLblSoil.textContent = t.modalSoil;
  const elLblSoilOpt = document.getElementById('lbl-modal-soil-opt');
  if (elLblSoilOpt) elLblSoilOpt.textContent = t.modalSoilOpt;

  const elLblIrr = document.getElementById('lbl-modal-irrigation');
  if (elLblIrr) elLblIrr.textContent = t.modalIrrigation;
  const elLblIrrOpt = document.getElementById('lbl-modal-irrigation-opt');
  if (elLblIrrOpt) elLblIrrOpt.textContent = t.modalIrrigationOpt;

  const elLblStg = document.getElementById('lbl-modal-stage');
  if (elLblStg) elLblStg.textContent = t.modalStage;
  const elLblStgOpt = document.getElementById('lbl-modal-stage-opt');
  if (elLblStgOpt) elLblStgOpt.textContent = t.modalStageOpt;

  const elDisc = document.getElementById('modal-disclaimer-text');
  if (elDisc) elDisc.textContent = t.modalDisclaimer;

  if (dom.modalSubmitBtnText) {
    dom.modalSubmitBtnText.textContent = state.profileCompleted ? t.editProfileSaveBtn : t.modalSaveBtn;
  }

  // Profile view labels
  const pCrops = document.getElementById('profile-lbl-crops');
  if (pCrops) pCrops.textContent = t.profileLblCrops;
  const pSize = document.getElementById('profile-lbl-size');
  if (pSize) pSize.textContent = t.profileLblSize;
  const pVar = document.getElementById('profile-lbl-variety');
  if (pVar) pVar.textContent = t.profileLblVariety;
  const pSoil = document.getElementById('profile-lbl-soil');
  if (pSoil) pSoil.textContent = t.profileLblSoil;
  const pIrr = document.getElementById('profile-lbl-irrigation');
  if (pIrr) pIrr.textContent = t.profileLblIrrigation;
  const pStg = document.getElementById('profile-lbl-stage');
  if (pStg) pStg.textContent = t.profileLblStage;

  if (dom.editProfileBtn) dom.editProfileBtn.textContent = t.editProfileBtnText;
  if (dom.resetProfileBtn) dom.resetProfileBtn.textContent = t.resetProfileBtnText;
  const backChatBtn = document.querySelector('#view-profile .btn-secondary');
  if (backChatBtn) backChatBtn.textContent = t.backToChatBtnText;

  // Weather section static headers
  const wH2 = document.querySelector('#view-weather h2');
  if (wH2) wH2.textContent = t.weatherHeading;
  const wSub = document.querySelector('#view-weather p');
  if (wSub) wSub.textContent = t.weatherSub;
  const wAdvTitle = document.querySelector('.advisory-title');
  if (wAdvTitle) wAdvTitle.textContent = t.recommendationTitle;
  const wOutlook = document.querySelector('#view-weather h3');
  if (wOutlook) wOutlook.textContent = t.forecastOutlook;

  // My Crops section static headers
  const crH2 = document.querySelector('#view-crops h2');
  if (crH2) crH2.textContent = t.cropsHeading;
  const crSub = document.querySelector('#view-crops p');
  if (crSub) crSub.textContent = t.cropsSub;

  // Profile section static headers
  const prH2 = document.querySelector('#view-profile h2');
  if (prH2) prH2.textContent = t.profileHeading;
  const prSub = document.querySelector('#view-profile p');
  // Mobile Share labels
  const lblHeaderMobile = document.getElementById('lbl-header-mobile');
  if (lblHeaderMobile) lblHeaderMobile.textContent = t.openOnMobile || 'Open on Mobile';
  const lblSidebarMobile = document.getElementById('lbl-sidebar-mobile');
  if (lblSidebarMobile) lblSidebarMobile.textContent = t.openOnMobile || 'Open on Mobile';
  const lblMobileTitle = document.getElementById('lbl-mobile-modal-title');
  if (lblMobileTitle) lblMobileTitle.textContent = t.mobileModalTitle || 'Open on Mobile Phone';
  const lblMobileSub = document.getElementById('lbl-mobile-modal-sub');
  if (lblMobileSub) lblMobileSub.textContent = t.mobileModalSub || 'Scan the QR code or use the links below to run KisanMitra on your phone.';
  const lblQrTip = document.getElementById('lbl-qr-scan-tip');
  if (lblQrTip) lblQrTip.textContent = t.qrScanTip || 'Point your phone camera at this QR code to open instantly';
  const lblLinkRec = document.getElementById('lbl-link-rec');
  if (lblLinkRec) lblLinkRec.textContent = t.recommendedLink || '⭐ Recommended (All Networks & Mobile Data)';
  const lblLinkRecDesc = document.getElementById('lbl-link-rec-desc');
  if (lblLinkRecDesc) lblLinkRecDesc.textContent = t.recommendedDesc || 'Works on 4G/5G mobile data and any Wi-Fi. Enables live voice mic and camera!';
  const lblLinkLocal = document.getElementById('lbl-link-local');
  if (lblLinkLocal) lblLinkLocal.textContent = t.localWifiLink || '📶 Same Wi-Fi Network';
  const lblLinkLocalDesc = document.getElementById('lbl-link-local-desc');
  if (lblLinkLocalDesc) lblLinkLocalDesc.textContent = t.localWifiDesc || 'Direct IP link when your phone is connected to the same local Wi-Fi:';
  const copyPublicBtnText = dom.copyPublicUrlBtn ? dom.copyPublicUrlBtn.querySelector('.copy-btn-text') : null;
  if (copyPublicBtnText) copyPublicBtnText.textContent = t.copyBtn || '📋 Copy';
  const copyLocalBtnText = dom.copyLocalUrlBtn ? dom.copyLocalUrlBtn.querySelector('.copy-btn-text') : null;
  if (copyLocalBtnText) copyLocalBtnText.textContent = t.copyBtn || '📋 Copy';
  const lblFeatVoice = document.getElementById('lbl-feature-voice');
  if (lblFeatVoice && t.featureLiveVoice) {
    lblFeatVoice.innerHTML = `<strong>${state.lang === 'te' ? 'వాయిస్ సంభాషణ:' : state.lang === 'hi' ? 'लाइव वॉइस:' : 'Live Voice:'}</strong> ${t.featureLiveVoice.replace(/^(Live Voice:|వాయిస్ సంభాషణ:|लाइव वॉइस:)\s*/i, '')}`;
  }
  const lblFeatCamera = document.getElementById('lbl-feature-camera');
  if (lblFeatCamera && t.featureCamera) {
    lblFeatCamera.innerHTML = `<strong>${state.lang === 'te' ? 'పంట కెమెరా:' : state.lang === 'hi' ? 'कैमरा जांच:' : 'Camera Snap:'}</strong> ${t.featureCamera.replace(/^(Camera Snap:|పంట కెమెరా:|कैमरा जांच:)\s*/i, '')}`;
  }
  const lblFeatPwa = document.getElementById('lbl-feature-pwa');
  if (lblFeatPwa && t.featurePWA) {
    lblFeatPwa.innerHTML = `<strong>${state.lang === 'te' ? 'హోమ్ స్క్రీన్:' : state.lang === 'hi' ? 'होम स्क्रीन:' : 'Home Screen:'}</strong> ${t.featurePWA.replace(/^(Home Screen:|హోమ్ స్క్రీన్:|होम स्क्रीन:)\s*/i, '')}`;
  }

  // Re-render modal crop chips with localized labels
  renderCropChips(state.profile.crops || []);

  updateHeaderProfileUI(state.profileCompleted);

  // Re-render currently active view
  if (state.activeTab === 'market') {
    renderCurrentMarketPage();
  } else if (state.activeTab === 'weather' && state.weatherDataCache) {
    renderWeatherView(state.weatherDataCache, {
      location: dom.weatherLocation,
      temp: dom.weatherTemp,
      condition: dom.weatherCondition,
      humidity: dom.weatherHumidity,
      rain: dom.weatherRain,
      wind: dom.weatherWind,
      advisory: dom.weatherAdvisory,
      forecastContainer: dom.weatherForecastContainer
    }, state.lang);
  } else if (state.activeTab === 'crops') {
    loadCropsData();
  } else if (state.activeTab === 'profile') {
    updateProfileViewUI();
  }
}

function updateHeaderProfileUI(isCompleted) {
  const t = translations[state.lang] || translations.en;
  if (isCompleted && state.profile.name) {
    if (dom.sidebarFarmerName) dom.sidebarFarmerName.textContent = state.profile.name;
    if (dom.sidebarProfileSub) dom.sidebarProfileSub.textContent = state.profile.location ? `📍 ${state.profile.location}` : t.statusReady;
    if (dom.sidebarStatusDot) {
      dom.sidebarStatusDot.classList.remove('status-pending');
      dom.sidebarStatusDot.classList.add('status-active');
    }
    if (dom.headerFarmerName) dom.headerFarmerName.textContent = state.profile.name;
    if (dom.headerStatusDot) {
      dom.headerStatusDot.classList.remove('status-pending');
      dom.headerStatusDot.classList.add('status-active');
    }
  } else {
    const placeholder = t.setUpProfile || 'Set up profile';
    if (dom.sidebarFarmerName) dom.sidebarFarmerName.textContent = placeholder;
    if (dom.sidebarProfileSub) dom.sidebarProfileSub.textContent = t.tapToPersonalize || 'Tap to personalize';
    if (dom.sidebarStatusDot) {
      dom.sidebarStatusDot.classList.remove('status-active');
      dom.sidebarStatusDot.classList.add('status-pending');
    }
    if (dom.headerFarmerName) dom.headerFarmerName.textContent = placeholder;
    if (dom.headerStatusDot) {
      dom.headerStatusDot.classList.remove('status-active');
      dom.headerStatusDot.classList.add('status-pending');
    }
  }

  const profileBadge = document.getElementById('sidebar-profile-badge');
  if (profileBadge) {
    profileBadge.textContent = isCompleted ? (t.statusReady || 'Ready') : (t.statusSetup || 'Setup');
  }
}


// -------------------------------------------------------------
// Navigation Controller
// -------------------------------------------------------------
function navigateToView(tabId) {
  state.activeTab = tabId;

  closeSidebar();

  dom.navTabs.forEach(tab => {
    const badge = tab.querySelector('.nav-badge-pill');
    if (tab.getAttribute('data-tab') === tabId) {
      tab.classList.add('active');
      if (badge) badge.classList.add('active-badge');
    } else {
      tab.classList.remove('active');
      if (badge) badge.classList.remove('active-badge');
    }
  });

  dom.tabPanes.forEach(pane => {
    if (pane.id === `view-${tabId}`) {
      pane.classList.add('active');
    } else {
      pane.classList.remove('active');
    }
  });

  if (tabId === 'market') {
    loadMarketData(state.marketCrop, state.marketRange, state.marketDate, state.marketVariety);
  } else if (tabId === 'weather') {
    loadWeatherData(state.profile.location || 'Guntur');
  } else if (tabId === 'crops') {
    loadCropsData();
  } else if (tabId === 'profile') {
    updateProfileViewUI();
  }
}

// -------------------------------------------------------------
// Core Interaction & Profile Deferral Logic
// -------------------------------------------------------------
function handleSendInput() {
  const text = dom.chatInput.value.trim();
  const image = state.selectedImageBase64;

  if (!text && !image) return;

  dom.chatInput.value = '';
  clearAttachment();

  const defaultPhotoPrompt = state.lang === 'te'
    ? 'ఈ పంట ఫోటోను పరిశీలించి తెగులు నివారణ తెలపండి'
    : state.lang === 'hi'
      ? 'इस फसल फोटो की जांच कर रोग व उपचार बताएं'
      : 'Analyze this crop photo for pest or disease diagnosis';

  handleInteraction({
    text: text || defaultPhotoPrompt,
    image: image,
    action: image ? 'crop_photo' : 'chat_message'
  });
}

/**
 * CHAT-FIRST FLOW:
 * - If profile is NOT completed:
 *   1. Preserve query in state.pendingMessage
 *   2. Open friendly profile modal without sending query to AI yet
 * - If profile IS completed:
 *   Proceed immediately with AI answer!
 */
function handleInteraction(interaction) {
  if (!state.profileCompleted) {
    // Preserve query
    state.pendingMessage = interaction;
    openProfileModal(false);
    return;
  }

  // Profile already exists: execute query immediately
  executeUserQuery(interaction);
}

function executeUserQuery(interaction) {
  // Render user message in chat
  const userBubble = createUserBubble(interaction.text, interaction.image);
  if (interaction.image) {
    const attachEl = userBubble.querySelector('.message-attachment');
    if (attachEl) {
      attachEl.addEventListener('click', () => openLightbox(interaction.image));
    }
  }
  dom.chatStream.appendChild(userBubble);
  dom.chatStream.scrollTop = dom.chatStream.scrollHeight;

  // Ensure active view is chat
  if (state.activeTab !== 'chat') {
    navigateToView('chat');
  }

  // Show typing / thinking indicator
  const typingIndicator = createTypingIndicator();
  dom.chatStream.appendChild(typingIndicator);
  dom.chatStream.scrollTop = dom.chatStream.scrollHeight;

  let streamReply = '';
  let streamBubble = null;
  let streamBody = null;

  // Use live streaming SSE response with smooth chunk appending
  api.sendChatStream({
    message: interaction.text,
    image: interaction.image,
    action: interaction.action,
    profile: state.profile,
    location: state.location,
    lang: state.lang,
    conversation_id: state.conversationId,
    onChunk: (chunk, convId) => {
      if (convId) {
        state.conversationId = convId;
        localStorage.setItem('kisanmitra_conv_id', convId);
      }
      if (typingIndicator && typingIndicator.parentNode) {
        typingIndicator.remove();
      }
      if (!streamBubble) {
        streamBubble = createBotBubble('', null, [], null, null, null, state.lang);
        streamBody = streamBubble.querySelector('.message-body');
        dom.chatStream.appendChild(streamBubble);
      }
      streamReply += chunk;
      if (streamBody) {
        streamBody.innerHTML = formatMarkdown(streamReply);
      }
      dom.chatStream.scrollTop = dom.chatStream.scrollHeight;
    },
    onDone: (res) => {
      if (res.conversation_id) {
        state.conversationId = res.conversation_id;
        localStorage.setItem('kisanmitra_conv_id', res.conversation_id);
      }
      if (typingIndicator && typingIndicator.parentNode) {
        typingIndicator.remove();
      }
      if (streamBubble && streamBubble.parentNode) {
        streamBubble.remove();
      }
      const botBubble = createBotBubble(
        res.reply,
        res.context_applied,
        res.suggested_actions,
        (suggestedText) => {
          handleInteraction({ text: suggestedText, image: null, action: 'suggestion' });
        },
        res.spoken_text,
        (spokenToReplay, replayBtn) => {
          VoiceController.speakText(spokenToReplay, replayBtn, res.detected_language);
        },
        res.detected_language || state.lang
      );
      dom.chatStream.appendChild(botBubble);
      dom.chatStream.scrollTop = dom.chatStream.scrollHeight;

      // Automatically speak the AI answer if the query originated via voice
      if (interaction.isVoice && (res.spoken_text || res.reply)) {
        VoiceController.speakText(res.spoken_text || res.reply, null, res.detected_language);
      }
    },
    onError: (err) => {
      console.warn('Streaming failed, attempting fallback to standard sendChat:', err);
      // Seamless fallback to non-streaming sendChat
      api.sendChat({
        message: interaction.text,
        image: interaction.image,
        action: interaction.action,
        profile: state.profile,
        location: state.location,
        lang: state.lang,
        conversation_id: state.conversationId
      })
      .then(response => {
        if (typingIndicator && typingIndicator.parentNode) typingIndicator.remove();
        if (streamBubble && streamBubble.parentNode) streamBubble.remove();
        if (response.conversation_id) {
          state.conversationId = response.conversation_id;
          localStorage.setItem('kisanmitra_conv_id', response.conversation_id);
        }
        const botBubble = createBotBubble(
          response.reply,
          response.context_applied,
          response.suggested_actions,
          (suggestedText) => {
            handleInteraction({ text: suggestedText, image: null, action: 'suggestion' });
          },
          response.spoken_text,
          (spokenToReplay, replayBtn) => {
            VoiceController.speakText(spokenToReplay, replayBtn, response.detected_language);
          },
          response.detected_language || state.lang
        );
        dom.chatStream.appendChild(botBubble);
        dom.chatStream.scrollTop = dom.chatStream.scrollHeight;

        if (interaction.isVoice && (response.spoken_text || response.reply)) {
          VoiceController.speakText(response.spoken_text || response.reply, null, response.detected_language);
        }
      })
      .catch(finalErr => {
        if (typingIndicator && typingIndicator.parentNode) typingIndicator.remove();
        if (streamBubble && streamBubble.parentNode) streamBubble.remove();
        console.error('Chat error:', finalErr);
        const errorBubble = createBotBubble(
          `We encountered a temporary connection issue. Please verify your connection or try again.\n\n*Error: ${finalErr.message}*`,
          null,
          ['Try again', 'Check market prices']
        );
        dom.chatStream.appendChild(errorBubble);
        dom.chatStream.scrollTop = dom.chatStream.scrollHeight;
      });
    }
  });
}

// -------------------------------------------------------------
// Profile Setup Modal Management
// -------------------------------------------------------------
function openProfileModal(isEditMode = false) {
  const t = translations[state.lang] || translations.en;

  // Populate form with existing data
  dom.inputName.value = state.profile.name || '';
  dom.inputLocation.value = state.profile.location || '';
  dom.inputSize.value = state.profile.farm_size || '';
  dom.inputVariety.value = state.profile.crop_variety || '';
  dom.inputSoil.value = state.profile.soil_type || '';
  dom.inputIrrigation.value = state.profile.irrigation_type || '';
  dom.inputStage.value = state.profile.growth_stage || '';

  renderCropChips(state.profile.crops || []);

  // Preserved Question Notice
  if (state.pendingMessage && !isEditMode) {
    dom.preservedQueryNotice.style.display = 'flex';
    dom.preservedQueryText.textContent = `"${state.pendingMessage.text}"`;
  } else {
    dom.preservedQueryNotice.style.display = 'none';
  }

  if (isEditMode) {
    dom.modalHeading.textContent = t.editProfileTitle;
    dom.modalSubheading.textContent = t.editProfileSubtitle;
    dom.modalSubmitBtnText.textContent = t.editProfileSaveBtn;
    if (dom.modalCloseBtn) dom.modalCloseBtn.style.display = 'block';
  } else {
    dom.modalHeading.textContent = t.modalHeading;
    dom.modalSubheading.textContent = t.modalSubheading;
    dom.modalSubmitBtnText.textContent = t.modalSaveBtn;
    if (dom.modalCloseBtn) dom.modalCloseBtn.style.display = 'none';
  }

  dom.modalBackdrop.classList.add('visible');
}

function closeProfileModal() {
  dom.modalBackdrop.classList.remove('visible');
}

function renderCropChips(selectedCrops) {
  dom.cropChipsContainer.innerHTML = '';
  const cropNames = cropTranslations[state.lang] || cropTranslations.en;
  POPULAR_CROPS.forEach(item => {
    const chip = document.createElement('button');
    chip.type = 'button';
    const isSelected = selectedCrops.includes(item.name);
    chip.className = `filter-chip ${isSelected ? 'selected' : ''}`;
    chip.setAttribute('data-crop', item.name);
    const locName = cropNames[item.name] || item.name;
    chip.innerHTML = `<span>${item.icon}</span> <span>${locName}</span>`;
    chip.addEventListener('click', () => {
      chip.classList.toggle('selected');
    });
    dom.cropChipsContainer.appendChild(chip);
  });
}

function getSelectedCrops() {
  const selected = [];
  dom.cropChipsContainer.querySelectorAll('.filter-chip.selected').forEach(c => {
    const canonical = c.getAttribute('data-crop');
    if (canonical) {
      selected.push(canonical);
    } else {
      const text = c.innerText.replace(/[^\w\s]/gi, '').trim();
      if (text) selected.push(text);
    }
  });

  const custom = dom.inputCustomCrops.value.trim();
  if (custom) {
    custom.split(',').forEach(crop => {
      const clean = crop.trim();
      if (clean && !selected.includes(clean)) {
        selected.push(clean);
      }
    });
  }
  return selected;
}

function toggleOptionalFields() {
  const isCurrentlyOpen = dom.optionalFieldsContainer.classList.contains('expanded');
  if (isCurrentlyOpen) {
    dom.optionalFieldsContainer.classList.remove('expanded');
    dom.optionalToggleBtn.querySelector('.toggle-arrow').textContent = '▼';
  } else {
    dom.optionalFieldsContainer.classList.add('expanded');
    dom.optionalToggleBtn.querySelector('.toggle-arrow').textContent = '▲';
  }
}

async function handleProfileFormSubmit(e) {
  e.preventDefault();

  const name = dom.inputName.value.trim();
  const location = dom.inputLocation.value.trim();
  const farmSize = dom.inputSize.value.trim();
  const crops = getSelectedCrops();

  // Validate required fields
  if (!name) {
    alert('Please enter your name.');
    dom.inputName.focus();
    return;
  }
  if (!location) {
    alert('Please enter your farm location.');
    dom.inputLocation.focus();
    return;
  }
  if (crops.length === 0) {
    alert('Please select or specify at least one crop.');
    return;
  }
  if (!farmSize) {
    alert('Please enter your farm size.');
    dom.inputSize.focus();
    return;
  }

  const payload = {
    name,
    location,
    crops,
    farm_size: farmSize,
    crop_variety: dom.inputVariety.value.trim(),
    soil_type: dom.inputSoil.value,
    irrigation_type: dom.inputIrrigation.value,
    growth_stage: dom.inputStage.value,
    completed: true
  };

  try {
    const res = await api.saveProfile(payload);
    state.profile = res.profile;
    state.profileCompleted = true;
    updateHeaderProfileUI(true);
    updateProfileViewUI();
    closeProfileModal();

    // AUTOMATICALLY RESUME PRESERVED USER QUERY
    if (state.pendingMessage) {
      const preserved = state.pendingMessage;
      state.pendingMessage = null;
      navigateToView('chat');
      // Executes seamlessly without requiring the farmer to retype
      executeUserQuery(preserved);
    }
  } catch (err) {
    console.error('Failed to save profile:', err);
    alert(`Could not save profile: ${err.message}`);
  }
}

async function handleResetProfile() {
  if (confirm('Reset profile to initial state? This allows you to test the onboarding prompt again.')) {
    try {
      await api.resetProfile();
      state.profileCompleted = false;
      state.profile = {
        name: '',
        location: '',
        crops: [],
        farm_size: '',
        crop_variety: '',
        soil_type: '',
        irrigation_type: '',
        growth_stage: ''
      };
      updateHeaderProfileUI(false);
      updateProfileViewUI();
      navigateToView('chat');
    } catch (err) {
      console.error('Reset error:', err);
    }
  }
}

// -------------------------------------------------------------
// Data Loaders for Secondary Views
// -------------------------------------------------------------
function updateProfileViewUI() {
  const p = state.profile;
  const t = translations[state.lang] || translations.en;
  const cropNames = cropTranslations[state.lang] || cropTranslations.en;

  dom.profileDisplayName.textContent = p.name || t.notSet;
  dom.profileDisplayLocation.textContent = p.location ? `📍 ${p.location}` : t.locationNotSet;
  
  if (p.crops && p.crops.length > 0) {
    dom.profileDisplayCrops.textContent = p.crops.map(c => cropNames[c] || c).join(', ');
  } else {
    dom.profileDisplayCrops.textContent = t.noneSelected;
  }

  dom.profileDisplaySize.textContent = p.farm_size || t.notSet;
  dom.profileDisplayVariety.textContent = p.crop_variety || 'Standard / Local';
  dom.profileDisplaySoil.textContent = p.soil_type || 'Red Loam';
  dom.profileDisplayIrrigation.textContent = p.irrigation_type || 'Drip Irrigation';
  dom.profileDisplayStage.textContent = p.growth_stage || 'Flowering / Fruiting';
}

function renderCurrentMarketPage() {
  if (!state.marketDataCache || !dom.marketViewContainer) return;
  renderMarketPage({
    marketPayload: state.marketDataCache,
    container: dom.marketViewContainer,
    currentCrop: state.marketCrop,
    currentRange: state.marketRange,
    currentDate: state.marketDate,
    currentVariety: state.marketVariety,
    currentLang: state.lang,
    searchQuery: state.marketSearchQuery,
    sortCol: state.marketSortCol,
    sortDir: state.marketSortDir,
    showVarietyCompare: state.showVarietyCompare,
    onToggleVarietyCompare: () => {
      state.showVarietyCompare = !state.showVarietyCompare;
      renderCurrentMarketPage();
    },
    onSelectCrop: (newCrop) => {
      state.marketCrop = newCrop;
      state.marketVariety = 'all';
      state.showVarietyCompare = false;
      loadMarketData(newCrop, state.marketRange, state.marketDate, 'all');
    },
    onSelectRange: (newRange) => {
      state.marketRange = newRange;
      renderCurrentMarketPage();
    },
    onSelectDate: (newDate) => {
      state.marketDate = newDate;
      loadMarketData(state.marketCrop, state.marketRange, newDate, state.marketVariety);
    },
    onSelectVariety: (newVariety) => {
      state.marketVariety = newVariety;
      loadMarketData(state.marketCrop, state.marketRange, state.marketDate, newVariety);
    },
    onSearch: (query, shouldRerender = true) => {
      state.marketSearchQuery = query;
      if (shouldRerender) {
        renderCurrentMarketPage();
      }
    },
    onSort: (col) => {
      if (state.marketSortCol === col) {
        state.marketSortDir = state.marketSortDir === 'asc' ? 'desc' : 'asc';
      } else {
        state.marketSortCol = col;
        state.marketSortDir = (col === 'market' || col === 'district' || col === 'crop' || col === 'variety') ? 'asc' : 'desc';
      }
      renderCurrentMarketPage();
    }
  });
}

async function loadMarketData(crop = state.marketCrop, range = state.marketRange, date = state.marketDate, variety = state.marketVariety) {
  try {
    state.marketCrop = crop || 'Tomato';
    state.marketRange = range || '7D';
    state.marketDate = date || 'Yesterday';
    state.marketVariety = variety || 'all';

    const res = await api.getMarketPrices(state.marketCrop, '', state.marketDate, state.marketVariety);
    state.marketDataCache = res;
    renderCurrentMarketPage();
  } catch (err) {
    console.error('Market data error:', err);
  }
}

async function loadWeatherData(location = 'Guntur') {
  try {
    const res = await api.getWeather(location);
    state.weatherDataCache = res;
    renderWeatherView(res, {
      location: dom.weatherLocation,
      temp: dom.weatherTemp,
      condition: dom.weatherCondition,
      humidity: dom.weatherHumidity,
      rain: dom.weatherRain,
      wind: dom.weatherWind,
      advisory: dom.weatherAdvisory,
      forecastContainer: dom.weatherForecastContainer
    }, state.lang);
  } catch (err) {
    console.error('Weather data error:', err);
  }
}

async function loadCropsData() {
  try {
    const res = await api.getCropAdvisories();
    renderCropCards(res.data, dom.cropsListContainer, state.lang);
  } catch (err) {
    console.error('Crops advisory error:', err);
  }
}


// -------------------------------------------------------------
// Media & Input Helpers
// -------------------------------------------------------------
/**
 * Advanced Client-Side Image Compressor & Optimizer
 * Scales down large smartphone camera photos (5MB - 15MB) to high-clarity ~150KB-250KB JPEGs.
 * Runs instantly via Offscreen Canvas, preventing browser memory leaks and slow uploads.
 */
async function compressAndOptimizeImage(fileOrBlob, maxDimension = 1280, quality = 0.82) {
  return new Promise((resolve, reject) => {
    const originalSizeKb = fileOrBlob.size ? Math.round(fileOrBlob.size / 1024) : 0;
    const reader = new FileReader();

    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        let { width, height } = img;

        // Downscale while strictly preserving aspect ratio
        if (width > maxDimension || height > maxDimension) {
          if (width > height) {
            height = Math.round((height * maxDimension) / width);
            width = maxDimension;
          } else {
            width = Math.round((width * maxDimension) / height);
            height = maxDimension;
          }
        }

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        const compressedBase64 = canvas.toDataURL('image/jpeg', quality);
        const head = 'data:image/jpeg;base64,';
        const sizeKb = Math.round(((compressedBase64.length - head.length) * 3) / 4 / 1024);

        resolve({
          base64: compressedBase64,
          sizeKb: sizeKb || 1,
          originalSizeKb: originalSizeKb || sizeKb,
          width,
          height
        });
      };
      img.onerror = (err) => reject(err);
      img.src = e.target.result;
    };
    reader.onerror = (err) => reject(err);
    reader.readAsDataURL(fileOrBlob);
  });
}

/**
 * Live Camera Controller
 * Manages device camera stream via getUserMedia with rear/environment camera preference,
 * camera flipping, targeting guidelines, frame capture, and graceful fallbacks.
 */
const CameraController = {
  stream: null,
  facingMode: 'environment', // Rear camera by default for farm plants
  activeSnapshotBase64: null,
  activeSnapshotMeta: null,

  async openCamera() {
    closePhotoOptionsModal();

    // Check getUserMedia availability (requires HTTPS or localhost in modern browsers)
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      if (dom.cameraCaptureInput) {
        dom.cameraCaptureInput.click();
      } else if (dom.photoInput) {
        dom.photoInput.click();
      }
      return;
    }

    if (dom.cameraModal) {
      dom.cameraModal.classList.add('visible');
    }
    this.resetToLiveView();
    await this.startStream();
  },

  async startStream() {
    this.stopStream();
    try {
      const constraints = {
        video: {
          facingMode: { ideal: this.facingMode },
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      };
      this.stream = await navigator.mediaDevices.getUserMedia(constraints);
      if (dom.cameraVideo) {
        dom.cameraVideo.setAttribute('playsinline', '');
        dom.cameraVideo.setAttribute('muted', '');
        dom.cameraVideo.playsInline = true;
        dom.cameraVideo.muted = true;
        dom.cameraVideo.srcObject = this.stream;
        await dom.cameraVideo.play();
      }
    } catch (err) {
      console.warn('Camera stream error, falling back to native capture:', err);
      this.closeCamera();
      // On permission rejection, insecure HTTP origin, or device without webcam, seamlessly trigger native mobile camera
      if (dom.cameraCaptureInput) {
        dom.cameraCaptureInput.click();
      } else if (dom.photoInput) {
        dom.photoInput.click();
      }
    }
  },

  stopStream() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    if (dom.cameraVideo) {
      dom.cameraVideo.srcObject = null;
    }
  },

  async flipCamera() {
    this.facingMode = this.facingMode === 'environment' ? 'user' : 'environment';
    await this.startStream();
  },

  snapPhoto() {
    if (!dom.cameraVideo || !dom.cameraCanvas) return;

    // Visual shutter flash effect
    if (dom.cameraShutterFlash) {
      dom.cameraShutterFlash.classList.add('flashing');
      setTimeout(() => dom.cameraShutterFlash.classList.remove('flashing'), 180);
    }

    const video = dom.cameraVideo;
    const canvas = dom.cameraCanvas;
    const width = video.videoWidth || 640;
    const height = video.videoHeight || 480;

    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, width, height);

    canvas.toBlob(async (blob) => {
      if (!blob) return;
      try {
        const optimized = await compressAndOptimizeImage(blob);
        this.activeSnapshotBase64 = optimized.base64;
        this.activeSnapshotMeta = optimized;

        if (dom.cameraSnapshotPreview) {
          dom.cameraSnapshotPreview.src = this.activeSnapshotBase64;
          dom.cameraSnapshotPreview.style.display = 'block';
        }
        if (dom.cameraVideo) {
          dom.cameraVideo.style.display = 'none';
        }

        if (dom.cameraCaptureControls) dom.cameraCaptureControls.style.display = 'none';
        if (dom.cameraReviewControls) dom.cameraReviewControls.style.display = 'flex';
      } catch (e) {
        console.error('Snapshot processing error:', e);
      }
    }, 'image/jpeg', 0.9);
  },

  resetToLiveView() {
    this.activeSnapshotBase64 = null;
    this.activeSnapshotMeta = null;
    if (dom.cameraSnapshotPreview) {
      dom.cameraSnapshotPreview.style.display = 'none';
      dom.cameraSnapshotPreview.src = '';
    }
    if (dom.cameraVideo) {
      dom.cameraVideo.style.display = 'block';
    }
    if (dom.cameraCaptureControls) dom.cameraCaptureControls.style.display = 'flex';
    if (dom.cameraReviewControls) dom.cameraReviewControls.style.display = 'none';
  },

  retake() {
    this.resetToLiveView();
  },

  confirmPhoto() {
    if (this.activeSnapshotBase64) {
      setAttachedPhoto(this.activeSnapshotBase64, this.activeSnapshotMeta);
    }
    this.closeCamera();
  },

  closeCamera() {
    this.stopStream();
    this.resetToLiveView();
    if (dom.cameraModal) {
      dom.cameraModal.classList.remove('visible');
    }
  }
};

// Photo Options Modal Management
function openPhotoOptionsModal() {
  if (dom.photoOptionsModal) {
    dom.photoOptionsModal.classList.add('visible');
  }
}

function closePhotoOptionsModal() {
  if (dom.photoOptionsModal) {
    dom.photoOptionsModal.classList.remove('visible');
  }
}

// Lightbox Modal Management
function openLightbox(imgSrc, caption = '') {
  if (!dom.lightboxModal || !dom.lightboxImg) return;
  dom.lightboxImg.src = imgSrc;
  const capEl = document.getElementById('lightbox-caption');
  if (capEl) {
    capEl.textContent = caption || (translations[state.lang] || translations.en).lightboxCaption || 'Crop Leaf Detail';
  }
  dom.lightboxModal.classList.add('visible');
}

function closeLightbox() {
  if (dom.lightboxModal) {
    dom.lightboxModal.classList.remove('visible');
  }
}

// Mobile Share Modal Management
async function loadNetworkInfo() {
  try {
    const data = await api.getNetworkInfo();
    const publicUrl = data.public_url || data.local_url;
    const localUrl = data.local_url;

    if (dom.publicUrlInput) dom.publicUrlInput.value = publicUrl;
    if (dom.openPublicUrlBtn) dom.openPublicUrlBtn.href = publicUrl;
    if (dom.localUrlInput) dom.localUrlInput.value = localUrl;
    if (dom.openLocalUrlBtn) dom.openLocalUrlBtn.href = localUrl;

    if (dom.mobileQrImg) {
      const qrTarget = data.preferred_url || publicUrl;
      dom.mobileQrImg.src = data.qr_code_url || `https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=${encodeURIComponent(qrTarget)}`;
    }
  } catch (err) {
    console.warn('Could not load network info:', err);
    const fallbackUrl = window.location.href;
    if (dom.publicUrlInput) dom.publicUrlInput.value = fallbackUrl;
    if (dom.openPublicUrlBtn) dom.openPublicUrlBtn.href = fallbackUrl;
    if (dom.mobileQrImg) {
      dom.mobileQrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=${encodeURIComponent(fallbackUrl)}`;
    }
  }
}

function openMobileShareModal() {
  if (dom.mobileShareModal) {
    dom.mobileShareModal.style.display = 'flex';
    dom.mobileShareModal.classList.add('visible');
    loadNetworkInfo();
  }
  closeSidebar();
}

function closeMobileShareModal() {
  if (dom.mobileShareModal) {
    dom.mobileShareModal.style.display = 'none';
    dom.mobileShareModal.classList.remove('visible');
  }
}

function copyToClipboard(text, btnElement) {
  if (!text) return;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => showCopiedFeedback(btnElement));
  } else {
    const temp = document.createElement('input');
    temp.value = text;
    document.body.appendChild(temp);
    temp.select();
    try {
      document.execCommand('copy');
      showCopiedFeedback(btnElement);
    } catch (e) {
      console.warn('Copy failed:', e);
    }
    document.body.removeChild(temp);
  }
}

function showCopiedFeedback(btn) {
  if (!btn) return;
  const originalHtml = btn.innerHTML;
  const t = translations[state.lang] || translations.en;
  btn.innerHTML = `<span>✓</span> <span>${t.copied || 'Copied!'}</span>`;
  btn.classList.add('copied-state');
  setTimeout(() => {
    btn.innerHTML = originalHtml;
    btn.classList.remove('copied-state');
  }, 2000);
}

// Attachment State Helper
function setAttachedPhoto(base64Data, meta = null) {
  state.selectedImageBase64 = base64Data;
  state.selectedImageMeta = meta;

  if (dom.attachmentPreview) {
    dom.attachmentPreview.src = base64Data;
  }

  const t = translations[state.lang] || translations.en;
  if (dom.attachmentMainText) {
    dom.attachmentMainText.textContent = t.photoAttachedText || 'Crop photo ready for diagnosis';
  }

  if (dom.attachmentSizeBadge) {
    if (meta && meta.sizeKb) {
      dom.attachmentSizeBadge.textContent = `${meta.sizeKb} KB`;
      dom.attachmentSizeBadge.style.display = 'inline-flex';
    } else {
      dom.attachmentSizeBadge.style.display = 'none';
    }
  }

  if (dom.attachmentChangeBtn) {
    dom.attachmentChangeBtn.textContent = `🔄 ${t.changePhoto || 'Change'}`;
  }

  if (dom.attachmentBar) {
    dom.attachmentBar.style.display = 'flex';
  }

  // Set chat input placeholder guidance
  if (dom.chatInput && !dom.chatInput.value.trim()) {
    dom.chatInput.placeholder = t.analyzePhoto || 'Analyze my crop photo for pest or disease';
  }
}

async function handleFileSelected(e) {
  const file = e.target.files[0];
  if (!file) return;

  closePhotoOptionsModal();
  try {
    const optimized = await compressAndOptimizeImage(file);
    setAttachedPhoto(optimized.base64, optimized);
  } catch (err) {
    console.error('File compression error:', err);
    // Fallback: direct read
    const reader = new FileReader();
    reader.onload = (event) => {
      setAttachedPhoto(event.target.result);
    };
    reader.readAsDataURL(file);
  }
}

function clearAttachment() {
  state.selectedImageBase64 = null;
  state.selectedImageMeta = null;
  if (dom.photoInput) dom.photoInput.value = '';
  if (dom.cameraCaptureInput) dom.cameraCaptureInput.value = '';
  if (dom.attachmentBar) dom.attachmentBar.style.display = 'none';
  const t = translations[state.lang] || translations.en;
  if (dom.chatInput) dom.chatInput.placeholder = t.inputPlaceholder;
}

// Drag and Drop & Clipboard Paste setup
function setupDragAndDrop() {
  const chatView = document.getElementById('view-chat');
  if (!chatView) return;

  chatView.addEventListener('dragover', (e) => {
    e.preventDefault();
    if (dom.chatDragOverlay) dom.chatDragOverlay.classList.add('active');
  });

  chatView.addEventListener('dragleave', (e) => {
    if (!chatView.contains(e.relatedTarget)) {
      if (dom.chatDragOverlay) dom.chatDragOverlay.classList.remove('active');
    }
  });

  chatView.addEventListener('drop', async (e) => {
    e.preventDefault();
    if (dom.chatDragOverlay) dom.chatDragOverlay.classList.remove('active');

    const files = e.dataTransfer ? e.dataTransfer.files : null;
    if (files && files.length > 0 && files[0].type.startsWith('image/')) {
      try {
        const optimized = await compressAndOptimizeImage(files[0]);
        setAttachedPhoto(optimized.base64, optimized);
      } catch (err) {
        console.error('Drop image error:', err);
      }
    }
  });

  // Global paste handler for screenshots or copied images
  document.addEventListener('paste', async (e) => {
    const items = e.clipboardData ? e.clipboardData.items : null;
    if (!items) return;
    for (let item of items) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile();
        if (file) {
          try {
            const optimized = await compressAndOptimizeImage(file);
            setAttachedPhoto(optimized.base64, optimized);
            break;
          } catch (err) {
            console.error('Pasted image compression error:', err);
          }
        }
      }
    }
  });
}

function handleVoiceToggle() {
  VoiceController.toggleRecording();
}

/**
 * Advanced Multilingual Voice Assistant Controller
 * Provides first-class voice interaction:
 * - Real-time speech recognition (Telugu, Hindi, Indian English)
 * - Animated audio waveforms, pulsing halo, and review states
 * - Graceful auto-send countdown (2.5s) with review/edit overrides
 * - Natural spoken AI responses via Web Speech Synthesis
 * - Floating speech playback controller (pause, resume, stop)
 * - In-message replay buttons for re-listening to answers
 */
const VoiceController = {
  recognition: null,
  isListening: false,
  isSpeaking: false,
  isPaused: false,
  currentUtterance: null,
  activeReplayBtn: null,
  countdownInterval: null,
  currentTranscript: '',
  voices: [],

  init() {
    this.initVoices();
  },

  initVoices() {
    if ('speechSynthesis' in window) {
      const load = () => {
        try {
          this.voices = window.speechSynthesis.getVoices() || [];
        } catch (e) {
          this.voices = [];
        }
      };
      load();
      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = load;
      }
    }
  },

  getBestVoice(langCode) {
    if (!this.voices || this.voices.length === 0) {
      if ('speechSynthesis' in window) {
        try {
          this.voices = window.speechSynthesis.getVoices() || [];
        } catch (e) {
          this.voices = [];
        }
      }
    }

    const target = (langCode || state.lang || 'en').toLowerCase();
    const prefix = target === 'te' ? 'te' : target === 'hi' ? 'hi' : 'en';

    // 1. Direct language tag match (e.g. te-IN, hi-IN, en-IN)
    const exact = this.voices.find(v => v.lang && v.lang.toLowerCase().replace('_', '-').startsWith(prefix));
    if (exact) return exact;

    // 2. Cultural regional fallbacks
    if (prefix === 'te') {
      const hi = this.voices.find(v => v.lang && v.lang.toLowerCase().startsWith('hi'));
      if (hi) return hi;
    }
    const enIn = this.voices.find(v => v.lang && v.lang.toLowerCase().includes('en-in'));
    if (enIn) return enIn;

    const anyEn = this.voices.find(v => v.lang && v.lang.toLowerCase().startsWith('en'));
    return anyEn || (this.voices.length > 0 ? this.voices[0] : null);
  },

  cleanTextForSpeech(rawText) {
    if (!rawText) return '';
    let text = rawText;

    // Remove markdown links [title](url) -> title
    text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');

    // Remove markdown styling characters
    text = text.replace(/[*#_`>|~]/g, ' ');

    // Conversational currency replacement for natural Indian pronunciation
    if (state.lang === 'te') {
      text = text.replace(/₹\s*(\d+(?:,\d+)*(?:\.\d+)?)/g, '$1 రూపాయలు');
      text = text.replace(/₹/g, ' రూపాయలు ');
    } else if (state.lang === 'hi') {
      text = text.replace(/₹\s*(\d+(?:,\d+)*(?:\.\d+)?)/g, '$1 रुपये');
      text = text.replace(/₹/g, ' रुपये ');
    } else {
      text = text.replace(/₹\s*(\d+(?:,\d+)*(?:\.\d+)?)/g, '$1 rupees');
      text = text.replace(/₹/g, ' rupees ');
    }

    // Collapse multiple spaces
    return text.replace(/\s+/g, ' ').trim();
  },

  speakText(text, replayButton = null, langCode = null) {
    if (!('speechSynthesis' in window)) return;

    this.stopSpeaking();
    const spokenContent = this.cleanTextForSpeech(text);
    if (!spokenContent) return;

    const effectiveLang = langCode || state.lang || 'en';
    const t = translations[effectiveLang] || translations[state.lang] || translations.en;
    const utterance = new SpeechSynthesisUtterance(spokenContent);
    const voice = this.getBestVoice(effectiveLang);

    if (voice) {
      utterance.voice = voice;
      utterance.lang = voice.lang;
    } else {
      utterance.lang = effectiveLang === 'te' ? 'te-IN' : effectiveLang === 'hi' ? 'hi-IN' : 'en-IN';
    }

    utterance.rate = 0.95; // Farmer-friendly, calm natural cadence
    utterance.pitch = 1.0;

    this.currentUtterance = utterance;
    this.isSpeaking = true;
    this.isPaused = false;
    this.activeReplayBtn = replayButton;
    this.setDockState('RESPONDING', spokenContent);

    if (this.activeReplayBtn) {
      this.activeReplayBtn.classList.add('speaking');
    }

    // Show floating speaking status bar
    if (dom.speakingStatusBar) {
      dom.speakingStatusBar.classList.add('active');
      if (dom.speakingStatusText) {
        dom.speakingStatusText.textContent = t.voiceSpeaking || 'KisanMitra is speaking...';
      }
      if (dom.speakingPauseBtn) {
        dom.speakingPauseBtn.textContent = `⏸️ ${t.voicePause || 'Pause'}`;
      }
    }

    utterance.onend = () => {
      this.finishSpeaking();
    };

    utterance.onerror = (e) => {
      console.warn('Speech synthesis error:', e);
      this.finishSpeaking();
    };

    window.speechSynthesis.speak(utterance);
  },

  finishSpeaking() {
    this.isSpeaking = false;
    this.isPaused = false;
    this.currentUtterance = null;
    if (this.activeReplayBtn) {
      this.activeReplayBtn.classList.remove('speaking');
      this.activeReplayBtn = null;
    }
    if (dom.speakingStatusBar) {
      dom.speakingStatusBar.classList.remove('active');
    }
    this.setDockState('IDLE');
  },

  stopSpeaking() {
    if ('speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
      } catch (e) {}
    }
    this.finishSpeaking();
  },

  togglePauseSpeaking() {
    if (!('speechSynthesis' in window) || !this.isSpeaking) return;
    const t = translations[state.lang] || translations.en;
    if (this.isPaused) {
      window.speechSynthesis.resume();
      this.isPaused = false;
      if (dom.speakingPauseBtn) {
        dom.speakingPauseBtn.textContent = `⏸️ ${t.voicePause || 'Pause'}`;
      }
      const wave = dom.speakingStatusBar ? dom.speakingStatusBar.querySelector('.speaking-mini-wave') : null;
      if (wave) wave.style.opacity = '1';
    } else {
      window.speechSynthesis.pause();
      this.isPaused = true;
      if (dom.speakingPauseBtn) {
        dom.speakingPauseBtn.textContent = `▶️ ${t.voiceResume || 'Resume'}`;
      }
      const wave = dom.speakingStatusBar ? dom.speakingStatusBar.querySelector('.speaking-mini-wave') : null;
      if (wave) wave.style.opacity = '0.35';
    }
  },

  // ----------------- Speech Recognition -----------------
  toggleRecording() {
    if (this.isListening) {
      this.stopListening();
    } else {
      this.startListening();
    }
  },

  startListening() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const t = translations[state.lang] || translations.en;

    if (!SpeechRecognition) {
      this.showDockError(t.voiceErrorUnsupported || 'Voice recognition is not supported in this browser.');
      return;
    }

    // Stop speaking if AI is currently talking
    this.stopSpeaking();
    this.clearCountdown();

    try {
      this.recognition = new SpeechRecognition();
    } catch (err) {
      this.showDockError(t.voiceErrorUnsupported || 'Voice recognition is not supported in this browser.');
      return;
    }

    // Map language to regional Indian locales
    this.recognition.lang = state.lang === 'te' ? 'te-IN' : state.lang === 'hi' ? 'hi-IN' : 'en-IN';
    this.recognition.interimResults = true;
    this.recognition.maxAlternatives = 1;
    this.recognition.continuous = false;

    this.currentTranscript = '';
    this.setDockState('LISTENING');

    this.recognition.onstart = () => {
      this.isListening = true;
      state.isRecordingVoice = true;
      if (dom.voiceBtn) dom.voiceBtn.classList.add('voice-active');
    };

    this.recognition.onresult = (event) => {
      let interim = '';
      let final = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        const item = event.results[i];
        if (item.isFinal) {
          final += item[0].transcript;
        } else {
          interim += item[0].transcript;
        }
      }
      const display = (final || interim).trim();
      if (display) {
        this.currentTranscript = display;
        if (dom.voiceTranscriptText) {
          dom.voiceTranscriptText.textContent = `“${display}”`;
          dom.voiceTranscriptText.classList.remove('placeholder');
        }
      }
    };

    this.recognition.onerror = (event) => {
      console.warn('SpeechRecognition error:', event.error);
      this.isListening = false;
      state.isRecordingVoice = false;
      if (dom.voiceBtn) dom.voiceBtn.classList.remove('voice-active');

      if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        this.showDockError(t.voiceErrorPermission || 'Microphone permission is required for voice interaction.');
      } else if (event.error === 'no-speech' && !this.currentTranscript) {
        this.showDockError(t.voiceErrorNoSpeech || "Sorry, I couldn't hear that clearly.");
      } else if (this.currentTranscript && this.currentTranscript.trim().length > 0) {
        // Fallback: If partial transcript was captured, show review
        this.transitionToReview();
      } else {
        this.showDockError(t.voiceErrorNoSpeech || "Sorry, I couldn't hear that clearly.");
      }
    };

    this.recognition.onend = () => {
      this.isListening = false;
      state.isRecordingVoice = false;
      if (dom.voiceBtn) dom.voiceBtn.classList.remove('voice-active');

      if (this.currentTranscript && this.currentTranscript.trim().length > 0) {
        this.transitionToReview();
      } else {
        // If dock is active and waiting without text
        if (dom.voiceDock && dom.voiceDock.classList.contains('active')) {
          if (!dom.voiceCountdownBar || dom.voiceCountdownBar.style.display !== 'block') {
            this.showDockError(t.voiceErrorNoSpeech || "Sorry, I couldn't hear that clearly.");
          }
        }
      }
    };

    try {
      this.recognition.start();
    } catch (e) {
      console.warn('Recognition start error:', e);
      this.showDockError(t.voiceErrorPermission || 'Microphone permission is required.');
    }
  },

  stopListening() {
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {}
    }
    this.isListening = false;
    state.isRecordingVoice = false;
    if (dom.voiceBtn) dom.voiceBtn.classList.remove('voice-active');
  },

  cancelVoiceInput() {
    this.clearCountdown();
    this.stopListening();
    this.hideDock();
  },

  transitionToReview() {
    this.stopListening();
    this.setDockState('REVIEW');
    this.startAutoSendCountdown();
  },

  startAutoSendCountdown() {
    this.clearCountdown();
    if (!this.currentTranscript) return;

    if (dom.voiceCountdownBar) {
      dom.voiceCountdownBar.style.display = 'block';
    }
    if (dom.voiceCountdownFill) {
      dom.voiceCountdownFill.style.width = '100%';
    }

    const durationMs = 2500;
    const stepMs = 50;
    let elapsedMs = 0;

    this.countdownInterval = setInterval(() => {
      elapsedMs += stepMs;
      const remainingPct = Math.max(0, 100 - (elapsedMs / durationMs) * 100);
      if (dom.voiceCountdownFill) {
        dom.voiceCountdownFill.style.width = `${remainingPct}%`;
      }
      if (elapsedMs >= durationMs) {
        this.clearCountdown();
        this.dispatchVoiceQuery(this.currentTranscript);
      }
    }, stepMs);
  },

  clearCountdown() {
    if (this.countdownInterval) {
      clearInterval(this.countdownInterval);
      this.countdownInterval = null;
    }
    if (dom.voiceCountdownBar) {
      dom.voiceCountdownBar.style.display = 'none';
    }
  },

  editVoiceInput() {
    this.clearCountdown();
    this.stopListening();
    const text = this.currentTranscript;
    this.hideDock();
    if (dom.chatInput) {
      dom.chatInput.value = text;
      dom.chatInput.focus();
    }
  },

  sendVoiceInputNow() {
    this.clearCountdown();
    this.dispatchVoiceQuery(this.currentTranscript);
  },

  dispatchVoiceQuery(text) {
    if (!text || !text.trim()) {
      this.hideDock();
      return;
    }
    this.clearCountdown();
    this.setDockState('PROCESSING');

    const queryText = text.trim();
    this.currentTranscript = '';

    // Route through chat-first handler with voice tag preserved
    if (!state.profileCompleted) {
      state.pendingMessage = {
        text: queryText,
        image: null,
        action: 'voice_query',
        isVoice: true
      };
      openProfileModal(false);
      return;
    }

    executeUserQuery({
      text: queryText,
      image: null,
      action: 'voice_query',
      isVoice: true
    });
  },

  setDockState(stateName, extraContent = null) {
    const t = translations[state.lang] || translations.en;
    if (!dom.voiceDock) return;

    if (stateName === 'IDLE') {
      this.hideDock();
      return;
    }

    dom.voiceDock.classList.add('active');

    if (stateName === 'LISTENING') {
      if (dom.voiceMicHalo) {
        dom.voiceMicHalo.className = 'voice-mic-halo pulse';
        dom.voiceMicHalo.textContent = '🎙️';
      }
      if (dom.voiceWaveform) dom.voiceWaveform.className = 'voice-waveform-container active';
      if (dom.voiceStatusHeading) dom.voiceStatusHeading.textContent = t.voiceListening || 'Listening...';
      if (dom.voiceTranscriptText) {
        dom.voiceTranscriptText.textContent = `“${t.voiceSpeakPrompt || 'Speak your question...'}”`;
        dom.voiceTranscriptText.classList.add('placeholder');
      }
      this.clearCountdown();
      this.renderDockActions([
        { label: `❌ ${t.voiceCancel || 'Cancel'}`, cls: 'voice-btn-secondary', onClick: () => this.cancelVoiceInput() },
        { label: `⏹️ ${t.voiceStop || 'Stop'}`, cls: 'voice-btn-primary', onClick: () => {
          if (this.currentTranscript) {
            this.transitionToReview();
          } else {
            this.stopListening();
          }
        }}
      ]);
    } else if (stateName === 'PROCESSING') {
      if (dom.voiceMicHalo) {
        dom.voiceMicHalo.className = 'voice-mic-halo processing';
        dom.voiceMicHalo.textContent = '⏳';
      }
      if (dom.voiceWaveform) dom.voiceWaveform.className = 'voice-waveform-container';
      if (dom.voiceStatusHeading) dom.voiceStatusHeading.textContent = t.voiceProcessing || 'Understanding your question...';
      this.renderDockActions([]);
    } else if (stateName === 'REVIEW') {
      if (dom.voiceMicHalo) {
        dom.voiceMicHalo.className = 'voice-mic-halo';
        dom.voiceMicHalo.textContent = '💬';
      }
      if (dom.voiceWaveform) dom.voiceWaveform.className = 'voice-waveform-container';
      if (dom.voiceStatusHeading) dom.voiceStatusHeading.textContent = t.voiceReviewHeading || 'Recognized Question:';
      if (dom.voiceTranscriptText) {
        dom.voiceTranscriptText.textContent = `“${this.currentTranscript}”`;
        dom.voiceTranscriptText.classList.remove('placeholder');
      }
      this.renderDockActions([
        { label: `✏️ ${t.voiceEdit || 'Edit'}`, cls: 'voice-btn-secondary', onClick: () => this.editVoiceInput() },
        { label: `❌ ${t.voiceCancel || 'Cancel'}`, cls: 'voice-btn-secondary', onClick: () => this.cancelVoiceInput() },
        { label: `➔ ${t.voiceSend || 'Send'}`, cls: 'voice-btn-primary', onClick: () => this.sendVoiceInputNow() }
      ]);
    } else if (stateName === 'RESPONDING') {
      if (dom.voiceMicHalo) {
        dom.voiceMicHalo.className = 'voice-mic-halo pulse';
        dom.voiceMicHalo.textContent = '🔊';
      }
      if (dom.voiceWaveform) dom.voiceWaveform.className = 'voice-waveform-container active';
      if (dom.voiceStatusHeading) dom.voiceStatusHeading.textContent = t.voiceSpeaking || 'KisanMitra is speaking...';
      if (dom.voiceTranscriptText && extraContent) {
        dom.voiceTranscriptText.textContent = `“${extraContent}”`;
        dom.voiceTranscriptText.classList.remove('placeholder');
      }
      this.clearCountdown();
      this.renderDockActions([
        { label: `⏹️ ${t.voiceStop || 'Stop'}`, cls: 'voice-btn-secondary', onClick: () => this.stopSpeaking() },
        { label: `🔄 ${t.voiceReplay || 'Replay'}`, cls: 'voice-btn-primary', onClick: () => this.speakText(extraContent) }
      ]);
    } else if (stateName === 'ERROR') {
      this.showDockError(extraContent || t.voiceErrorNoSpeech || 'Voice assistance error');
    }
  },

  showDockError(msg) {
    const t = translations[state.lang] || translations.en;
    this.clearCountdown();
    if (!dom.voiceDock) return;
    dom.voiceDock.classList.add('active');

    if (dom.voiceMicHalo) {
      dom.voiceMicHalo.className = 'voice-mic-halo';
      dom.voiceMicHalo.textContent = '⚠️';
    }
    if (dom.voiceWaveform) dom.voiceWaveform.className = 'voice-waveform-container';
    if (dom.voiceStatusHeading) dom.voiceStatusHeading.textContent = msg;
    if (dom.voiceTranscriptText) {
      dom.voiceTranscriptText.textContent = '';
      dom.voiceTranscriptText.classList.add('placeholder');
    }

    this.renderDockActions([
      { label: `🔄 ${t.voiceTryAgain || 'Try Again'}`, cls: 'voice-btn-primary', onClick: () => this.startListening() },
      { label: `⌨️ ${t.voiceTypeInstead || 'Type Instead'}`, cls: 'voice-btn-secondary', onClick: () => {
        this.hideDock();
        if (dom.chatInput) dom.chatInput.focus();
      }}
    ]);
  },

  renderDockActions(buttons) {
    if (!dom.voiceActionsRow) return;
    dom.voiceActionsRow.innerHTML = '';
    buttons.forEach(b => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = b.cls;
      btn.textContent = b.label;
      btn.addEventListener('click', b.onClick);
      dom.voiceActionsRow.appendChild(btn);
    });
  },

  hideDock() {
    this.clearCountdown();
    if (dom.voiceDock) {
      dom.voiceDock.classList.remove('active');
    }
    if (dom.voiceBtn) {
      dom.voiceBtn.classList.remove('voice-active');
    }
    state.isRecordingVoice = false;
  }
};
