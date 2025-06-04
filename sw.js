self.addEventListener('push', function(event) {
    const data = event.data ? event.data.json() : {};
    const options = {
        body: data.body || 'Новое уведомление!',
        icon: '/static/images/notification-icon.png',
        data: { url: data.url || '/' },
    };

    event.waitUntil(
        self.registration.showNotification(data.title || 'OBNIMI Kids', options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    const url = event.notification.data.url || '/';
    event.waitUntil(
        clients.openWindow(url)
    );
});