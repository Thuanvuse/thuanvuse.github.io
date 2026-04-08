/**
 * generate_fid.js - Tạo F-Id MỚI mỗi lần chạy bằng FingerprintJS Pro
 * Full randomize browser fingerprint: canvas, audio, fonts, WebGL, platform,
 * timezone, hardware, device memory, plugins, touch, battery, media devices...
 */
const puppeteer = require('puppeteer');
const crypto = require('crypto');

const API_KEY = 'FWckR5IO3ixuWIEZSxrx';

// ========== POOLS DỮ LIỆU RANDOM ==========

const USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
];

const RESOLUTIONS = [
    [1920, 1080], [1366, 768], [1440, 900], [1536, 864],
    [1280, 720], [1600, 900], [2560, 1440], [1680, 1050],
    [1280, 800], [1280, 1024], [1920, 1200], [1360, 768],
    [1024, 768], [1600, 1024], [2560, 1080], [3440, 1440],
    [3840, 2160], [1920, 1280],
];

const LANGUAGES = [
    'vi-VN,vi', 'en-US,en', 'vi-VN,vi,en-US,en', 'en-GB,en',
    'vi,en-US,en', 'en-US,en,vi', 'zh-CN,zh,en-US,en',
    'ja-JP,ja,en-US,en', 'ko-KR,ko,en-US,en', 'vi-VN,vi,en',
];

const PLATFORMS = [
    'Win32', 'Win64', 'MacIntel', 'Linux x86_64', 'Linux x86',
];

const TIMEZONES = [
    'Asia/Ho_Chi_Minh', 'Asia/Bangkok', 'Asia/Singapore', 'Asia/Tokyo',
    'Asia/Seoul', 'Asia/Shanghai', 'America/New_York', 'America/Los_Angeles',
    'Europe/London', 'Europe/Paris', 'Australia/Sydney', 'Asia/Kolkata',
    'America/Chicago', 'America/Denver', 'Pacific/Auckland',
];

const TIMEZONE_OFFSETS = {
    'Asia/Ho_Chi_Minh': -420, 'Asia/Bangkok': -420, 'Asia/Singapore': -480,
    'Asia/Tokyo': -540, 'Asia/Seoul': -540, 'Asia/Shanghai': -480,
    'America/New_York': 300, 'America/Los_Angeles': 480,
    'Europe/London': 0, 'Europe/Paris': -60, 'Australia/Sydney': -660,
    'Asia/Kolkata': -330, 'America/Chicago': 360, 'America/Denver': 420,
    'Pacific/Auckland': -780,
};

const GPU_VENDORS = [
    'Google Inc. (NVIDIA)',
    'Google Inc. (AMD)',
    'Google Inc. (Intel)',
    'Google Inc.',
];

const GPU_RENDERERS = [
    'ANGLE (NVIDIA, NVIDIA GeForce GTX 1050 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (NVIDIA, NVIDIA GeForce GTX 1070 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (NVIDIA, NVIDIA GeForce GTX 1080 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (NVIDIA, NVIDIA GeForce RTX 2060 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (NVIDIA, NVIDIA GeForce RTX 2070 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (NVIDIA, NVIDIA GeForce RTX 4060 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (NVIDIA, NVIDIA GeForce RTX 4070 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (AMD, AMD Radeon RX 5700 XT Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (AMD, AMD Radeon RX 6700 XT Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (AMD, AMD Radeon RX 6800 XT Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (Intel, Intel(R) UHD Graphics 770 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (Intel, Intel(R) HD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)',
    'ANGLE (Apple, Apple M1 Pro, OpenGL 4.1)',
    'ANGLE (Apple, Apple M2, OpenGL 4.1)',
];

const FONT_POOLS = [
    ['Arial', 'Verdana', 'Tahoma', 'Trebuchet MS', 'Georgia', 'Times New Roman', 'Courier New', 'Impact', 'Comic Sans MS'],
    ['Segoe UI', 'Calibri', 'Consolas', 'Cambria', 'Candara', 'Corbel', 'Constantia'],
    ['Lucida Console', 'Lucida Sans Unicode', 'Palatino Linotype', 'Book Antiqua', 'Franklin Gothic Medium'],
    ['Microsoft Sans Serif', 'MS Gothic', 'MS PGothic', 'MS UI Gothic', 'Meiryo'],
    ['Malgun Gothic', 'SimSun', 'NSimSun', 'SimHei', 'Microsoft YaHei'],
    ['Helvetica Neue', 'Helvetica', 'San Francisco', 'Menlo', 'Monaco'],
];

// ========== HELPER FUNCTIONS ==========

function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function randInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function randFloat(min, max, decimals = 6) { return parseFloat((Math.random() * (max - min) + min).toFixed(decimals)); }

// Tạo random seed cho canvas/audio noise - khác nhau mỗi lần chạy
function generateNoiseSeed() {
    return crypto.randomBytes(16).toString('hex');
}

// Chọn random subset fonts từ pool
function generateFontList() {
    const allFonts = FONT_POOLS.flat();
    const count = randInt(15, allFonts.length);
    const shuffled = allFonts.sort(() => Math.random() - 0.5);
    return shuffled.slice(0, count);
}

(async () => {
    const fs = require('fs');
    const path = require('path');
    const fidLogPath = path.join(__dirname, 'used_fids.txt');

    const loadFids = () => {
        try {
            if (fs.existsSync(fidLogPath)) {
                const data = fs.readFileSync(fidLogPath, 'utf8');
                return new Set(data.split('\n').map(s => s.trim()).filter(s => s));
            }
        } catch (e) { }
        return new Set();
    };

    let usedFids = loadFids();

    let attempt = 0;
    const maxAttempts = 10;
    let finalResult = null;

    while (attempt < maxAttempts) {
        attempt++;
        // ===== Tạo profile fingerprint hoàn toàn mới mỗi lần =====
        const ua = pick(USER_AGENTS);
        const [w, h] = pick(RESOLUTIONS);
        const lang = pick(LANGUAGES);
        const platform = pick(PLATFORMS);
        const timezone = pick(TIMEZONES);
        const tzOffset = TIMEZONE_OFFSETS[timezone] || -420;
        const gpuVendor = pick(GPU_VENDORS);
        const gpuRenderer = pick(GPU_RENDERERS);
        const hardwareConcurrency = pick([2, 4, 6, 8, 10, 12, 16]);
        const deviceMemory = pick([2, 4, 8, 16, 32]);
        const maxTouchPoints = pick([0, 0, 0, 1, 5, 10]); // Đa số desktop = 0
        const colorDepth = pick([24, 30, 32]);
        const pixelRatio = pick([1, 1, 1.25, 1.5, 2, 2]);
        const canvasNoiseSeed = generateNoiseSeed();
        const audioNoiseSeed = generateNoiseSeed();
        const fontList = generateFontList();
        const doNotTrack = pick([null, '1', 'unspecified']);
        const cookieEnabled = true;
        const pdfViewerEnabled = pick([true, true, false]);
        const webdriver = false;
        // Random screen offsets (khác nhau nếu có taskbar vị trí khác nhau)
        const screenAvailTop = pick([0, 0, 0, 30, 40]);
        const screenAvailLeft = pick([0, 0, 0, 65]);
        const availH = h - pick([30, 40, 48, 56, 60, 72]);
        // Random session storage / indexedDB support
        const sessionStorageEnabled = true;
        const indexedDBEnabled = true;
        const openDatabaseEnabled = pick([true, false]);

        const browser = await puppeteer.launch({
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                `--window-size=${w},${h}`,
                `--lang=${lang.split(',')[0]}`,
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                `--timezone=${timezone}`,
                '--disable-web-security',
            ]
        });

        try {
            const page = await browser.newPage();
            await page.setUserAgent(ua);
            await page.setViewport({ width: w, height: h, deviceScaleFactor: pixelRatio });

            // Chặn tải hình ảnh, css, font để giảm thời gian load trang (tăng tốc độ tạo FID)
            await page.setRequestInterception(true);
            page.on('request', (req) => {
                const rt = req.resourceType();
                if (['image', 'stylesheet', 'font', 'media'].includes(rt)) {
                    req.abort();
                } else {
                    req.continue();
                }
            });

            // Xóa dấu hiệu automation
            await page.evaluateOnNewDocument(() => {
                delete navigator.__proto__.webdriver;
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                // Xóa cdc_ marks
                const props = Object.getOwnPropertyNames(window);
                for (const prop of props) {
                    if (prop.match(/^cdc_/) || prop.match(/^_selenium/) || prop.match(/^_Selenium/) || prop.match(/callPhantom/) || prop.match(/__nightmare/)) {
                        delete window[prop];
                    }
                }
                // Chrome runtime spoof
                window.chrome = { runtime: {}, loadTimes: function () { }, csi: function () { } };
                // Permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) =>
                    parameters.name === 'notifications'
                        ? Promise.resolve({ state: Notification.permission })
                        : originalQuery(parameters);
            });

            // ===== FULL FINGERPRINT OVERRIDE =====
            await page.evaluateOnNewDocument((cfg) => {
                // --- Navigator ---
                Object.defineProperty(navigator, 'language', { get: () => cfg.lang.split(',')[0] });
                Object.defineProperty(navigator, 'languages', { get: () => Object.freeze(cfg.lang.split(',')) });
                Object.defineProperty(navigator, 'platform', { get: () => cfg.platform });
                Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => cfg.hardwareConcurrency });
                Object.defineProperty(navigator, 'deviceMemory', { get: () => cfg.deviceMemory });
                Object.defineProperty(navigator, 'maxTouchPoints', { get: () => cfg.maxTouchPoints });
                Object.defineProperty(navigator, 'cookieEnabled', { get: () => cfg.cookieEnabled });
                Object.defineProperty(navigator, 'pdfViewerEnabled', { get: () => cfg.pdfViewerEnabled });
                Object.defineProperty(navigator, 'doNotTrack', { get: () => cfg.doNotTrack });
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                // Vendor - match UA
                if (cfg.ua.includes('Firefox')) {
                    Object.defineProperty(navigator, 'vendor', { get: () => '' });
                    Object.defineProperty(navigator, 'product', { get: () => 'Gecko' });
                } else {
                    Object.defineProperty(navigator, 'vendor', { get: () => 'Google Inc.' });
                    Object.defineProperty(navigator, 'product', { get: () => 'Gecko' });
                }
                // Connection (NetworkInformation)
                if (navigator.connection) {
                    const connTypes = ['wifi', '4g', 'ethernet'];
                    const effectiveTypes = ['4g', '3g'];
                    Object.defineProperty(navigator.connection, 'effectiveType', { get: () => effectiveTypes[Math.floor(Math.random() * effectiveTypes.length)] });
                    Object.defineProperty(navigator.connection, 'type', { get: () => connTypes[Math.floor(Math.random() * connTypes.length)] });
                    Object.defineProperty(navigator.connection, 'downlink', { get: () => (Math.random() * 10 + 1).toFixed(1) });
                    Object.defineProperty(navigator.connection, 'rtt', { get: () => Math.floor(Math.random() * 200 + 50) });
                }

                // --- Screen ---
                Object.defineProperty(screen, 'width', { get: () => cfg.w });
                Object.defineProperty(screen, 'height', { get: () => cfg.h });
                Object.defineProperty(screen, 'availWidth', { get: () => cfg.w - cfg.screenAvailLeft });
                Object.defineProperty(screen, 'availHeight', { get: () => cfg.availH });
                Object.defineProperty(screen, 'availTop', { get: () => cfg.screenAvailTop });
                Object.defineProperty(screen, 'availLeft', { get: () => cfg.screenAvailLeft });
                Object.defineProperty(screen, 'colorDepth', { get: () => cfg.colorDepth });
                Object.defineProperty(screen, 'pixelDepth', { get: () => cfg.colorDepth });
                Object.defineProperty(window, 'devicePixelRatio', { get: () => cfg.pixelRatio });
                Object.defineProperty(window, 'innerWidth', { get: () => cfg.w });
                Object.defineProperty(window, 'innerHeight', { get: () => cfg.h - 80 }); // toolbar
                Object.defineProperty(window, 'outerWidth', { get: () => cfg.w });
                Object.defineProperty(window, 'outerHeight', { get: () => cfg.h });
                Object.defineProperty(document.documentElement, 'clientWidth', { get: () => cfg.w });
                Object.defineProperty(document.documentElement, 'clientHeight', { get: () => cfg.h - 80 });

                // --- Timezone ---
                const origDTF = Intl.DateTimeFormat;
                Intl.DateTimeFormat = function (...args) {
                    if (!args[1]) args[1] = {};
                    if (!args[1].timeZone) args[1].timeZone = cfg.timezone;
                    return new origDTF(...args);
                };
                Intl.DateTimeFormat.prototype = origDTF.prototype;
                Intl.DateTimeFormat.supportedLocalesOf = origDTF.supportedLocalesOf;
                const origResolvedOptions = origDTF.prototype.resolvedOptions;
                origDTF.prototype.resolvedOptions = function () {
                    const result = origResolvedOptions.call(this);
                    result.timeZone = cfg.timezone;
                    return result;
                };
                // Date timezone offset
                Date.prototype.getTimezoneOffset = function () { return cfg.tzOffset; };

                // --- Canvas Fingerprint Noise ---
                // Thêm noise ngẫu nhiên vào canvas output
                const seed = cfg.canvasNoiseSeed;
                // Simple seeded PRNG từ hex seed
                let _s = 0;
                for (let i = 0; i < seed.length; i++) _s = ((_s << 5) - _s + seed.charCodeAt(i)) | 0;
                function seededRandom() {
                    _s = (_s * 16807 + 0) % 2147483647;
                    return (_s & 0xFFFF) / 0xFFFF;
                }

                const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function (type, quality) {
                    const ctx = this.getContext('2d');
                    if (ctx && this.width > 0 && this.height > 0) {
                        try {
                            const imageData = ctx.getImageData(0, 0, this.width, this.height);
                            const pixels = imageData.data;
                            // Thêm noise nhẹ vào pixels
                            for (let i = 0; i < pixels.length; i += 4) {
                                pixels[i] = Math.max(0, Math.min(255, pixels[i] + Math.floor((seededRandom() - 0.5) * 4)));
                                pixels[i + 1] = Math.max(0, Math.min(255, pixels[i + 1] + Math.floor((seededRandom() - 0.5) * 4)));
                                pixels[i + 2] = Math.max(0, Math.min(255, pixels[i + 2] + Math.floor((seededRandom() - 0.5) * 4)));
                            }
                            ctx.putImageData(imageData, 0, 0);
                        } catch (e) { }
                    }
                    return origToDataURL.call(this, type, quality);
                };

                const origToBlob = HTMLCanvasElement.prototype.toBlob;
                HTMLCanvasElement.prototype.toBlob = function (callback, type, quality) {
                    const ctx = this.getContext('2d');
                    if (ctx && this.width > 0 && this.height > 0) {
                        try {
                            const imageData = ctx.getImageData(0, 0, this.width, this.height);
                            const pixels = imageData.data;
                            for (let i = 0; i < pixels.length; i += 4) {
                                pixels[i] = Math.max(0, Math.min(255, pixels[i] + Math.floor((seededRandom() - 0.5) * 4)));
                                pixels[i + 1] = Math.max(0, Math.min(255, pixels[i + 1] + Math.floor((seededRandom() - 0.5) * 4)));
                                pixels[i + 2] = Math.max(0, Math.min(255, pixels[i + 2] + Math.floor((seededRandom() - 0.5) * 4)));
                            }
                            ctx.putImageData(imageData, 0, 0);
                        } catch (e) { }
                    }
                    return origToBlob.call(this, callback, type, quality);
                };

                // --- Audio Fingerprint Noise ---
                const audioSeed = cfg.audioNoiseSeed;
                let _as = 0;
                for (let i = 0; i < audioSeed.length; i++) _as = ((_as << 5) - _as + audioSeed.charCodeAt(i)) | 0;
                function audioSeededRandom() {
                    _as = (_as * 16807 + 0) % 2147483647;
                    return (_as & 0xFFFF) / 0xFFFF;
                }

                const origCreateOscillator = AudioContext.prototype.createOscillator;
                const origCreateDynamicsCompressor = AudioContext.prototype.createDynamicsCompressor;
                const origGetChannelData = AudioBuffer.prototype.getChannelData;
                AudioBuffer.prototype.getChannelData = function (channel) {
                    const data = origGetChannelData.call(this, channel);
                    // Add tiny noise to audio buffer
                    for (let i = 0; i < data.length; i += 100) {
                        data[i] += (audioSeededRandom() - 0.5) * 0.0001;
                    }
                    return data;
                };

                const origCopyFromChannel = AudioBuffer.prototype.copyFromChannel;
                AudioBuffer.prototype.copyFromChannel = function (destination, channelNumber, startInChannel) {
                    origCopyFromChannel.call(this, destination, channelNumber, startInChannel);
                    for (let i = 0; i < destination.length; i += 100) {
                        destination[i] += (audioSeededRandom() - 0.5) * 0.0001;
                    }
                };

                // --- WebGL ---
                const origGetContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function (type, attrs) {
                    const ctx = origGetContext.call(this, type, attrs);
                    if (ctx && (type === 'webgl' || type === 'webgl2' || type === 'experimental-webgl')) {
                        const origGetParam = ctx.getParameter.bind(ctx);
                        const origGetExtension = ctx.getExtension.bind(ctx);
                        const origGetShaderPrecisionFormat = ctx.getShaderPrecisionFormat ? ctx.getShaderPrecisionFormat.bind(ctx) : null;

                        ctx.getParameter = function (param) {
                            // UNMASKED_VENDOR_WEBGL
                            if (param === 37445) return cfg.gpuVendor;
                            // UNMASKED_RENDERER_WEBGL
                            if (param === 37446) return cfg.gpuRenderer;
                            // MAX_TEXTURE_SIZE - vary slightly
                            if (param === 3379) return [8192, 16384, 16384, 32768][Math.floor(seededRandom() * 4)];
                            // MAX_VIEWPORT_DIMS
                            if (param === 3386) return new Int32Array([cfg.w > 2560 ? 32768 : 16384, cfg.h > 1440 ? 32768 : 16384]);
                            // MAX_RENDERBUFFER_SIZE
                            if (param === 34024) return [8192, 16384, 16384][Math.floor(seededRandom() * 3)];
                            // ALIASED_LINE_WIDTH_RANGE
                            if (param === 33902) return new Float32Array([1, 1]);
                            // ALIASED_POINT_SIZE_RANGE
                            if (param === 33901) return new Float32Array([1, [1024, 2048, 8192][Math.floor(seededRandom() * 3)]]);
                            // MAX_VERTEX_ATTRIBS
                            if (param === 34921) return [16, 16, 32][Math.floor(seededRandom() * 3)];
                            // MAX_VERTEX_UNIFORM_VECTORS
                            if (param === 36347) return [256, 1024, 4096][Math.floor(seededRandom() * 3)];
                            // MAX_FRAGMENT_UNIFORM_VECTORS
                            if (param === 36349) return [256, 1024, 4096][Math.floor(seededRandom() * 3)];
                            // MAX_VARYING_VECTORS
                            if (param === 36348) return [15, 16, 30, 32][Math.floor(seededRandom() * 4)];
                            return origGetParam(param);
                        };

                        // Fake WebGL extensions list
                        const origGetSupportedExtensions = ctx.getSupportedExtensions ? ctx.getSupportedExtensions.bind(ctx) : null;
                        if (origGetSupportedExtensions) {
                            ctx.getSupportedExtensions = function () {
                                const exts = origGetSupportedExtensions();
                                // Randomly remove 1-3 extensions to vary
                                if (exts && exts.length > 5) {
                                    const removeCount = Math.floor(seededRandom() * 3) + 1;
                                    for (let i = 0; i < removeCount; i++) {
                                        const idx = Math.floor(seededRandom() * exts.length);
                                        exts.splice(idx, 1);
                                    }
                                }
                                return exts;
                            };
                        }
                    }
                    return ctx;
                };

                // --- Fonts Detection Spoof ---
                // Override measureText to slightly alter width for font detection
                const origMeasureText = CanvasRenderingContext2D.prototype.measureText;
                CanvasRenderingContext2D.prototype.measureText = function (text) {
                    const result = origMeasureText.call(this, text);
                    const origWidth = result.width;
                    // Tiny noise to font metrics
                    Object.defineProperty(result, 'width', {
                        get: () => origWidth + (seededRandom() - 0.5) * 0.00001
                    });
                    return result;
                };

                // --- Plugins ---
                // Spoof plugins list
                Object.defineProperty(navigator, 'plugins', {
                    get: () => {
                        const pluginData = [];
                        if (cfg.pdfViewerEnabled) {
                            pluginData.push({
                                name: 'PDF Viewer', filename: 'internal-pdf-viewer',
                                description: 'Portable Document Format', length: 1,
                                0: { type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format' },
                                item: (i) => pluginData[0][i],
                                namedItem: () => pluginData[0][0],
                            });
                            pluginData.push({
                                name: 'Chrome PDF Viewer', filename: 'internal-pdf-viewer',
                                description: 'Portable Document Format', length: 1,
                                0: { type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format' },
                                item: (i) => pluginData[1][i],
                                namedItem: () => pluginData[1][0],
                            });
                            pluginData.push({
                                name: 'Chromium PDF Viewer', filename: 'internal-pdf-viewer',
                                description: 'Portable Document Format', length: 1,
                                0: { type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format' },
                                item: (i) => pluginData[2][i],
                                namedItem: () => pluginData[2][0],
                            });
                        }
                        pluginData.length = pluginData.length;
                        return pluginData;
                    }
                });

                // --- Media Devices ---
                if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
                    const origEnumerate = navigator.mediaDevices.enumerateDevices.bind(navigator.mediaDevices);
                    navigator.mediaDevices.enumerateDevices = async function () {
                        // Generate random device IDs
                        const devices = [];
                        const audioInputCount = Math.floor(seededRandom() * 2) + 1;
                        const videoInputCount = Math.floor(seededRandom() * 2) + 1;
                        for (let i = 0; i < audioInputCount; i++) {
                            devices.push({
                                deviceId: cfg.canvasNoiseSeed.substr(i * 8, 16) + cfg.audioNoiseSeed.substr(i * 4, 16),
                                kind: 'audioinput',
                                label: '',
                                groupId: cfg.canvasNoiseSeed.substr(0, 32),
                            });
                        }
                        devices.push({
                            deviceId: 'default',
                            kind: 'audiooutput',
                            label: '',
                            groupId: cfg.canvasNoiseSeed.substr(0, 32),
                        });
                        for (let i = 0; i < videoInputCount; i++) {
                            devices.push({
                                deviceId: cfg.audioNoiseSeed.substr(i * 8, 16) + cfg.canvasNoiseSeed.substr(i * 4, 16),
                                kind: 'videoinput',
                                label: '',
                                groupId: cfg.audioNoiseSeed.substr(0, 32),
                            });
                        }
                        return devices;
                    };
                }

                // --- Battery API ---
                if (navigator.getBattery) {
                    navigator.getBattery = () => Promise.resolve({
                        charging: seededRandom() > 0.5,
                        chargingTime: Math.floor(seededRandom() * 7200),
                        dischargingTime: Infinity,
                        level: parseFloat((seededRandom() * 0.6 + 0.4).toFixed(2)),
                        addEventListener: () => { },
                    });
                }

                // --- Storage estimates ---
                if (navigator.storage && navigator.storage.estimate) {
                    navigator.storage.estimate = () => Promise.resolve({
                        quota: [1073741824, 2147483648, 4294967296, 8589934592][Math.floor(seededRandom() * 4)],
                        usage: Math.floor(seededRandom() * 1048576),
                    });
                }

                // --- Performance.now noise ---
                const origPerfNow = Performance.prototype.now;
                Performance.prototype.now = function () {
                    return origPerfNow.call(this) + (seededRandom() - 0.5) * 0.1;
                };

                // --- SpeechSynthesis voices ---
                if (window.speechSynthesis) {
                    const origGetVoices = window.speechSynthesis.getVoices;
                    window.speechSynthesis.getVoices = function () {
                        const voices = origGetVoices.call(this);
                        // Randomly shuffle and trim to vary
                        if (voices.length > 3) {
                            const shuffled = [...voices].sort(() => seededRandom() - 0.5);
                            return shuffled.slice(0, Math.max(5, Math.floor(voices.length * (0.6 + seededRandom() * 0.4))));
                        }
                        return voices;
                    };
                }

                // --- ClientRects noise ---
                const origGetBoundingClientRect = Element.prototype.getBoundingClientRect;
                Element.prototype.getBoundingClientRect = function () {
                    const rect = origGetBoundingClientRect.call(this);
                    const noise = (seededRandom() - 0.5) * 0.00001;
                    return new DOMRect(
                        rect.x + noise, rect.y + noise,
                        rect.width + noise, rect.height + noise
                    );
                };

                const origGetClientRects = Element.prototype.getClientRects;
                Element.prototype.getClientRects = function () {
                    const rects = origGetClientRects.call(this);
                    const newRects = [];
                    for (let i = 0; i < rects.length; i++) {
                        const r = rects[i];
                        const noise = (seededRandom() - 0.5) * 0.00001;
                        newRects.push(new DOMRect(r.x + noise, r.y + noise, r.width + noise, r.height + noise));
                    }
                    return newRects;
                };

            }, {
                lang, platform, timezone, tzOffset, w, h, ua,
                hardwareConcurrency, deviceMemory, maxTouchPoints,
                colorDepth, pixelRatio, gpuVendor, gpuRenderer,
                canvasNoiseSeed, audioNoiseSeed, fontList,
                doNotTrack, cookieEnabled, pdfViewerEnabled,
                screenAvailTop, screenAvailLeft, availH,
                openDatabaseEnabled,
            });

            await page.goto('https://m.oklavip16.live/register', {
                waitUntil: 'domcontentloaded',
                timeout: 15000
            });

            const result = await page.evaluate(async (apiKey) => {
                return new Promise(async (resolve) => {
                    setTimeout(() => resolve({ error: 'timeout' }), 12000);
                    try {
                        const script = document.createElement('script');
                        script.src = `https://fpnpmcdn.net/v3/${apiKey}/loader_v3.9.0.js`;
                        document.head.appendChild(script);
                        await new Promise((res, rej) => {
                            script.onload = res;
                            script.onerror = rej;
                            setTimeout(rej, 8000);
                        });
                        const fp = window.__fpjs_p_l_b;
                        if (fp && fp.load) {
                            const agent = await fp.load({ apiKey, region: 'ap' });
                            const r = await agent.get();
                            resolve({ fid: r.visitorId, rid: r.requestId });
                        } else {
                            resolve({ error: 'FingerprintJS not loaded' });
                        }
                    } catch (e) {
                        resolve({ error: e.message || String(e) });
                    }
                });
            }, API_KEY);

            if (result && result.fid) {
                // Đọc lại file lần chót để đề phòng có luồng khác vừa ghi thêm FID này vào txt
                usedFids = loadFids();

                if (!usedFids.has(result.fid)) {
                    // Ghi vào file với cơ chế chống lỗi ghi đồng thời (retry append)
                    for (let i = 0; i < 10; i++) {
                        try {
                            fs.appendFileSync(fidLogPath, result.fid + '\n', 'utf8');
                            break;
                        } catch (err) {
                            // Nếu file đang bị lock/chiếm dụng trên Windows, đợi 50-100ms
                            await new Promise(r => setTimeout(r, 50 + Math.random() * 50));
                        }
                    }

                    finalResult = result;
                    await browser.close();
                    break; // Thoát vòng lặp while
                } else {
                    // Bị trùng lặp: ghi đè lỗi vào finalResult rồi loop mới chạy lại
                    finalResult = { error: 'duplicate_fid', fid: result.fid };
                }
            } else {
                // Lỗi load script fpjs (ví dụ network timeout, Cloudflare block)
                // Ngừng loop ngay lập tức để trả lỗi về Python, tránh vượt quá 30s
                finalResult = result;
                break;
            }

        } catch (e) {
            finalResult = { error: e.message };
            break;
        } finally {
            if (browser && typeof browser.close === 'function') {
                await browser.close().catch(() => { });
            }
        }
    } // End while loop

    console.log(JSON.stringify(finalResult || { error: 'Unknown failed after max attempts' }));
})();
