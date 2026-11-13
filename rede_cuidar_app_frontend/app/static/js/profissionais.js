const searchInput = document.querySelector('[data-professionals-search]');

if (searchInput) {
  const cards = Array.from(document.querySelectorAll('[data-professional-card]'));
  const categoryButtons = Array.from(document.querySelectorAll('[data-professional-category]'));
  const count = document.querySelector('[data-professionals-count]');
  const emptyMessage = document.querySelector('[data-professionals-empty]');
  let activeCategory = 'all';

  const normalize = (value) => String(value)
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase();

  const updateResults = () => {
    const query = normalize(searchInput.value.trim());
    let visibleCount = 0;

    cards.forEach((card) => {
      const matchesCategory = activeCategory === 'all'
        || normalize(card.dataset.category) === normalize(activeCategory);
      const matchesSearch = normalize(card.textContent).includes(query);
      const isVisible = matchesCategory && matchesSearch;

      card.hidden = !isVisible;
      if (isVisible) visibleCount += 1;
    });

    count.textContent = `${visibleCount} ${visibleCount === 1 ? 'profissional' : 'profissionais'}`;
    emptyMessage.hidden = visibleCount > 0;
  };

  searchInput.addEventListener('input', updateResults);

  categoryButtons.forEach((button) => {
    button.addEventListener('click', () => {
      activeCategory = button.dataset.professionalCategory;
      categoryButtons.forEach((categoryButton) => {
        const isActive = categoryButton === button;
        categoryButton.classList.toggle('is-active', isActive);
        categoryButton.setAttribute('aria-pressed', String(isActive));
      });
      updateResults();
    });
  });
}
