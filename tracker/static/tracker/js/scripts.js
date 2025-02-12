let currentSlide = 0;
const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.slider-dot');
const prevArrow = document.querySelector('.slider-arrow.prev');
const nextArrow = document.querySelector('.slider-arrow.next');

function showSlide(index) {
    slides.forEach(slide => slide.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));
    
    currentSlide = (index + slides.length) % slides.length;
    slides[currentSlide].classList.add('active');
    dots[currentSlide].classList.add('active');
}

// Auto slide every 5 seconds
setInterval(() => showSlide(currentSlide + 1), 5000);

// Manual navigation
prevArrow.addEventListener('click', () => showSlide(currentSlide - 1));
nextArrow.addEventListener('click', () => showSlide(currentSlide + 1));
dots.forEach((dot, index) => {
    dot.addEventListener('click', () => showSlide(index));
});

// Form handling
function showForm() {
    document.getElementById('startContainer').style.display = 'none';
    document.getElementById('formContainer').style.display = 'block';
}

// Form submission
const form = document.getElementById('priceForm');
form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Show loading state
    document.getElementById('formContainer').style.display = 'none';
    document.getElementById('loadingContainer').style.display = 'block';
    
    // Get form data
    const formData = new FormData(this);
    
    // Submit form using fetch
    fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessContainer({
                email: data.email,
                target_price: data.target_price,
                product_name: data.product_name
            });
        } else {
            // Show error message
            document.getElementById('formContainer').style.display = 'block';
            document.getElementById('loadingContainer').style.display = 'none';
            alert(data.error || 'An error occurred. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('formContainer').style.display = 'block';
        document.getElementById('loadingContainer').style.display = 'none';
        alert('An error occurred. Please try again.');
    });
});

// Success handling
function showSuccessContainer(data) {
    document.getElementById('loadingContainer').style.display = 'none';
    document.getElementById('userEmail').textContent = data.email;
    document.getElementById('targetPrice').textContent = data.target_price;
    document.getElementById('successContainer').style.display = 'block';
}

function resetForm() {
    form.reset();
    document.getElementById('successContainer').style.display = 'none';
    document.getElementById('formContainer').style.display = 'block';
}

// Handle Django messages
document.addEventListener('DOMContentLoaded', function() {
    if (window.djangoData && window.djangoData.email && window.djangoData.targetPrice) {
        showSuccessContainer({
            email: window.djangoData.email,
            target_price: window.djangoData.targetPrice,
            product_name: window.djangoData.productName
        });
    }
});