const journal = document.querySelector('#journal');
const body = document.querySelector('#body');
let dirty = false;
function countWords() {
  const words = body.value.trim().split(/\s+/).filter(Boolean).length;
  document.querySelector('#word-count').textContent = `${words} ${words === 1 ? 'word' : 'words'}`;
}
countWords();
journal.addEventListener('input', () => {
  dirty = true;
  document.querySelector('#status').textContent = 'Unsaved changes';
  countWords();
});
journal.addEventListener('submit', () => { dirty = false; });
window.addEventListener('beforeunload', event => {
  if (dirty) { event.preventDefault(); event.returnValue = ''; }
});
document.querySelector('.delete-form')?.addEventListener('submit', event => {
  if (!confirm('Delete this entry permanently?')) event.preventDefault();
  else dirty = false;
});
