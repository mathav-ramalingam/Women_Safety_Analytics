$(document).ready(function () {
    // Initialize hidden elements
    $('.loader').hide(); // Keep loader functionality for real-time detection

    // Start live detection
    $('#btn-live-detect').click(function () {
        // Start live detection in the backend (Flask)
        window.location.href = '/live_detect';
    });

    // Toggle chatbot visibility
    $('#toggle-chatbot').on('click', function() {
        const chatbotContainer = $('#chatbot-container');
        const isVisible = chatbotContainer.is(':visible');

        if (isVisible) {
            chatbotContainer.slideUp(300);
            $(this).css('bottom', '20px');
            $(this).text('Chat');
        } else {
            chatbotContainer.slideDown(300);
            $(this).css('bottom', '540px');
            $(this).text('Close Chat');
        }
    });

    // Handle click event for the statistics button
    $('#btn-stats').on('click', function() {
        const imageUrl = 'C:/Users/sreep/OneDrive/Desktop/Deployment/Screenshot 2024-08-22 080644.png';
        const statsImageContainer = $('#stats-image-container');
        const statsImage = $('#stats-image');

        // Set the source of the image
        statsImage.attr('src', imageUrl);

        // Show the image container with a smooth effect
        statsImageContainer.slideDown(300);
    });

    // Ensure the chatbot iframe loads properly
    const chatbotIframe = document.querySelector('#chatbot-container iframe');
    chatbotIframe.addEventListener('load', function() {
        console.log('Chatbot loaded successfully');
    });

    chatbotIframe.addEventListener('error', function() {
        console.log('Error loading the chatbot');
        alert('Failed to load the chatbot. Please try again later.');
    });
});
