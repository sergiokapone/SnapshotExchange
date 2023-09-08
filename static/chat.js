function getCurrentBaseURL() {
    const protocol = window.location.protocol; 
    const host = window.location.host; 
    return `${protocol}//${host}`;
}

// const basURL = "wss://snapshotexchange.onrender.com"
const ws = new WebSocket(`${getCurrentBaseURL()}/views/ws`);
ws.onmessage = function(event) {


    const messages = document.getElementById('messages')
    const message = document.createElement('li')
    const content = document.createTextNode(event.data)
    message.appendChild(content)
    messages.appendChild(message)
};
function sendMessage(event) {
    var input = document.getElementById("messageText")
    ws.send(input.value)
    input.value = ''
    event.preventDefault()
}