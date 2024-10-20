document.addEventListener("DOMContentLoaded", function() {
    // Existing modal functionality
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

    // Function to format the date as 'YYYY-MM-DD'
    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    // Set default date for the date picker
    (function setDefaultDate() {
        const dateInput = document.getElementById('start_date');
        if (dateInput) {
            const today = new Date();
            dateInput.value = formatDate(today); // Set default to today initially
        }
    })();

    // Event listener to set the date to the start of the current week
    document.getElementById('set-today').addEventListener('click', function() {
        const today = new Date();
        const currentMonday = new Date(today);
        const daysSinceMonday = (today.getDay() + 6) % 7; // Find how many days ago Monday was (0-6)
        currentMonday.setDate(today.getDate() - daysSinceMonday);
        document.getElementById('start_date').value = formatDate(currentMonday);
    });

    // Event listener to set the date to the start of the next week
    document.getElementById('set-next-week').addEventListener('click', function() {
        const today = new Date();
        const nextMonday = new Date(today);
        const daysUntilNextMonday = (8 - today.getDay()) % 7; // Find days until the next Monday
        nextMonday.setDate(today.getDate() + daysUntilNextMonday);
        document.getElementById('start_date').value = formatDate(nextMonday);
    });
});




// document.getElementById('modal-open').onclick = function() {
//     document.getElementById('info-modal').style.display = 'flex';
// }

// document.querySelector('.close-button').onclick = function() {
//     document.getElementById('info-modal').style.display = 'none';
// }

// window.onclick = function(event) {
//     if (event.target == document.getElementById('info-modal')) {
//         document.getElementById('info-modal').style.display = 'none';
//     }
// }
