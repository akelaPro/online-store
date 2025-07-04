$(document).ready(function() {
    // Общие функции для работы с JWT и куками
    function setCookie(name, value, days) {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "") + expires + "; path=/; Secure; SameSite=Lax";
    }

    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    function deleteCookie(name) {
        document.cookie = name + '=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    }

    // Новая функция для получения CSRF токена из куки
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }

    async function checkAuth() {
        const accessToken = getCookie('access_token');
        if (!accessToken) return false;
        
        try {
            const response = await $.ajax({
                url: '/api/check_auth/',
                type: 'GET'
            });
            return response.isAuthenticated;
        } catch {
            return false;
        }
    }

    // Настройка AJAX запросов
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            // Добавляем CSRF токен
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
            }
            
            // Добавляем JWT токен из куки в заголовок
            const accessToken = getCookie('access_token');
            if (accessToken && !settings.noAuth) {
                xhr.setRequestHeader("Authorization", `Bearer ${accessToken}`);
            }
        },
        error: function(xhr, textStatus, errorThrown) {
            if (xhr.status === 401 && !xhr.config._retry) {
                const refreshToken = getCookie('refresh_token');
                
                if (refreshToken) {
                    xhr.config._retry = true;
                    
                    return $.ajax({
                        url: '/api/auth/jwt/refresh/',
                        type: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({ refresh: refreshToken }),
                        success: function(response) {
                            setCookie('access_token', response.access, 1);
                            xhr.config.headers['Authorization'] = 'Bearer ' + response.access;
                            return $.ajax(xhr.config);
                        },
                        error: function() {
                            deleteCookie('access_token');
                            deleteCookie('refresh_token');
                            window.location.href = '/login/';
                        }
                    });
                } else {
                    deleteCookie('access_token');
                    window.location.href = '/login/';
                }
            }
            return Promise.reject(xhr);
        }
    });

    // Загрузка данных при старте
    function loadInitialData() {
        loadCategories();
        loadProducts();
        updateCartCount();
    }

    // Загрузка категорий
    function loadCategories() {
        $.get('/api/categories/', function(data) {
            renderCategories(data.results || data);
        }).fail(function() {
            console.error('Ошибка загрузки категорий');
        });
    }

    // Загрузка товаров
    function loadProducts(categoryId = null) {
        let url = '/api/products/';
        if (categoryId) {
            url += `?categories=${categoryId}`;
        }

        $.get(url, function(data) {
            renderProducts(data.results || data);
        }).fail(function() {
            console.error('Ошибка загрузки товаров');
        });
    }

    // Отрисовка категорий
    function renderCategories(categories) {
        const $container = $('.categories-list');
        $container.empty();
        
        // Добавляем "Все категории"
        $container.append(`
            <a href="#" class="list-group-item list-group-item-action active" data-id="all">
                Все категории
            </a>
        `);
        
        categories.forEach(category => {
            $container.append(`
                <a href="#" class="list-group-item list-group-item-action" data-id="${category.id}">
                    ${category.name}
                </a>
            `);
        });

        // Обработчик выбора категории
        $container.find('a').on('click', function(e) {
            e.preventDefault();
            $container.find('a').removeClass('active');
            $(this).addClass('active');
            
            const categoryId = $(this).data('id');
            if (categoryId === 'all') {
                loadProducts();
            } else {
                loadProducts(categoryId);
            }
        });
    }

    // Отрисовка товаров
    function renderProducts(products) {
        const $container = $('.products-container');
        $container.empty();
        
        if (products.length === 0) {
            $container.html('<div class="col-12"><p>Товары не найдены</p></div>');
            return;
        }
        
        products.forEach(product => {
            const imageUrl = product.image || '/static/images/no-image.png';
            $container.append(`
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <img src="${imageUrl}" class="card-img-top product-image" alt="${product.title}">
                        <div class="card-body">
                            <h5 class="card-title">${product.title}</h5>
                            <p class="card-text">${product.price} руб.</p>
                            <a href="/product/${product.id}" class="btn btn-primary">Подробнее</a>
                            <button class="btn btn-success add-to-cart" data-product-id="${product.id}">
                                В корзину
                            </button>
                        </div>
                    </div>
                </div>
            `);
        });

        // Инициализация обработчиков для кнопок "В корзину"
        initAddToCartButtons();
    }

    // Инициализация кнопок "В корзину"
    function initAddToCartButtons() {
        $('.add-to-cart').off('click').on('click', function() {
            if (!checkAuth()) {
                window.location.href = '/login/';
                return;
            }

            const productId = $(this).data('product-id');
            addToCart(productId);
        });
    }

    // Добавление в корзину
    function addToCart(productId) {
        $.ajax({
            url: '/api/cart/items/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                product_id: productId,
                quantity: 1
            }),
            success: function() {
                updateCartCount();
                showAlert('Товар добавлен в корзину!', 'success');
            },
            error: function(xhr) {
                showAlert('Ошибка при добавлении в корзину', 'danger');
            }
        });
    }

    // Обновление счетчика корзины
    function updateCartCount() {
        $.get('/api/cart/', function(data) {
            const count = data.items ? data.items.length : 0;
            $('#cart-count').text(count);
        }).fail(function() {
            $('#cart-count').text('0');
        });
    }

    // Показать уведомление
    function showAlert(message, type = 'info') {
        const $alert = $(`
            <div class="alert alert-${type} alert-dismissible fade show fixed-top" role="alert" style="top: 20px; right: 20px; width: 300px; z-index: 1000;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `);
        
        $('body').append($alert);
        setTimeout(() => $alert.alert('close'), 3000);
    }

    // Инициализация при загрузке
    loadInitialData();

    // Обработчики форм
    $('#login-form').on('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            email: $('#email').val(),
            password: $('#password').val()
        };

        $.ajax({
            url: '/api/auth/jwt/create/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                setCookie('access_token', response.access, 1);
                setCookie('refresh_token', response.refresh, 7);
                window.location.href = '/';
            },
            error: function() {
                showAlert('Ошибка входа. Проверьте email и пароль.', 'danger');
            }
        });
    });

    $('#logout-btn').on('click', function(e) {
        e.preventDefault();
        
        // Сначала очищаем куки на клиенте
        deleteCookie('access_token');
        deleteCookie('refresh_token');
        
        // Затем делаем запрос на сервер
        $.ajax({
            url: '/api/auth/logout/',
            type: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            success: function() {
                // Принудительно обновляем страницу
                window.location.href = '/login/';
            },
            error: function(xhr) {
                console.error('Logout error:', xhr);
                // Все равно перенаправляем на страницу входа
                window.location.href = '/login/';
            }
        });
    })});