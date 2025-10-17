document.addEventListener('DOMContentLoaded', function(){
  const btn = document.getElementById('theme-toggle');
  if(!btn) return;
  const root = document.documentElement;
  const saved = localStorage.getItem('mf-theme');
  if(saved === 'dark') document.body.classList.add('dark');
  btn.addEventListener('click', function(){
    document.body.classList.toggle('dark');
    localStorage.setItem('mf-theme', document.body.classList.contains('dark') ? 'dark' : 'light');
  });
});