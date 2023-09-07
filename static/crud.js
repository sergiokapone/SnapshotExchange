const baseURL = 'https://shapshotexchange.onrender.com/'
const api = 'api/photos/'

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }

async function deletePhoto(photoId) {
    const url = baseURL + api + photoId;
    
        try {
            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Authorization': getCookie('access_token'), 
                },
            });

            if (response.ok) {
                console.log("The photo has been successfully deleted.");

                location.reload(); 
            } else {
                alert("Error when deleting a photo.");
            }
        } catch (error) {
            console.error("Error when deleting a photo:", error);
            alert("Error when deleting a photo.");
        }
}


const deleteButtons = document.querySelectorAll('.delete-photo-btn');
deleteButtons.forEach(button => {
    const photoId = button.getAttribute('data-photo-id');
    button.addEventListener('click', () => deletePhoto(photoId));
});