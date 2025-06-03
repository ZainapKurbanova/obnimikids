// static/js/common.js
function showAlert(message, type) {
    let alertDiv = document.createElement('div');
    alertDiv.className = `custom-alert ${type}`;
    alertDiv.textContent = message;
    document.body.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.classList.add('show');
    }, 100);

    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => {
            alertDiv.remove();
        }, 500);
    }, 5000);
}

document.addEventListener('DOMContentLoaded', function() {
    let alertMessages = document.getElementById('alert-messages');
    if (alertMessages) {
        let messages = alertMessages.getElementsByClassName('alert-message');
        let currentPage = window.location.pathname;

        for (let i = 0; i < messages.length; i++) {
            let message = messages[i];
            let messageText = message.textContent;
            let messageType = message.classList.contains('success') ? 'success' : 'error';
            let messageDataType = message.getAttribute('data-type');

            if (currentPage.includes('/cart/')) {
                if (messageDataType === 'cart_action') {
                    showAlert(messageText, messageType);
                }
            } else if (currentPage.includes('/catalog/') || currentPage.includes('/product/')) {
                if (messageDataType === 'cart_action') {
                    showAlert(messageText, messageType);
                }
            } else if (currentPage.includes('/checkout/')) {
                if (messageDataType === 'order_success') {
                    showAlert(messageText, messageType);
                }
            }
        }
    }
});