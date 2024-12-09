document.addEventListener('DOMContentLoaded', function () {

    // Dropdown selection for 'Bank' or 'Government Work'
    const workDropdown = document.getElementById('work-type');
    workDropdown.addEventListener('change', function () {
        if (this.value === 'bank') {
            console.log('Bank work selected');
        } else if (this.value === 'government') {
            console.log('Government work selected');
        }
    });

    // Form submission with image preview
    const fileInput = document.getElementById('signature-file');
    const filePreview = document.getElementById('file-preview');

    fileInput.addEventListener('change', function () {
        const file = fileInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                filePreview.src = e.target.result;
                filePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        } else {
            filePreview.style.display = 'none';
        }
    });

    // Handle form validation
    const form = document.getElementById('verification-form');
    form.addEventListener('submit', function (e) {
        const signatureFile = fileInput.value;
        if (!signatureFile) {
            e.preventDefault();
            alert('Please upload a signature image.');
        }
    });
});
