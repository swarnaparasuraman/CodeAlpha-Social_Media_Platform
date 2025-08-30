// Glintz Service Worker - PWA Support

const CACHE_NAME = 'glintz-v1.0.0';
const STATIC_CACHE = 'glintz-static-v1';
const DYNAMIC_CACHE = 'glintz-dynamic-v1';

// Assets to cache immediately
const STATIC_ASSETS = [
    '/',
    '/static/css/glintz-design-system.css',
    '/static/js/glintz-premium.js',
    '/static/js/lazy-loading.js',
    'https://cdn.tailwindcss.com',
    'https://unpkg.com/lucide@latest/dist/umd/lucide.js',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:wght@400;500;600;700&display=swap'
];

// Install event - cache static assets
self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .catch(error => {
                console.error('Failed to cache static assets:', error);
            })
    );
    self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch event - serve from cache with network fallback
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Skip external requests (except fonts and CDN)
    if (url.origin !== location.origin && 
        !url.hostname.includes('googleapis.com') && 
        !url.hostname.includes('gstatic.com') &&
        !url.hostname.includes('tailwindcss.com') &&
        !url.hostname.includes('unpkg.com')) {
        return;
    }

    event.respondWith(
        caches.match(request)
            .then(cachedResponse => {
                if (cachedResponse) {
                    // Serve from cache
                    return cachedResponse;
                }

                // Network request with caching
                return fetch(request)
                    .then(response => {
                        // Don't cache non-successful responses
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // Clone the response
                        const responseToCache = response.clone();

                        // Determine cache type
                        const cacheType = isStaticAsset(request.url) ? STATIC_CACHE : DYNAMIC_CACHE;

                        // Cache the response
                        caches.open(cacheType)
                            .then(cache => {
                                cache.put(request, responseToCache);
                            });

                        return response;
                    })
                    .catch(error => {
                        console.error('Fetch failed:', error);
                        
                        // Return offline fallback for HTML pages
                        if (request.headers.get('accept').includes('text/html')) {
                            return caches.match('/offline.html');
                        }
                        
                        throw error;
                    });
            })
    );
});

// Background sync for offline actions
self.addEventListener('sync', event => {
    console.log('Background sync triggered:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

// Push notifications
self.addEventListener('push', event => {
    console.log('Push notification received:', event);
    
    const options = {
        body: event.data ? event.data.text() : 'New notification from Glintz',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View',
                icon: '/static/icons/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/icons/xmark.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('Glintz', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
    console.log('Notification clicked:', event);
    
    event.notification.close();

    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/posts/explore/')
        );
    } else if (event.action === 'close') {
        // Just close the notification
    } else {
        // Default action - open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Helper functions
function isStaticAsset(url) {
    return url.includes('/static/') || 
           url.includes('googleapis.com') || 
           url.includes('gstatic.com') ||
           url.includes('tailwindcss.com') ||
           url.includes('unpkg.com');
}

async function doBackgroundSync() {
    try {
        // Get pending actions from IndexedDB
        const pendingActions = await getPendingActions();
        
        for (const action of pendingActions) {
            try {
                await fetch(action.url, {
                    method: action.method,
                    headers: action.headers,
                    body: action.body
                });
                
                // Remove successful action
                await removePendingAction(action.id);
            } catch (error) {
                console.error('Failed to sync action:', error);
            }
        }
    } catch (error) {
        console.error('Background sync failed:', error);
    }
}

// IndexedDB helpers for offline storage
async function getPendingActions() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('glintz-offline', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['actions'], 'readonly');
            const store = transaction.objectStore('actions');
            const getAllRequest = store.getAll();
            
            getAllRequest.onsuccess = () => resolve(getAllRequest.result);
            getAllRequest.onerror = () => reject(getAllRequest.error);
        };
        
        request.onupgradeneeded = () => {
            const db = request.result;
            if (!db.objectStoreNames.contains('actions')) {
                db.createObjectStore('actions', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}

async function removePendingAction(id) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('glintz-offline', 1);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['actions'], 'readwrite');
            const store = transaction.objectStore('actions');
            const deleteRequest = store.delete(id);
            
            deleteRequest.onsuccess = () => resolve();
            deleteRequest.onerror = () => reject(deleteRequest.error);
        };
    });
}

// Cache management
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            caches.open(DYNAMIC_CACHE)
                .then(cache => cache.addAll(event.data.payload))
        );
    }
});

console.log('Glintz Service Worker loaded successfully');
