document.getElementById("login-form").addEventListener('submit', handleLogin);

async function handleLogin(e) {
    e.preventDefault(); 

    const url = getCurrentBaseURL() + '/api/auth/login'
    
    const formData = {
        username: document.getElementById('username').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(formData) 
        });

        if (response.ok) {

            const responseJSON =  await response.json();
            const access_token = responseJSON.access_token;

            // localStorage.setItem('access_token', access_token);
            setCookie('access_token', access_token, 1)
            
            window.location.href = getCurrentBaseURL() + '/views/database';
            Notiflix.Notify.success('Login successful.');

        } else {
            Notiflix.Notify.failure('Error during login.');
        }
    } catch (error) {
        Notiflix.Notify.failure('Error:', error);
    }
}




