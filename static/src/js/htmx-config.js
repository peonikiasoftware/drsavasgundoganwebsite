/**
 * HTMX config — attach Django CSRF token automatically.
 */
(function () {
  function getCookie(name) {
    const m = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]*)'));
    return m ? decodeURIComponent(m[2]) : null;
  }

  document.addEventListener('htmx:configRequest', (evt) => {
    const csrftoken = getCookie('csrftoken');
    if (csrftoken) {
      evt.detail.headers['X-CSRFToken'] = csrftoken;
    }
  });
})();
