if (access_token) {
    localStorage.setItem('access_token', access_token);
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function deleteCookie(name) {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

function getCurrentBaseURL() {
    const protocol = window.location.protocol; 
    const host = window.location.host; 
    return `${protocol}//${host}`;
}


// document.getElementById('signup-form').addEventListener('submit', handleSignup);

// async function handleSignup(e) {
//     e.preventDefault(); 

//     const formData = new FormData(e.target);
//     const url = getCurrentBaseURL() + '/api/auth/signup'; 

//     try {
//         const response = await fetch(url, {
//             method: 'POST',
//             body: formData,
//         });

//         if (response.ok) {
            
//             window.location.href = getCurrentBaseURL() + '/views/dashboard';
//         } else {
//             console.error('Error during signup.');
//         }
//     } catch (error) {
//         console.error('Error:', error);
//     }
// }


document.getElementById('logout-btn').addEventListener('click', () => {
    const accessToken = localStorage.getItem('access_token');
    const url = getCurrentBaseURL() + '/api/auth/logout';
    fetch(url, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`, 
        },
        
    })
    .then(response => {
        if (response.ok) {
            localStorage.removeItem('access_token');
            // deleteCookie('access_token');
            window.location.href = getCurrentBaseURL() + '/views/dashboard';
        } else {
            console.error('Error logging out.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});


async function deletePhoto(photoId) {
    const url = getCurrentBaseURL() + '/api/photos/' + photoId;
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


const addPhotoButton = document.getElementById('add-photo-btn');
addPhotoButton.addEventListener('click', () => {
    $('#add-photo-modal').modal('show');
});


const uploadButton = document.getElementById('upload-button');
uploadButton.addEventListener('click', () => {

    const url = getCurrentBaseURL() + '/api/photos/upload';
    const accessToken = localStorage.getItem('access_token');

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
