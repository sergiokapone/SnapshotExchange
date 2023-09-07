function getCurrentBaseURL() {
    const protocol = window.location.protocol; 
    const host = window.location.host; 
    return `${protocol}//${host}`;
}

const api = '/api/photos/'


async function deletePhoto(photoId) {
    const url = getCurrentBaseURL() + api + photoId;

    const accessToken = localStorage.getItem('access_token');

   
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
            consile.log("Error when deleting a photo.");
        }
}


const deleteButtons = document.querySelectorAll('.delete-photo-btn');
deleteButtons.forEach(button => {
    const photoId = button.getAttribute('data-photo-id');
    button.addEventListener('click', () => deletePhoto(photoId));
});