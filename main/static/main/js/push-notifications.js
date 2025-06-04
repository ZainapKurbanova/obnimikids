document.addEventListener('DOMContentLoaded', function() {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('Service Worker зарегистрирован:', registration);
                return registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlB64ToUint8Array(vapidPublicKey)
                });
            })
            .then(function(subscription) {
                console.log('Подписка получена:', subscription);
                fetch('/notifications/subscribe/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify(subscription)
                })
                .then(response => {
                    console.log('Ответ сервера:', response);
                    return response.json();
                })
                .then(data => console.log('Устройство зарегистрировано:', data))
                .catch(error => console.error('Ошибка регистрации:', error));
            })
            .catch(function(error) {
                console.error('Ошибка регистрации Service Worker:', error);
            });
    } else {
        console.warn('Push-уведомления не поддерживаются.');
    }
});

function urlB64ToUint8Array(base64String) {
    console.log('Converting base64String:', base64String);  // Отладка
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    console.log('Converted to Uint8Array:', outputArray);
    return outputArray;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}