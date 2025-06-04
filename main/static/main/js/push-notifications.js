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
    console.log('Input base64String:', base64String);
    if (!base64String) {
        console.error('base64String is empty or undefined');
        return new Uint8Array(0);
    }
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
    try {
        const rawData = atob(base64);
        const output = new Uint8Array(rawData.length);
        for (let i = 0; i < rawData.length; i++) {
            output[i] = rawData.charCodeAt(i);
        }
        console.log('Converted Uint8Array:', output);
        return output;
    } catch (e) {
        console.error('Error converting base64 to Uint8Array:', e);
        return new Uint8Array(0);
    }
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
