// Modal window index.html

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('noteModal');
    const span = document.getElementsByClassName('close')[0];

    document.querySelectorAll('.btn-openNote').forEach((btn) => {
        btn.addEventListener('click', function () {
            const note = this.parentElement;
            document.getElementById('modalTitle').innerText = note.querySelector('h2').innerText;
            document.getElementById('modalType').innerText = note.querySelector('p:nth-of-type(1)').innerText;
            document.getElementById('modalDate').innerText = note.querySelector('p:nth-of-type(2)').innerText;
            document.getElementById('modalContent').innerText = note.querySelector('p:nth-of-type(3)').innerText;

            modal.style.display = 'block';
        });
    });

    span.onclick = function () {
        modal.style.display = 'none';
    };

    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    };
});

// Filter search

