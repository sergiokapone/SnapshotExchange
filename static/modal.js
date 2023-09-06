// Get elements
const modalPhotos = document.querySelectorAll(".modal-photo");
const modalPhoto = document.getElementById("modalPhoto");
const modalTitle = document.getElementById("photoModalLabel");

// Image click handler
modalPhotos.forEach(function(photo) {
    photo.addEventListener("click", function () {
        // Get the description from the data-description attribute
        const description = this.getAttribute("data-description");

        // Set the description in the modal title
        modalTitle.textContent = description;

        // Get the URL of the selected photo
        const selectedPhotoUrl = this.getAttribute("src");

        // Set the URL of the photo in the modal window
        modalPhoto.src = selectedPhotoUrl;
        
        // Opening a modal window
        $("#photoModal").modal("show");
    });
});