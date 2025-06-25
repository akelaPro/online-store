import api from './api.js';

$(document).ready(function() {
    const authModal = new bootstrap.Modal(document.getElementById('authModal'));
    let isLoginForm = true;
    let selectedCategories = [];
    let minPrice = null;
    let maxPrice = null;
    let allProducts = [];
    let filteredProducts = [];

    // Инициализация при загрузке страницы
    initializePage();

    function initializePage() {
        setupAuthHandlers();
        setupProductHandlers();
        api.checkAuth();
        loadCategories();
        loadAllProducts();
    }

    function setupAuthHandlers() {
        // Переключение между формами
        $('#toggleAuthForm').click(function(e) {
            e.preventDefault();
            toggleAuthForms();
        });

        // Обработка входа
        $('#loginForm').submit(async function(e) {
            e.preventDefault();
            const email = $('#loginEmail').val();
            const password = $('#loginPassword').val();
            await handleLogin(email, password);
        });

        // Обработка регистрации
        $('#registerForm').submit(async function(e) {
            e.preventDefault();
            const email = $('#registerEmail').val();
            const username = $('#registerUsername').val();
            const password = $('#registerPassword').val();
            const passwordConfirm = $('#registerPasswordConfirm').val();
            
            if (password !== passwordConfirm) {
                alert('Пароли не совпадают');
                return;
            }
            
            await handleRegister(email, username, password, passwordConfirm);
        });

        // Открытие модального окна
        $('body').on('click', '#login-link, #alert-login-link', function(e) {
            e.preventDefault();
            showLoginForm();
            authModal.show();
        });

        $('body').on('click', '#register-link', function(e) {
            e.preventDefault();
            showRegisterForm();
            authModal.show();
        });

        // Выход
        $('body').on('click', '#logout-link', function(e) {
            e.preventDefault();
            handleLogout();
        });
    }

    function setupProductHandlers() {
        // Обработчики фильтров
        $('#apply-filters').click(applyFilters);
        $(document).on('click', '.add-to-cart', addToCartHandler);
    }

    // Auth functions
    function toggleAuthForms() {
        isLoginForm = !isLoginForm;
        
        if (isLoginForm) {
            showLoginForm();
        } else {
            showRegisterForm();
        }
    }

    function showLoginForm() {
        isLoginForm = true;
        $('#loginForm').show();
        $('#registerForm').hide();
        $('#authModalTitle').text('Вход');
        $('#toggleAuthForm').text('Нет аккаунта? Зарегистрироваться');
    }

    function showRegisterForm() {
        isLoginForm = false;
        $('#loginForm').hide();
        $('#registerForm').show();
        $('#authModalTitle').text('Регистрация');
        $('#toggleAuthForm').text('Уже есть аккаунт? Войти');
    }

    async function handleLogin(email, password) {
        try {
            await api.login(email, password);
            authModal.hide();
        } catch (error) {
            alert('Ошибка авторизации: ' + error.message);
        }
    }

    async function handleRegister(email, username, password, passwordConfirm) {
        try {
            await api.register(email, username, password, passwordConfirm);
            await api.login(email, password);
            authModal.hide();
        } catch (error) {
            alert('Ошибка регистрации: ' + error.message);
        }
    }

    async function handleLogout() {
        try {
            await api.logout();
            location.reload();
        } catch (error) {
            alert('Ошибка при выходе: ' + error.message);
        }
    }

    // Product functions
    function loadCategories() {
        api.getCategories()
            .then(data => {
                renderCategories(data);
                setupCategoryHandlers();
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Ошибка загрузки категорий');
            });
    }

    function renderCategories(categories) {
        const categoryList = $('#category-list');
        categoryList.empty();
        
        categoryList.append(`
            <li class="list-group-item category-item" data-id="all">
                <a href="#" class="text-decoration-none">Все категории</a>
            </li>
        `);
        
        categories.forEach(category => {
            categoryList.append(`
                <li class="list-group-item category-item" data-id="${category.id}">
                    <a href="#" class="text-decoration-none">${category.name}</a>
                </li>
            `);
        });
        
        $('.category-item[data-id="all"]').addClass('active');
    }

    function setupCategoryHandlers() {
        $('.category-item').click(function(e) {
            e.preventDefault();
            const categoryId = $(this).data('id');
            
            if (categoryId === 'all') {
                selectedCategories = [];
                $('.category-item').removeClass('active');
                $(this).addClass('active');
            } else {
                $(this).toggleClass('active');
                
                selectedCategories = $('.category-item.active')
                    .map(function() { 
                        const id = $(this).data('id');
                        return id !== 'all' ? id : null; 
                    })
                    .get()
                    .filter(id => id !== null);
                
                if (selectedCategories.length === 0 || 
                    $('.category-item[data-id="all"]').hasClass('active')) {
                    selectedCategories = [];
                    $('.category-item').removeClass('active');
                    $('.category-item[data-id="all"]').addClass('active');
                }
            }
            
            filterProducts();
        });
    }

    function loadAllProducts() {
        api.getProducts()
            .then(data => {
                allProducts = data;
                filterProducts();
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Ошибка загрузки товаров');
            });
    }

    function applyFilters() {
        minPrice = $('#price-min').val() || null;
        maxPrice = $('#price-max').val() || null;
        filterProducts();
    }

    function filterProducts() {
        filteredProducts = allProducts.filter(product => {
            if (selectedCategories.length > 0) {
                const productCategories = product.categories.map(c => c.id);
                const hasCategory = productCategories.some(catId => selectedCategories.includes(catId));
                if (!hasCategory) return false;
            }
            
            const price = parseFloat(product.price);
            if (minPrice && price < parseFloat(minPrice)) return false;
            if (maxPrice && price > parseFloat(maxPrice)) return false;
            
            return true;
        });
        
        displayProducts();
    }

    function displayProducts() {
        const productsContainer = $('#products-container');
        productsContainer.empty();
        
        if (filteredProducts.length === 0) {
            productsContainer.html('<div class="col-12"><p class="text-center">Товары не найдены</p></div>');
            return;
        }
        
        filteredProducts.forEach(product => {
            const imageUrl = product.image ? product.image : '/static/images/no-image.jpg';
            productsContainer.append(`
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <img src="${imageUrl}" class="card-img-top" alt="${product.title}">
                        <div class="card-body">
                            <h5 class="card-title">${product.title}</h5>
                            <p class="card-text">${product.description ? product.description.substring(0, 100) + '...' : ''}</p>
                            <p class="text-primary fw-bold">${product.price} руб.</p>
                            <button class="btn btn-primary add-to-cart" data-id="${product.id}">В корзину</button>
                        </div>
                    </div>
                </div>
            `);
        });
    }

    function addToCartHandler() {
        const productId = $(this).data('id');
        addToCart(productId);
    }

    async function addToCart(productId) {
        try {
            await api.addToCart(productId);
            showSuccess('Товар добавлен в корзину');
        } catch (error) {
            console.error('Ошибка:', error);
            showError(error.message);
        }
    }

    // Helper functions
    function showError(message) {
        alert(message);
    }

    function showSuccess(message) {
        alert(message);
    }
});