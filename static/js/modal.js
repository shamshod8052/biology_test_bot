document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.open-modal').forEach(function(button) {
        button.addEventListener('click', function() {
            var targetId = button.getAttribute('data-target');
            document.getElementById(targetId).style.display = 'flex';
        });
    });

    document.querySelectorAll('.custom-close-btn').forEach(function(closeBtn) {
        closeBtn.addEventListener('click', function() {
            var targetId = closeBtn.getAttribute('data-target');
            document.getElementById(targetId).style.display = 'none';
        });
    });

    document.querySelectorAll('.custom-modal-overlay').forEach(function(overlay) {
        overlay.addEventListener('click', function(event) {
            if (event.target.classList.contains('custom-modal-overlay')) {
                event.target.style.display = 'none';
            }
        });
    });
});
