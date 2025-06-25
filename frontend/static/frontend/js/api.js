class ApiClient {
    constructor() {
        this.baseUrl = '/api';
        this.currentUserId = null;
        this.isAuthenticated = false;
        this.accessToken = null;
        this.refreshToken = null;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const defaults = {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCookie('csrftoken'),
            },
        };

        // Add Authorization header if token exists
        if (this.accessToken) {
            defaults.headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        const config = { ...defaults, ...options };
        
        if (config.body && typeof config.body !== 'string') {
            config.body = JSON.stringify(config.body);
        }

        try {
            let response = await fetch(url, config);
            
            // If 401, try to refresh token first
            if (response.status === 401 && this.refreshToken) {
                try {
                    await this.refreshAccessToken();
                    // Retry with new token
                    config.headers['Authorization'] = `Bearer ${this.accessToken}`;
                    response = await fetch(url, config);
                } catch (refreshError) {
                    // Refresh failed - full logout
                    return this.handleUnauthorized();
                }
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async refreshAccessToken() {
        try {
            const response = await fetch(`${this.baseUrl}/auth/jwt/refresh/`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken'),
                },
                body: JSON.stringify({ refresh: this.refreshToken }),
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data = await response.json();
            this.accessToken = data.access;
            return true;
        } catch (error) {
            console.error('Token refresh error:', error);
            this.handleUnauthorized();
            throw error;
        }
    }

    handleUnauthorized() {
        this.isAuthenticated = false;
        this.currentUserId = null;
        this.accessToken = null;
        this.refreshToken = null;
        this.updateAuthUI(false, null);
        return { is_authenticated: false, user_id: null };
    }

    getCookie(name) {
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

    // Auth methods
    async login(email, password) {
        try {
            const response = await fetch(`${this.baseUrl}/auth/jwt/create/`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken'),
                },
                body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
                throw new Error('Ошибка авторизации');
            }

            const tokens = await response.json();
            this.accessToken = tokens.access;
            this.refreshToken = tokens.refresh;
            
            // Теперь делаем запрос с токеном
            const authData = await this.checkAuth();
            this.isAuthenticated = authData.is_authenticated;
            this.currentUserId = authData.user_id;
            this.updateAuthUI(authData.is_authenticated, authData.user_id);
            return authData;
        } catch (error) {
            this.handleUnauthorized();
            throw error;
        }
    }

    async logout() {
        try {
            await this.request('/auth/logout/', {
                method: 'POST',
                body: { refresh: this.refreshToken }
            });
            return this.handleUnauthorized();
        } catch (error) {
            this.handleUnauthorized();
            throw error;
        }
    }

    async register(email, username, password, passwordConfirm) {
        try {
            return await this.request('/auth/register/', {
                method: 'POST',
                body: { 
                    email, 
                    username,
                    password, 
                    password_confirmation: passwordConfirm 
                }
            });
        } catch (error) {
            this.handleUnauthorized();
            throw error;
        }
    }

    async checkAuth() {
        try {
            const data = await this.request('/check_auth/');  // Fixed typo here
            this.isAuthenticated = data.is_authenticated;
            this.currentUserId = data.user_id;
            this.updateAuthUI(data.is_authenticated, data.user_id);
            return data;
        } catch (error) {
            return this.handleUnauthorized();
        }
    }

    // Product methods
    async getProducts() {
        return this.request('/products/');
    }

    async getCategories() {
        return this.request('/categories/');
    }

    async addToCart(productId, quantity = 1) {
        try {
            // Получаем корзину пользователя
            const cart = await this.request('/cart/');
            
            // Проверяем структуру ответа
            if (!cart || !cart.id) {
                throw new Error('Не удалось получить корзину');
            }
            
            return this.request(`/cart/${cart.id}/items/`, {
                method: 'POST',
                body: {
                    product_id: productId,
                    quantity: quantity
                }
            });
        } catch (error) {
            console.error('Ошибка при добавлении в корзину:', error);
            throw error;
        }
    }


    async getCartItems() {
        try {
            const cart = await this.request('/cart/');
            if (cart && cart.id) {
                return this.request(`/cart/${cart.id}/items/`);
            }
            return [];
        } catch (error) {
            if (error.message.includes('401')) {
                // Don't clear auth state here - let the request() method handle it
                return [];
            }
            console.error('Ошибка при получении корзины:', error);
            return [];
        }
    }
    
    async removeCartItem(itemId) {
        try {
            const cart = await this.request('/cart/');
            if (cart && cart.id) {
                return this.request(`/cart/${cart.id}/items/${itemId}/`, {
                    method: 'DELETE'
                });
            }
        } catch (error) {
            console.error('Ошибка при удалении товара:', error);
            throw error;
        }
    }
    
    async updateCartItemQuantity(itemId, quantity) {
        try {
            const cart = await this.request('/cart/');
            if (cart && cart.id) {
                return this.request(`/cart/${cart.id}/items/${itemId}/`, {
                    method: 'PATCH',
                    body: { quantity }
                });
            }
        } catch (error) {
            console.error('Ошибка при обновлении количества:', error);
            throw error;
        }
    }

    // UI Update methods
    updateAuthUI(isAuthenticated, userId) {
        if (isAuthenticated) {
            this.showAuthenticatedUI(userId);
        } else {
            this.showAnonymousUI();
        }
    }

    showAuthenticatedUI(userId) {
        $('.cart-button').show();
        $('#auth-alert').hide();
        
        $('#auth-buttons').html(`
            <a href="#" class="btn btn-outline-light me-2 cart-button">Корзина</a>
            <div class="dropdown">
                <button class="btn btn-outline-light dropdown-toggle" type="button" id="userMenu" data-bs-toggle="dropdown">
                    ${userId || 'Пользователь'}
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                    <li><a class="dropdown-item" href="#" id="profile-link">Профиль</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item" href="#" id="logout-link">Выйти</a></li>
                </ul>
            </div>
        `);
    }

    showAnonymousUI() {
        $('.cart-button').hide();
        $('#auth-alert').show();
        
        $('#auth-buttons').html(`
            <a href="#" class="btn btn-outline-light me-2" id="login-link">Войти</a>
            <a href="#" class="btn btn-primary" id="register-link">Регистрация</a>
        `);
    }
}


    

const api = new ApiClient();
export default api;