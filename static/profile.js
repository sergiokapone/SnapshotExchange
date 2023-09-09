document.querySelectorAll('.toggle-status-button').forEach(button => {
    button.addEventListener('click', function() {
        const accessToken = getCookie('access_token');
        const userEmail = this.getAttribute('data-email');
        const userStatus = this.getAttribute('data-status');

        let url, successMessage;



        if (userStatus === 'True') {
            // Если пользователь активен, то выполняем бан
            url = getCurrentBaseURL() + `/api/users/ban?email=${userEmail}`;
            successMessage = 'User has been banned successfully.';
        } else {
            // Если пользователь неактивен, то выполняем активацию
            url = getCurrentBaseURL() + `/api/users/activate?email=${userEmail}`;
            successMessage = 'User has been activated successfully.';
        }

        fetch(url, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${accessToken}`, 
            },
        })
        .then(response => {
            if (response.ok) {
                Notiflix.Notify.success(successMessage);
                location.reload();
            } else {
                Notiflix.Notify.failure('Error during the operation.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Notiflix.Notify.failure('Network error during the operation.');
        });
    });
});
