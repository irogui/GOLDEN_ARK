document.addEventListener("DOMContentLoaded", function() {
    const input = document.getElementById("image_item");
    const preview = document.getElementById("preview_image_item");

    input.addEventListener("change", function() {
        const file = input.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
});