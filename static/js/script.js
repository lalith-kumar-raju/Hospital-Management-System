// script.js - jQuery for form validation, UI effects, and interactions

$(document).ready(function() {

    // ─── Flash message auto-dismiss (5 seconds) ───
    setTimeout(function() {
        $('.flash-msg').fadeOut(500, function() {
            $(this).remove();
        });
    }, 5000);

    // ─── Password visibility toggle ───
    $('.toggle-password').on('click', function() {
        var targetId = $(this).data('target');
        var input = $('#' + targetId);
        var icon = $(this).find('i');
        if (input.attr('type') === 'password') {
            input.attr('type', 'text');
            icon.removeClass('bi-eye').addClass('bi-eye-slash');
        } else {
            input.attr('type', 'password');
            icon.removeClass('bi-eye-slash').addClass('bi-eye');
        }
    });

    // ─── Registration form validation ───
    $('#registerForm').on('submit', function(e) {
        var name = $('#full_name').val().trim();
        var email = $('#email').val().trim();
        var phone = $('#phone').val().trim();
        var password = $('#password').val();
        var confirm = $('#confirm_password').val();
        var errors = [];

        if (name.length < 2) errors.push('Name must be at least 2 characters.');
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.push('Enter a valid email address.');
        if (!/^\d{10}$/.test(phone)) errors.push('Phone must be 10 digits.');
        if (password.length < 6) errors.push('Password must be at least 6 characters.');
        if (password !== confirm) errors.push('Passwords do not match.');

        if (errors.length > 0) {
            e.preventDefault();
            alert(errors.join('\n'));
        }
    });

    // ─── Login form validation ───
    $('#loginForm').on('submit', function(e) {
        var email = $('#email').val().trim();
        var password = $('#password').val();
        if (!email || !password) {
            e.preventDefault();
            alert('Please fill in all fields.');
        }
    });

    // ─── Admin login validation ───
    $('#adminLoginForm').on('submit', function(e) {
        var username = $('#username').val().trim();
        var password = $('#password').val();
        if (!username || !password) {
            e.preventDefault();
            alert('Please fill in all fields.');
        }
    });

    // ─── Password strength indicator ───
    $('#password').on('input', function() {
        var val = $(this).val();
        var strength = '';
        var color = '';
        if (val.length < 6) {
            strength = 'Weak';
            color = 'text-danger';
        } else if (val.length < 10) {
            strength = 'Medium';
            color = 'text-warning';
        } else {
            strength = 'Strong';
            color = 'text-success';
        }
        $('#passwordStrength').html('<span class="' + color + '">Strength: ' + strength + '</span>');
    });

    // ─── Confirm cancel appointment ───
    $('.confirm-cancel').on('submit', function(e) {
        if (!confirm('Are you sure you want to cancel this appointment?')) {
            e.preventDefault();
        }
    });

    // ─── Confirm delete (doctors, services) ───
    $('.confirm-delete').on('submit', function(e) {
        if (!confirm('Are you sure you want to delete this? This action cannot be undone.')) {
            e.preventDefault();
        }
    });

    // ─── Book by disease form validation ───
    $('#bookDiseaseForm').on('submit', function(e) {
        var disease = $('#disease').val();
        var date = $('#appointment_date').val();
        var slot = $('#time_slot').val();
        if (!disease || !date || !slot) {
            e.preventDefault();
            alert('Please fill in all required fields.');
        }
    });

    // ─── Add doctor form validation ───
    $('#addDoctorForm').on('submit', function(e) {
        var name = $(this).find('[name="full_name"]').val().trim();
        var username = $(this).find('[name="username"]').val().trim();
        var password = $(this).find('[name="password"]').val();
        if (!name || !username || !password) {
            e.preventDefault();
            alert('Full name, username, and password are required.');
        }
    });
});
