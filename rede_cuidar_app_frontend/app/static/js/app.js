const modals = Array.from(document.querySelectorAll('[data-modal]'));
const openButtons = document.querySelectorAll('[data-open-modal]');

function setModal(modal, open) {
  if (!modal) return;
  if (open) {
    modals.forEach((otherModal) => {
      if (otherModal !== modal) setModal(otherModal, false);
    });
  }
  modal.classList.toggle('is-open', open);
  modal.setAttribute('aria-hidden', String(!open));
  document.body.style.overflow = open ? 'hidden' : '';
  if (open) {
    const firstField = modal.querySelector('input:not([disabled]), textarea, select');
    if (firstField) firstField.focus();
  }
}

openButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const modal = button.dataset.openModal
      ? document.getElementById(button.dataset.openModal)
      : document.querySelector('[data-modal]');
    setModal(modal, true);
  });
});

modals.forEach((modal) => {
  modal.querySelectorAll('[data-close-modal]').forEach((button) => {
    button.addEventListener('click', () => setModal(modal, false));
  });
  modal.addEventListener('click', (event) => {
    if (event.target === modal) setModal(modal, false);
  });
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    const openModal = modals.find((modal) => modal.classList.contains('is-open'));
    setModal(openModal, false);
  }
});

if (document.body.dataset.openRegister === 'true') setModal(modals[0], true);
if (document.body.dataset.openProfessionalModal === 'true') {
  setModal(document.getElementById('professional-edit-modal'), true);
}
