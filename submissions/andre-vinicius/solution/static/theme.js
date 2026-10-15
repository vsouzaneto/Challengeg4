(function(){
  const key='foco-theme';
  const choices=['auto','light','dark'];
  function apply(value){
    const choice=choices.includes(value)?value:'auto';
    document.documentElement.dataset.theme=choice;
    document.documentElement.style.colorScheme=choice==='auto'?'light dark':choice;
    for(const select of document.querySelectorAll('[data-theme-choice]'))select.value=choice;
    try{localStorage.setItem(key,choice)}catch{}
  }
  let saved='auto';
  try{saved=localStorage.getItem(key)||'auto'}catch{}
  apply(saved);
  document.addEventListener('change',event=>{if(event.target.matches('[data-theme-choice]'))apply(event.target.value)});
})();
