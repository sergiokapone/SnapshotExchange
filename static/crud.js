function getCurrentBaseURL() {
    const protocol = window.location.protocol; 
    const host = window.location.host; 
    return `${protocol}//${host}`;
}

const api = '/api/photos/'

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
            window.location.href = getCurrentBaseURL() + '/views/auth/login';
        } else {
            console.error('Error logging out.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});


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

// Обработчик события для кнопки "Add Photo"
const addPhotoButton = document.getElementById('add-photo-btn');
addPhotoButton.addEventListener('click', () => {
    // Открываем модальное окно для добавления фото
    $('#add-photo-modal').modal('show');
});

// Обработчик события для кнопки "Upload"
const uploadButton = document.getElementById('upload-button');
uploadButton.addEventListener('click', () => {

    const url = getCurrentBaseURL() + api + 'upload';
    const accessToken = localStorage.getItem('access_token');
    // Получите данные из формы
    const formData = new FormData(document.getElementById('upload-photo-form'));

    // Отправьте данные на сервер для загрузки фото
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
            // Закройте модальное окно после успешной загрузки
            $('#add-photo-modal').modal('hide');
            // Обновите страницу или выполните другие необходимые действия
        } else {
            console.error('Error when uploading photo.');
        }
    })
    .catch(error => {
        console.error('Error when uploading photo:', error);
    });
});
