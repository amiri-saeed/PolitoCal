document.getElementById('modal-open').onclick = function() {
    document.getElementById('info-modal').style.display = 'flex';
}

document.querySelector('.close-button').onclick = function() {
    document.getElementById('info-modal').style.display = 'none';
}

window.onclick = function(event) {
    if (event.target == document.getElementById('info-modal')) {
        document.getElementById('info-modal').style.display = 'none';
    }
}
