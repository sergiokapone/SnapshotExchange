async function deletePhoto(photoId) {
    const url = getCurrentBaseURL() + '/api/photos/' + photoId;
    const accessToken = getCookie('access_token');

   
        try {
            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${accessToken}`, 
                },
            });

            if (response.ok) {
                console.log("The photo has been successfully deleted.");

                location.reload(); 
            } else {
                console.log(`Error when deleting a photo from ${url}`);
            }
        } catch (error) {
            console.error("Error when deleting a photo:", error);
            console.log("Error when deleting a photo.");
        }
}



const deleteButtons = document.querySelectorAll('.delete-photo-btn');
deleteButtons.forEach(button => {
    const photoId = button.getAttribute('data-photo-id');
    button.addEventListener('click', () => deletePhoto(photoId));
});


const addPhotoButton = document.getElementById('add-photo-btn');
addPhotoButton.addEventListener('click', () => {
    $('#add-photo-modal').modal('show');
});


const uploadButton = document.getElementById('upload-button');
uploadButton.addEventListener('click', () => {

    const url = getCurrentBaseURL() + '/api/photos/upload';
    const accessToken = getCookie('access_token');

    const formData = new FormData(document.getElementById('upload-photo-form'));

    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'Authorization': `Bearer ${accessToken}`,
        },
    })
    .then(response => {
        if (response.ok) {
            console.log('Photo uploaded successfully.');
            $('#add-photo-modal').modal('hide');
        } else {
            console.error('Error when uploading photo.');
        }
    })
    .catch(error => {
        console.error('Error when uploading photo:', error);
    });
});

document.getElementById('logout-btn').addEventListener('click', () => {
    const accessToken = getCookie('access_token');
    const url = getCurrentBaseURL() + '/api/auth/logout';
    fetch(url, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`, 
        },
        
    })
    .then(response => {
        if (response.ok) {
            eraseCookie('access_token')
            window.location.href = getCurrentBaseURL() + '/views/dashboard';
        } else {
            console.error('Error logging out.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
