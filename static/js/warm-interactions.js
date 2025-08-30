// Warm Interactions for Social Media Platform

document.addEventListener('DOMContentLoaded', function() {
    // Add warm hover effects to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
            this.style.boxShadow = '0 25px 50px rgba(255, 107, 53, 0.25)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 10px 30px rgba(255, 107, 53, 0.15)';
        });
    });

    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Smooth scroll for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add floating animation to profile pictures
    const profilePics = document.querySelectorAll('.profile-picture');
    profilePics.forEach(pic => {
        pic.addEventListener('mouseenter', function() {
            this.style.animation = 'float 2s ease-in-out infinite';
        });
        
        pic.addEventListener('mouseleave', function() {
            this.style.animation = 'none';
        });
    });

    // Add warm glow effect on focus for form inputs
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.boxShadow = '0 0 20px rgba(255, 107, 53, 0.3)';
            this.style.borderColor = '#ff6b35';
        });
        
        input.addEventListener('blur', function() {
            this.style.boxShadow = 'none';
            this.style.borderColor = '#e8e2db';
        });
    });

    // Add success animation for like button
    window.likePost = function(postId) {
        const button = document.querySelector(`button[onclick="likePost(${postId})"]`);
        const icon = button.querySelector('i');
        
        // Add bounce animation
        icon.style.animation = 'bounce 0.6s ease';
        
        fetch(`/posts/${postId}/like/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => response.json())
        .then(data => {
            const likeCount = document.getElementById(`likes-count-${postId}`);
            
            if (data.liked) {
                icon.className = 'fas fa-heart text-red-500 text-lg';
                // Add heart particles effect
                createHeartParticles(button);
            } else {
                icon.className = 'far fa-heart text-lg';
            }
            
            likeCount.textContent = data.likes_count;
            
            // Remove animation after completion
            setTimeout(() => {
                icon.style.animation = 'none';
            }, 600);
        })
        .catch(error => console.error('Error:', error));
    };

    // Create heart particles effect
    function createHeartParticles(button) {
        for (let i = 0; i < 6; i++) {
            const particle = document.createElement('div');
            particle.innerHTML = '❤️';
            particle.style.position = 'absolute';
            particle.style.fontSize = '12px';
            particle.style.pointerEvents = 'none';
            particle.style.zIndex = '1000';
            
            const rect = button.getBoundingClientRect();
            particle.style.left = (rect.left + Math.random() * rect.width) + 'px';
            particle.style.top = rect.top + 'px';
            
            document.body.appendChild(particle);
            
            // Animate particle
            particle.animate([
                { transform: 'translateY(0) scale(1)', opacity: 1 },
                { transform: 'translateY(-50px) scale(0.5)', opacity: 0 }
            ], {
                duration: 1000,
                easing: 'ease-out'
            }).onfinish = () => particle.remove();
        }
    }

    // Add typing indicator for comment forms
    const commentForms = document.querySelectorAll('form[action*="comment"]');
    commentForms.forEach(form => {
        const textarea = form.querySelector('textarea, input[type="text"]');
        if (textarea) {
            let typingTimer;
            
            textarea.addEventListener('input', function() {
                clearTimeout(typingTimer);
                this.style.borderColor = '#ff6b35';
                this.style.backgroundColor = '#fff5ee';
                
                typingTimer = setTimeout(() => {
                    this.style.borderColor = '#e8e2db';
                    this.style.backgroundColor = 'rgba(255, 247, 240, 0.7)';
                }, 1000);
            });
        }
    });

    // Add progressive image loading
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('fade-in');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // Add warm welcome animation for new users
    const welcomeElements = document.querySelectorAll('.warm-welcome');
    welcomeElements.forEach(element => {
        element.style.animation = 'warmWelcome 1s ease-out';
    });

    // Add notification badge animation
    const notificationBadges = document.querySelectorAll('.notification-badge');
    notificationBadges.forEach(badge => {
        badge.style.animation = 'pulse 2s infinite';
    });
});

// CSS animations (to be added to the warm-theme.css)
const style = document.createElement('style');
style.textContent = `
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes bounce {
        0%, 20%, 60%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        80% { transform: translateY(-5px); }
    }
    
    @keyframes warmWelcome {
        0% { opacity: 0; transform: translateY(30px) scale(0.9); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    @keyframes fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .fade-in {
        animation: fade-in 0.5s ease-in;
    }
`;

document.head.appendChild(style);
