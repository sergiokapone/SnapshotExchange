document.getElementById("signup-form").addEventListener('submit', handleSignup);


async function handleSignup(e) {
    e.preventDefault(); 

    const url = getCurrentBaseURL() + '/api/auth/signup'
    
    const formData = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
    };
    
    const jsonData = JSON.stringify(formData); // Преобразование в JSON

    const password = document.getElementById('password').value;
    const confirm_password = document.getElementById('confirm_password').value;

    if (password !== confirm_password) {
        console.error('Passwords do not match.');
        return;
    }

        
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: jsonData
        });

        if (response.ok) {
            window.location.href = getCurrentBaseURL() + '/views/dashboard';
            console.log('User registered successfully.');

        } else {

            console.error('Error during signup.');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
