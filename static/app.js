// Minimal & Sleek Ford Valuation App Frontend Logic

let metadata = null;
let currentCurrency = 'INR'; // Default to Indian Rupees (₹)
const currencyRates = {
  INR: { symbol: '₹ ', rate: 108.5 },
  GBP: { symbol: '£ ', rate: 1.0 },
  USD: { symbol: '$ ', rate: 1.28 }
};

let lastRawPrice = 12000;
let lastLowBound = 11000;
let lastHighBound = 13000;
let lastAvgModelPrice = 12000;
let debounceTimer = null;

// DOM Elements
const modelSelect = document.getElementById('car-model');
const yearSelect = document.getElementById('car-year');
const mileageInput = document.getElementById('mileage-input');
const mileageSlider = document.getElementById('mileage-slider');
const engineInput = document.getElementById('engine-size');
const mpgInput = document.getElementById('mpg-input');
const taxInput = document.getElementById('tax-input');
const calculateBtn = document.getElementById('calculate-btn');
const liveToggle = document.getElementById('live-mode-toggle');
const autoBadge = document.getElementById('auto-fill-badge');

const resultCarTitle = document.getElementById('result-car-title');
const resultCarSubtitle = document.getElementById('result-car-subtitle');
const predictedPriceEl = document.getElementById('predicted-price');
const priceCurrencySymbol = document.getElementById('price-currency-symbol');
const priceRangeEl = document.getElementById('price-range');
const avgModelPriceEl = document.getElementById('avg-model-price');
const priceDiffPctEl = document.getElementById('price-diff-pct');
const gaugeBarEl = document.getElementById('gauge-bar');
const valuationBadge = document.getElementById('valuation-badge');
const modelR2Badge = document.getElementById('model-r2-badge');
const copyBtn = document.getElementById('copy-summary-btn');
const toastEl = document.getElementById('toast');
const toastMsg = document.getElementById('toast-msg');

let selectedTransmission = 'Manual';
let selectedFuelType = 'Petrol';

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
  if (window.lucide) {
    lucide.createIcons();
  }

  await loadMetadata();
  setupEventListeners();

  // Initial calculation
  triggerPrediction();
});

// Load Metadata from API
async function loadMetadata() {
  try {
    const res = await fetch('/api/metadata');
    metadata = await res.json();

    // Check if URL specifies a model (e.g. from Showroom /?model=Mustang)
    const urlParams = new URLSearchParams(window.location.search);
    const paramModel = urlParams.get('model');
    const initialModel = (paramModel && metadata.models.includes(paramModel)) ? paramModel : 'Fiesta';

    // Populate Models
    modelSelect.innerHTML = '';
    metadata.models.forEach(model => {
      const opt = document.createElement('option');
      opt.value = model;
      opt.textContent = `Ford ${model}`;
      if (model === initialModel) opt.selected = true;
      modelSelect.appendChild(opt);
    });

    // Populate Years for initial model
    updateYearDropdown(initialModel);

    // Apply defaults for initial model
    const initialYear = parseInt(yearSelect.value) || 2018;
    applyModelDefaults(initialModel, initialYear);
  } catch (err) {
    console.error('Error fetching metadata:', err);
  }
}

// Quick Select from Popular Pills Carousel
function quickSelectModel(model) {
  if (!metadata || !modelSelect) return;
  modelSelect.value = model;
  updateYearDropdown(model);
  const yr = parseInt(yearSelect.value) || 2018;
  applyModelDefaults(model, yr);
  triggerPrediction();

  // Update pill active visual state
  document.querySelectorAll('#quick-model-pills button').forEach(btn => {
    if (btn.textContent.includes(model)) {
      btn.className = 'px-3 py-1.5 rounded-xl text-xs font-semibold bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 transition-all flex items-center space-x-1.5 whitespace-nowrap';
    } else {
      btn.className = 'px-3 py-1.5 rounded-xl text-xs font-semibold bg-[#111a2e] border border-white/[0.08] text-slate-300 hover:text-white transition-all flex items-center space-x-1.5 whitespace-nowrap';
    }
  });
}

// Update Year Dropdown based on chosen model
function updateYearDropdown(model) {
  const modelData = metadata?.model_defaults?.[model];
  const years = modelData?.available_years || metadata?.years || [2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013];

  yearSelect.innerHTML = '';
  years.forEach(yr => {
    const opt = document.createElement('option');
    opt.value = yr;
    opt.textContent = `${yr}`;
    if (yr === 2018) opt.selected = true;
    yearSelect.appendChild(opt);
  });

  // If 2018 wasn't an option, select the first available year
  if (!years.includes(2018) && years.length > 0) {
    yearSelect.value = years[0];
  }
}

// Apply Smart Defaults when Model or Year changes
function applyModelDefaults(model, year) {
  const modelData = metadata?.model_defaults?.[model];
  if (!modelData) return;

  const yearStats = modelData.by_year?.[year] || modelData.overall;
  if (!yearStats) return;

  // Set transmission
  if (yearStats.transmission) {
    setTransmission(yearStats.transmission, false);
  }

  // Set fuel type
  if (yearStats.fuelType) {
    setFuelType(yearStats.fuelType, false);
  }

  // Set numericals
  if (yearStats.mileage) {
    setMileage(yearStats.mileage, false);
  }
  if (yearStats.engineSize) {
    engineInput.value = yearStats.engineSize;
  }
  if (yearStats.mpg) {
    mpgInput.value = yearStats.mpg;
  }
  if (yearStats.tax !== undefined) {
    taxInput.value = yearStats.tax;
  }

  // Flash "Specs Loaded" Badge
  if (autoBadge) {
    autoBadge.style.opacity = '1';
    setTimeout(() => {
      autoBadge.style.opacity = '0';
    }, 2500);
  }
}

// Event Listeners Setup
function setupEventListeners() {
  // Model Change
  modelSelect.addEventListener('change', () => {
    const model = modelSelect.value;
    updateYearDropdown(model);
    applyModelDefaults(model, parseInt(yearSelect.value));
    triggerAutoPrediction();
  });

  // Year Change
  yearSelect.addEventListener('change', () => {
    const model = modelSelect.value;
    const year = parseInt(yearSelect.value);
    applyModelDefaults(model, year);
    triggerAutoPrediction();
  });

  // Transmission Buttons
  document.querySelectorAll('.trans-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      setTransmission(btn.getAttribute('data-value'), true);
    });
  });

  // Fuel Type Buttons
  document.querySelectorAll('.fuel-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      setFuelType(btn.getAttribute('data-value'), true);
    });
  });

  // Mileage Sync
  mileageSlider.addEventListener('input', () => {
    mileageInput.value = mileageSlider.value;
    triggerAutoPrediction();
  });

  mileageInput.addEventListener('input', () => {
    mileageSlider.value = mileageInput.value;
    triggerAutoPrediction();
  });

  // Numeric inputs
  [engineInput, mpgInput, taxInput].forEach(inp => {
    inp.addEventListener('input', triggerAutoPrediction);
  });

  // Algorithm radios
  document.querySelectorAll('input[name="ml-algo"]').forEach(radio => {
    radio.addEventListener('change', triggerAutoPrediction);
  });

  // Calculate Button
  calculateBtn.addEventListener('click', () => {
    triggerPrediction();
  });

  // Reset defaults button
  document.getElementById('reset-defaults-btn').addEventListener('click', () => {
    applyModelDefaults(modelSelect.value, parseInt(yearSelect.value));
    showToast('Reset to Ford factory defaults for this model & year');
    triggerPrediction();
  });

  // Currency switcher
  document.querySelectorAll('.curr-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.curr-btn').forEach(b => b.classList.remove('active', 'bg-brand-600', 'text-white'));
      document.querySelectorAll('.curr-btn').forEach(b => b.classList.add('text-slate-400'));

      btn.classList.add('active', 'bg-brand-600', 'text-white');
      btn.classList.remove('text-slate-400');

      if (btn.id === 'curr-usd') currentCurrency = 'USD';
      else if (btn.id === 'curr-inr') currentCurrency = 'INR';
      else currentCurrency = 'GBP';

      priceCurrencySymbol.textContent = currencyRates[currentCurrency].symbol;
      renderFormattedPrices();
    });
  });

  // Copy Summary
  copyBtn.addEventListener('click', () => {
    const summary = `Vehicle: ${yearSelect.value} Ford ${modelSelect.value}\n` +
      `Estimated Market Price: ${currencyRates[currentCurrency].symbol}${formatNumber(convertCurrency(lastRawPrice))}\n` +
      `Specs: ${engineInput.value}L ${selectedFuelType} • ${selectedTransmission} • ${formatNumber(mileageInput.value)} miles\n` +
      `Economy: ${mpgInput.value} MPG | Annual Tax: £${taxInput.value}\n` +
      `Valuation Source: Ford Valuator AI (Random Forest Model, R² 94%)`;

    navigator.clipboard.writeText(summary).then(() => {
      showToast('Valuation summary copied to clipboard!');
    }).catch(() => {
      showToast('Valuation copied!');
    });
  });
}

function setTransmission(val, shouldPredict = true) {
  selectedTransmission = val;
  document.querySelectorAll('.trans-btn').forEach(b => {
    if (b.getAttribute('data-value') === val) {
      b.classList.add('active');
    } else {
      b.classList.remove('active');
    }
  });
  if (shouldPredict) triggerAutoPrediction();
}

function setFuelType(val, shouldPredict = true) {
  selectedFuelType = val;
  document.querySelectorAll('.fuel-btn').forEach(b => {
    if (b.getAttribute('data-value') === val) {
      b.classList.add('active');
    } else {
      b.classList.remove('active');
    }
  });
  if (shouldPredict) triggerAutoPrediction();
}

function setMileage(val, shouldPredict = true) {
  mileageInput.value = val;
  mileageSlider.value = val;
  if (shouldPredict) triggerAutoPrediction();
}

function triggerAutoPrediction() {
  if (liveToggle.checked) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      triggerPrediction();
    }, 200);
  }
}

// Perform Prediction via API
async function triggerPrediction() {
  const model = modelSelect.value || 'Fiesta';
  const year = parseInt(yearSelect.value) || 2018;
  const mileage = parseInt(mileageInput.value) || 20000;
  const engineSize = parseFloat(engineInput.value) || 1.0;
  const mpg = parseFloat(mpgInput.value) || 58.0;
  const tax = parseInt(taxInput.value) || 145;
  const algo = document.querySelector('input[name="ml-algo"]:checked')?.value || 'random_forest';

  // Subtitle & Header Update
  resultCarTitle.textContent = `${year} Ford ${model}`;
  resultCarSubtitle.textContent = `${engineSize}L ${selectedFuelType} • ${selectedTransmission} • ${formatNumber(mileage)} miles`;

  // Visual calculating state
  predictedPriceEl.classList.add('calculating');

  try {
    const payload = {
      model: model,
      year: year,
      transmission: selectedTransmission,
      fuelType: selectedFuelType,
      mileage: mileage,
      tax: tax,
      mpg: mpg,
      engineSize: engineSize,
      algorithm: algo
    };

    const res = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error('Prediction API failed');
    const data = await res.json();

    lastRawPrice = data.predictedPrice;
    lastLowBound = data.range.low;
    lastHighBound = data.range.high;
    lastAvgModelPrice = data.comparison.avgModelPrice;

    // Animate Price Counter
    animatePrice(predictedPriceEl, convertCurrency(lastRawPrice));
    renderFormattedPrices();

    // Valuation Badge
    valuationBadge.textContent = data.comparison.tag;
    const badgeColor = data.comparison.badgeColor;
    valuationBadge.className = `px-2.5 py-1 rounded-full text-xs font-mono font-semibold bg-${badgeColor}-500/10 border border-${badgeColor}-500/30 text-${badgeColor}-400 flex items-center space-x-1`;

    // Comparison Diff
    const diff = data.comparison.diffPercentage;
    priceDiffPctEl.textContent = (diff >= 0 ? `+${diff}%` : `${diff}%`);
    priceDiffPctEl.className = `font-mono font-bold ${diff < 0 ? 'text-emerald-400' : 'text-sky-400'}`;

    // Gauge bar width: scale between 20% and 85%
    let gaugePct = 50 + (diff * 1.2);
    gaugePct = Math.min(95, Math.max(10, gaugePct));
    gaugeBarEl.style.width = `${gaugePct}%`;

    // Algorithm text
    modelR2Badge.textContent = data.modelUsed;

  } catch (err) {
    console.error('Prediction error:', err);
  } finally {
    predictedPriceEl.classList.remove('calculating');
  }
}

// Currency Conversion & Formatting
function convertCurrency(gbpPrice) {
  const rate = currencyRates[currentCurrency].rate;
  return Math.round(gbpPrice * rate);
}

function renderFormattedPrices() {
  const symbol = currencyRates[currentCurrency].symbol;
  const convertedLow = convertCurrency(lastLowBound);
  const convertedHigh = convertCurrency(lastHighBound);
  const convertedAvg = convertCurrency(lastAvgModelPrice);

  predictedPriceEl.textContent = formatNumber(convertCurrency(lastRawPrice));
  priceRangeEl.textContent = `${symbol}${formatNumber(convertedLow)} – ${symbol}${formatNumber(convertedHigh)}`;
  avgModelPriceEl.textContent = `${symbol}${formatNumber(convertedAvg)}`;
}

function formatNumber(num) {
  if (currentCurrency === 'INR') {
    return Number(num).toLocaleString('en-IN');
  }
  return Number(num).toLocaleString('en-US');
}

// Smooth Number Counter Animation
function animatePrice(element, target) {
  const current = parseInt(element.textContent.replace(/,/g, '')) || 0;
  if (current === target) return;

  const duration = 400; // ms
  const start = performance.now();

  function step(time) {
    const progress = Math.min((time - start) / duration, 1);
    const easeOutQuad = 1 - (1 - progress) * (1 - progress);
    const val = Math.round(current + (target - current) * easeOutQuad);
    element.textContent = formatNumber(val);

    if (progress < 1) {
      requestAnimationFrame(step);
    } else {
      element.textContent = formatNumber(target);
    }
  }

  requestAnimationFrame(step);
}

// Toast notification
function showToast(msg) {
  toastMsg.textContent = msg;
  toastEl.classList.remove('translate-y-24', 'opacity-0');
  setTimeout(() => {
    toastEl.classList.add('translate-y-24', 'opacity-0');
  }, 2800);
}

