const modal = document.querySelector('[data-modal]');
const openButtons = document.querySelectorAll('[data-open-modal]');
const closeButton = document.querySelector('[data-close-modal]');

function setModal(open) {
  modal.classList.toggle('is-open', open);
  modal.setAttribute('aria-hidden', String(!open));
  document.body.style.overflow = open ? 'hidden' : '';
  if (open) document.querySelector('#name').focus();
}

openButtons.forEach((button) => button.addEventListener('click', () => setModal(true)));
closeButton.addEventListener('click', () => setModal(false));
modal.addEventListener('click', (event) => {
  if (event.target === modal) setModal(false);
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') setModal(false);
});

if (document.body.dataset.openRegister === 'true') setModal(true);
