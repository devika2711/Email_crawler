//document.getElementById('connect-Gmail').addEventListener('click', function() {
   // window.location.href = 'http://localhost:5007'; // Redirect to Flask OAuth login
//});


async function fetchEmails() {
    const response = await fetch('http://localhost:5007/dashboard');
    const emails = await response.json();
    const emailList = document.getElementById('email-list');
    emailList.innerHTML = '';  

    emails.forEach(email => {
        const emailDiv = document.createElement('div');
        emailDiv.className = 'email-item';
        emailDiv.innerHTML = `
            <h3>${email.subject}</h3>
            <p><strong>From:</strong> ${email.sender}</p>
            <p><strong>Date:</strong> ${email.date}</p>
            <p><strong>Snippet:</strong> ${email.snippet}</p>
            <p><strong>Message:</strong> ${email.message_body}</p>
            <p><strong>Response:</strong> ${email.response}</p>
            <button onclick="approveEmail('${email.id}')">Approve</button>
            <button onclick="editEmail('${email.id}')">Edit</button>
            <button onclick="sendEmail('${email.id}', '${email.sender}', '${email.response}')">Send</button>
        `;
        emailList.appendChild(emailDiv);
    });
    
}


fetchEmails();

async function approveEmail(emailId) {
    await fetch(`http://localhost:5000/approve/${emailId}`, { method: 'POST' });
    fetchEmails();  // Refresh the email list
}

async function editEmail(emailId) {
    const newResponse = prompt('Edit response:');
    if (newResponse) {
        await fetch(`http://localhost:5000/edit/${emailId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ response: newResponse })
        });

        fetchEmails(); 
}

async function sendEmail(emailId, toEmail, response) {
    await fetch(`http://localhost:5000/send/${emailId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ response: response, to: toEmail })
    });

    fetchEmails();  
}
}
