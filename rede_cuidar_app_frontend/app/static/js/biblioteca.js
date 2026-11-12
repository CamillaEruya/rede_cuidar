const chatForm = document.querySelector('[data-chat-form]');
const chatMessages = document.querySelector('[data-chat-messages]');
const chatHistory = [];
const newsList = document.querySelector('[data-news-list]');
const newsRefreshButton = document.querySelector('[data-news-refresh]');
const newsStyles = ['library-news-teal', 'library-news-purple', 'library-news-peach'];
const newsIcons = ['♡', '✦', '☆'];

function appendMessage({ author, message, own = false, sources = [] }) {
  const article = document.createElement('article');
  article.className = `library-chat-message${own ? ' library-chat-message-own' : ''}`;

  const avatar = document.createElement('span');
  avatar.className = `feed-avatar ${own ? 'avatar-blue' : 'avatar-mint'}`;
  avatar.setAttribute('aria-hidden', 'true');
  avatar.textContent = own ? chatForm.dataset.chatAvatar : 'RC';

  const content = document.createElement('div');
  const authorElement = document.createElement('div');
  authorElement.className = 'library-chat-author';
  authorElement.textContent = author;

  const text = document.createElement('p');
  text.textContent = typeof message === 'string'
    ? message
    : 'Não foi possível processar esta resposta. Tente novamente.';
  content.append(authorElement, text);

  if (sources.length) {
    const sourceList = document.createElement('p');
    sourceList.className = 'library-chat-sources';
    const documentPages = new Map();
    for (const source of sources) {
      if (!documentPages.has(source.document)) {
        documentPages.set(source.document, new Set());
      }
      documentPages.get(source.document).add(source.page);
    }
    sourceList.textContent = `Se quiser conferir também: ${Array.from(documentPages, ([document, pages]) => {
      const pageList = Array.from(pages).sort((a, b) => a - b).join(', ');
      return `${document} (p. ${pageList})`;
    }).join('; ')}`;
    content.append(sourceList);
  }

  article.append(avatar, content);
  chatMessages.append(article);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return article;
}

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const input = chatForm.elements.message;
  const message = input.value.trim();
  if (!message) return;

  appendMessage({ author: chatForm.dataset.chatAuthor, message, own: true });
  input.value = '';
  input.disabled = true;
  chatForm.querySelector('button[type="submit"]').disabled = true;
  const pendingMessage = appendMessage({
    author: 'Assistente da Rede Cuidar',
    message: 'Consultando os documentos...',
  });

  try {
    const response = await fetch('/biblioteca/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history: chatHistory.slice(-8) }),
    });
    const result = await response.json();
    pendingMessage.remove();

    if (!response.ok) {
      const detail = result.detail;
      let errorMessage = 'Não foi possível responder agora. Tente novamente.';
      if (typeof detail === 'string') {
        errorMessage = detail;
      } else if (Array.isArray(detail)) {
        const validationMessages = detail
          .map(error => error && typeof error.msg === 'string' ? error.msg : '')
          .filter(Boolean);
        if (validationMessages.length) {
          errorMessage = validationMessages.join(' ');
        }
      }
      appendMessage({
        author: 'Assistente da Rede Cuidar',
        message: errorMessage,
      });
      return;
    }

    if (typeof result.answer !== 'string' || !Array.isArray(result.sources)) {
      appendMessage({
        author: 'Assistente da Rede Cuidar',
        message: 'A resposta recebida está em um formato inválido. Tente novamente.',
      });
      return;
    }

    appendMessage({
      author: 'Assistente da Rede Cuidar',
      message: result.answer,
      sources: result.sources,
    });
    chatHistory.push(
      { role: 'user', content: message },
      { role: 'assistant', content: result.answer },
    );
  } catch {
    pendingMessage.remove();
    appendMessage({
      author: 'Assistente da Rede Cuidar',
      message: 'Não foi possível conectar à biblioteca. Tente novamente.',
    });
  } finally {
    input.disabled = false;
    chatForm.querySelector('button[type="submit"]').disabled = false;
    input.focus();
  }
});

function showNewsStatus(message) {
  const status = document.createElement('p');
  status.className = 'professionals-note';
  status.dataset.newsStatus = '';
  status.textContent = message;
  newsList.replaceChildren(status);
}

function renderNews(articles) {
  if (!articles.length) {
    showNewsStatus('Não encontramos notícias recentes dessas fontes. Tente buscar novamente mais tarde.');
    return;
  }

  const cards = articles.map((article, index) => {
    const card = document.createElement('article');
    card.className = 'library-news-card';

    const art = document.createElement('div');
    art.className = `library-news-art ${newsStyles[index % newsStyles.length]}`;
    art.setAttribute('aria-hidden', 'true');
    art.textContent = newsIcons[index % newsIcons.length];

    const copy = document.createElement('div');
    copy.className = 'library-news-copy';

    const meta = document.createElement('div');
    meta.className = 'library-news-meta';
    const source = document.createElement('span');
    source.textContent = article.source;
    const date = document.createElement('time');
    date.textContent = article.date;
    meta.append(source, date);

    const title = document.createElement('h3');
    title.textContent = article.title;
    const summary = document.createElement('p');
    summary.textContent = article.summary;
    const link = document.createElement('a');
    link.className = 'library-news-link';
    link.href = article.url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = 'Ler notícia';
    copy.append(meta, title, summary, link);
    card.append(art, copy);
    return card;
  });

  newsList.replaceChildren(...cards);
}

async function loadNews() {
  newsList.setAttribute('aria-busy', 'true');
  newsRefreshButton.disabled = true;
  showNewsStatus('Buscando notícias recentes em fontes confiáveis...');

  try {
    const response = await fetch('/biblioteca/noticias');
    const result = await response.json();
    if (!response.ok) {
      throw new Error(
        typeof result.detail === 'string'
          ? result.detail
          : 'Não foi possível buscar notícias agora.',
      );
    }
    if (!Array.isArray(result.articles) || result.articles.length > 3) {
      throw new Error('A lista de notícias recebida está em um formato inválido.');
    }
    renderNews(result.articles);
  } catch (error) {
    showNewsStatus(
      error instanceof Error
        ? error.message
        : 'Não foi possível conectar à busca de notícias.',
    );
  } finally {
    newsList.setAttribute('aria-busy', 'false');
    newsRefreshButton.disabled = false;
  }
}

newsRefreshButton.addEventListener('click', loadNews);
loadNews();
