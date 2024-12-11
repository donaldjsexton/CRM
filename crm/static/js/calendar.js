
document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        plugins: ['dayGrid', 'timeGrid', 'interaction'],
        initialView: 'dayGridMonth',
        events: '/api/events/',  // Use the new URL
        eventClick: function(info) {
            alert('Event: ' + info.event.title);
        },
        selectable: true,
        dateClick: function(info) {
            alert('Selected date: ' + info.dateStr);
        },
    });

    calendar.render();
});