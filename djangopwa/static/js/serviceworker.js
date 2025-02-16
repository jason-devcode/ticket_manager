var staticCacheName = "django-pwa-v" + new Date().getTime();
var filesToCache = ["/offline", "/css/django-pwa-app.css"];

// Cache on install
self.addEventListener("install", (event) => {
  this.skipWaiting();
  event.waitUntil(
    caches
      .open(staticCacheName)
      .then((cache) => {
        return cache
          .addAll(filesToCache)
          .then(() => {
            console.log("All files cached successfully");
          })
          .catch((error) => {
            console.error("Failed to cache files:", error);
          });
      })
      .catch((error) => {
        console.error("Failed to open cache:", error);
      })
  );
});

// Clear cache on activate
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => cacheName.startsWith("django-pwa-"))
          .filter((cacheName) => cacheName !== staticCacheName)
          .map((cacheName) => caches.delete(cacheName))
      );
    })
  );
});

// Serve from Cache
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches
      .match(event.request)
      .then((response) => {
        return response || fetch(event.request);
      })
      .catch(() => {
        return caches.match("/offline");
      })
  );
});
