// Lazy loading for images
document.addEventListener('DOMContentLoaded', function() {
    // Intersection Observer for lazy loading
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    });

    // Observe all lazy images
    const lazyImages = document.querySelectorAll('img[data-src]');
    lazyImages.forEach(img => {
        imageObserver.observe(img);
    });

    // Infinite scroll for posts
    const postContainer = document.getElementById('posts-container');
    const loadMoreButton = document.getElementById('load-more-posts');
    
    if (postContainer && loadMoreButton) {
        let page = 2;
        let loading = false;

        const loadMorePosts = async () => {
            if (loading) return;
            loading = true;
            
            try {
                const response = await fetch(`?page=${page}`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });
                
                if (response.ok) {
                    const html = await response.text();
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newPosts = doc.querySelectorAll('.post-item');
                    
                    newPosts.forEach(post => {
                        postContainer.appendChild(post);
                        // Observe new lazy images
                        const newLazyImages = post.querySelectorAll('img[data-src]');
                        newLazyImages.forEach(img => imageObserver.observe(img));
                    });
                    
                    page++;
                    
                    // Hide load more button if no more posts
                    if (newPosts.length === 0) {
                        loadMoreButton.style.display = 'none';
                    }
                }
            } catch (error) {
                console.error('Error loading more posts:', error);
            } finally {
                loading = false;
            }
        };

        loadMoreButton.addEventListener('click', loadMorePosts);

        // Auto-load when scrolling near bottom
        window.addEventListener('scroll', () => {
            if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000) {
                loadMorePosts();
            }
        });
    }
});

// Image optimization and compression
function compressImage(file, maxWidth = 800, quality = 0.8) {
    return new Promise((resolve) => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        img.onload = () => {
            // Calculate new dimensions
            let { width, height } = img;
            
            if (width > maxWidth) {
                height = (height * maxWidth) / width;
                width = maxWidth;
            }
            
            canvas.width = width;
            canvas.height = height;
            
            // Draw and compress
            ctx.drawImage(img, 0, 0, width, height);
            canvas.toBlob(resolve, 'image/jpeg', quality);
        };
        
        img.src = URL.createObjectURL(file);
    });
}

// Progressive image loading
function loadImageProgressively(img) {
    const lowQualitySrc = img.dataset.lowSrc;
    const highQualitySrc = img.dataset.src;
    
    if (lowQualitySrc) {
        img.src = lowQualitySrc;
        img.classList.add('low-quality');
        
        const highQualityImg = new Image();
        highQualityImg.onload = () => {
            img.src = highQualitySrc;
            img.classList.remove('low-quality');
            img.classList.add('high-quality');
        };
        highQualityImg.src = highQualitySrc;
    } else {
        img.src = highQualitySrc;
    }
}

// Preload critical images
function preloadCriticalImages() {
    const criticalImages = document.querySelectorAll('img[data-critical]');
    criticalImages.forEach(img => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'image';
        link.href = img.dataset.src;
        document.head.appendChild(link);
    });
}

// Initialize on page load
preloadCriticalImages();
