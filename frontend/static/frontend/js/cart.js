import api from './api.js';

$(document).ready(function() {
    loadCartItems();
    
    // Обработчик кнопки "Оформить заказ"
    $('#checkout-btn').click(function() {
        alert('Заказ оформлен!');
        // Здесь можно добавить логику оформления заказа
    });
    
    // Обработчик удаления товара
    $(document).on('click', '.remove-item', function() {
        const itemId = $(this).data('id');
        removeCartItem(itemId);
    });
});

async function loadCartItems() {
    try {
        const items = await api.getCartItems();
        renderCartItems(items);
    } catch (error) {
        console.error('Ошибка загрузки корзины:', error);
        $('#cart-items-container').html('<div class="alert alert-danger">Ошибка загрузки корзины</div>');
    }
}

function renderCartItems(items) {
    if (items.length === 0) {
        $('#cart-items-container').html('<div class="alert alert-info">Корзина пуста</div>');
        $('#total-price').text('0');
        return;
    }
    
    let total = 0;
    let html = '<div class="list-group">';
    
    items.forEach(item => {
        total += item.price * item.quantity;
        html += `
        <div class="list-group-item">
            <div class="row align-items-center">
                <div class="col-md-2">
                    <img src="${item.product.image || '/static/images/no-image.jpg'}" 
                         class="img-thumbnail" 
                         alt="${item.product.title}">
                </div>
                <div class="col-md-4">
                    <h5>${item.product.title}</h5>
                </div>
                <div class="col-md-2">
                    <p>${item.price} руб./шт.</p>
                </div>
                <div class="col-md-2">
                    <input type="number" 
                           class="form-control quantity-input" 
                           value="${item.quantity}" 
                           min="1"
                           data-id="${item.id}">
                </div>
                <div class="col-md-2 text-end">
                    <button class="btn btn-danger remove-item" data-id="${item.id}">
                        Удалить
                    </button>
                </div>
            </div>
        </div>`;
    });
    
    html += '</div>';
    $('#cart-items-container').html(html);
    $('#total-price').text(total.toFixed(2));
}

async function removeCartItem(itemId) {
    try {
        await api.removeCartItem(itemId);
        loadCartItems();
    } catch (error) {
        alert('Ошибка при удалении товара: ' + error.message);
    }
}