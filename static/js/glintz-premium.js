// Glintz Premium Interactions & Features

class GlintzApp {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.initializeComponents();
    }

    init() {
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        // Add loading states
        this.addLoadingStates();
        
        // Initialize intersection observer for animations
        this.setupIntersectionObserver();
        
        // Setup touch gestures for mobile
        this.setupTouchGestures();
    }

    setupEventListeners() {
        // Enhanced like functionality
        document.addEventListener('click', (e) => {
            if (e.target.closest('[onclick*="likePost"]')) {
                e.preventDefault();
                const button = e.target.closest('button');
                const postId = button.getAttribute('onclick').match(/\d+/)[0];
                this.likePost(postId, button);
            }
        });

        // Image modal functionality
        window.openImageModal = (imageSrc) => {
            this.openImageModal(imageSrc);
        };

        // Infinite scroll
        this.setupInfiniteScroll();
        
        // Keyboard shortcuts
        this.setupKeyboardShortcuts();
    }

    initializeComponents() {
        // Initialize tooltips
        this.initTooltips();
        
        // Setup form enhancements
        this.enhanceForms();
        
        // Initialize progressive image loading
        this.setupProgressiveImageLoading();
    }

    async likePost(postId, button) {
        // Add immediate visual feedback
        const icon = button.querySelector('[data-lucide="heart"]');
        const countElement = document.getElementById(`likes-count-${postId}`);
        
        // Optimistic UI update
        const isLiked = icon.classList.contains('fill-current');
        
        // Add animation
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = 'scale(1)';
        }, 150);

        // Create heart particles
        if (!isLiked) {
            this.createHeartParticles(button);
        }

        try {
            const response = await fetch(`/posts/${postId}/like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                },
            });

            const data = await response.json();
            
            // Update UI based on response
            if (data.liked) {
                icon.classList.add('fill-current', 'text-red-500');
                icon.classList.remove('text-gray-500');
            } else {
                icon.classList.remove('fill-current', 'text-red-500');
                icon.classList.add('text-gray-500');
            }
            
            countElement.textContent = data.likes_count;
            
        } catch (error) {
            console.error('Error liking post:', error);
            // Revert optimistic update on error
            this.showNotification('Failed to like post', 'error');
        }
    }

    createHeartParticles(button) {
        const rect = button.getBoundingClientRect();
        const particles = 8;
        
        for (let i = 0; i < particles; i++) {
            const particle = document.createElement('div');
            particle.innerHTML = '❤️';
            particle.style.cssText = `
                position: fixed;
                left: ${rect.left + rect.width / 2}px;
                top: ${rect.top + rect.height / 2}px;
                font-size: 12px;
                pointer-events: none;
                z-index: 1000;
                user-select: none;
            `;
            
            document.body.appendChild(particle);
            
            // Animate particle
            const angle = (i / particles) * Math.PI * 2;
            const velocity = 50 + Math.random() * 50;
            const lifetime = 1000 + Math.random() * 500;
            
            particle.animate([
                {
                    transform: 'translate(0, 0) scale(1)',
                    opacity: 1
                },
                {
                    transform: `translate(${Math.cos(angle) * velocity}px, ${Math.sin(angle) * velocity - 50}px) scale(0.5)`,
                    opacity: 0
                }
            ], {
                duration: lifetime,
                easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
            }).onfinish = () => particle.remove();
        }
    }

    openImageModal(imageSrc) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4';
        modal.innerHTML = `
            <div class="relative max-w-4xl max-h-full">
                <img src="${imageSrc}" alt="Full size image" class="max-w-full max-h-full object-contain rounded-lg">
                <button onclick="this.closest('.fixed').remove()" 
                        class="absolute top-4 right-4 w-10 h-10 bg-white/20 rounded-full flex items-center justify-center text-white hover:bg-white/30 transition-colors">
                    <i data-lucide="x" class="w-6 h-6"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(modal);
        lucide.createIcons();
        
        // Close on click outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        // Close on escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    }

    setupInfiniteScroll() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadMoreContent();
                }
            });
        }, { threshold: 0.1 });

        const sentinel = document.querySelector('.pagination-sentinel');
        if (sentinel) {
            observer.observe(sentinel);
        }
    }

    setupIntersectionObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.card').forEach(card => {
            observer.observe(card);
        });
    }

    setupTouchGestures() {
        let startX, startY, currentX, currentY;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        document.addEventListener('touchmove', (e) => {
            if (!startX || !startY) return;
            
            currentX = e.touches[0].clientX;
            currentY = e.touches[0].clientY;
            
            const diffX = startX - currentX;
            const diffY = startY - currentY;
            
            // Implement swipe gestures for navigation
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    // Swipe left - next
                    this.handleSwipeLeft();
                } else {
                    // Swipe right - previous
                    this.handleSwipeRight();
                }
            }
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            
            switch(e.key) {
                case 'n':
                    // New post
                    window.location.href = '/posts/create/';
                    break;
                case 'h':
                    // Home
                    window.location.href = '/posts/';
                    break;
                case 'e':
                    // Explore
                    window.location.href = '/posts/explore/';
                    break;
                case '/':
                    // Focus search
                    e.preventDefault();
                    document.querySelector('input[name="q"]')?.focus();
                    break;
            }
        });
    }

    enhanceForms() {
        // Auto-resize textareas
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.addEventListener('input', () => {
                textarea.style.height = 'auto';
                textarea.style.height = textarea.scrollHeight + 'px';
            });
        });

        // Add character counters
        document.querySelectorAll('textarea[name="content"]').forEach(textarea => {
            const maxLength = 280;
            const counter = document.createElement('div');
            counter.className = 'text-sm text-gray-500 text-right mt-2';
            textarea.parentNode.appendChild(counter);
            
            const updateCounter = () => {
                const remaining = maxLength - textarea.value.length;
                counter.textContent = `${remaining} characters remaining`;
                counter.className = remaining < 20 ? 'text-sm text-red-500 text-right mt-2' : 'text-sm text-gray-500 text-right mt-2';
            };
            
            textarea.addEventListener('input', updateCounter);
            updateCounter();
        });
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'error' ? 'bg-red-500 text-white' : 
            type === 'success' ? 'bg-green-500 text-white' : 
            'bg-blue-500 text-white'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    }

    addLoadingStates() {
        // Add loading states to buttons
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitButton = form.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 mr-2 animate-spin"></i>Loading...';
                }
            });
        });
    }
}

// Initialize Glintz App
document.addEventListener('DOMContentLoaded', () => {
    new GlintzApp();
});

// Service Worker Registration for PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => console.log('SW registered'))
            .catch(error => console.log('SW registration failed'));
    });
}
