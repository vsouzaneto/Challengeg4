const library={
  'business-spec':['Especificação de negócio','business-spec.md'],
  'functional-spec':['Especificação funcional','functional-spec.md'],
  'technical-spec':['Especificação técnica','technical-spec.md'],
  'test-plan':['Plano de testes','test-plan.md'],
  operations:['Operação e entrega','operations.md'],
  'product-roadmap':['Evoluções propostas','product-roadmap.md'],
  'data-audit':['Auditoria dos dados','data-audit.md'],
  'case-development':['Como foi desenvolvido','case-development.md'],
  'process-log':['Registro do processo','process-log.md']
};
const fileToKey=Object.fromEntries(Object.entries(library).map(([key,[,file]])=>[file,key]));
fileToKey['PROCESS_LOG.md']='process-log';
function inline(parent,value){
  const pattern=/\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*|`([^`]+)`/g;let last=0,match;
  while((match=pattern.exec(value))){
    if(match.index>last)parent.append(document.createTextNode(value.slice(last,match.index)));
    if(match[1]){const href=match[2];const link=document.createElement('a');link.textContent=match[1];if(/^https?:\/\//.test(href))link.href=href;else if(href.endsWith('.md')){const key=fileToKey[href.split('/').pop()];link.href=key?`/reader.html?doc=${encodeURIComponent(key)}`:'#'}else if(/\.(png|jpe?g|webp)$/i.test(href)){link.href='/evidence/'+encodeURIComponent(href.split('/').pop());link.target='_blank';link.rel='noopener'}else link.href='#';parent.append(link)}
    else if(match[3]){const strong=document.createElement('strong');strong.textContent=match[3];parent.append(strong)}
    else{const code=document.createElement('code');code.textContent=match[4];parent.append(code)}
    last=pattern.lastIndex;
  }
  if(last<value.length)parent.append(document.createTextNode(value.slice(last)));
}
function startsBlock(line,next){return /^#{1,4} |^```|^\s*[-*] |^\s*\d+\. |^\|/.test(line)||(/^\|/.test(next||'')&&/^\|/.test(line))}
function render(markdown){const root=document.getElementById('reader-body');root.replaceChildren();const lines=markdown.split(/\r?\n/);let i=0;
  while(i<lines.length){const line=lines[i].trim();if(!line){i++;continue}
    if(line.startsWith('```')){const code=[];i++;while(i<lines.length&&!lines[i].trim().startsWith('```'))code.push(lines[i++]);i++;const pre=document.createElement('pre');const el=document.createElement('code');el.textContent=code.join('\n');pre.append(el);root.append(pre);continue}
    const image=/^!\[([^\]]*)\]\(([^)]+\.(?:png|jpe?g|webp))\)$/i.exec(line);if(image){const fig=document.createElement('figure');fig.className='reader-figure';const img=document.createElement('img');img.src='/evidence/'+encodeURIComponent(image[2].split('/').pop());img.alt=image[1];img.loading='lazy';const cap=document.createElement('figcaption');cap.textContent=image[1];fig.append(img,cap);root.append(fig);i++;continue}
    const heading=/^(#{1,4})\s+(.+)$/.exec(line);if(heading){const el=document.createElement(`h${heading[1].length}`);inline(el,heading[2]);root.append(el);i++;continue}
    if(line.startsWith('|')&&i+1<lines.length&&/^\|?[\s|:-]+\|?$/.test(lines[i+1].trim())){const table=document.createElement('table');let rowIndex=0;while(i<lines.length&&lines[i].trim().startsWith('|')){if(rowIndex!==1){const tr=document.createElement('tr');for(const cell of lines[i].trim().replace(/^\||\|$/g,'').split('|')){const el=document.createElement(rowIndex===0?'th':'td');inline(el,cell.trim());tr.append(el)}table.append(tr)}rowIndex++;i++}const box=document.createElement('div');box.className='reader-table';box.append(table);root.append(box);continue}
    const bullet=/^\s*([-*]|\d+\.)\s+/.exec(line);if(bullet){const ordered=/\d/.test(bullet[1]);const list=document.createElement(ordered?'ol':'ul');while(i<lines.length){const current=lines[i].trim();const token=/^([-*]|\d+\.)\s+(.+)$/.exec(current);if(!token||/\d/.test(token[1])!==ordered)break;const li=document.createElement('li');inline(li,token[2]);list.append(li);i++}root.append(list);continue}
    const parts=[line];i++;while(i<lines.length&&lines[i].trim()&&!startsBlock(lines[i].trim(),lines[i+1]))parts.push(lines[i++].trim());const p=document.createElement('p');inline(p,parts.join(' '));root.append(p);
  }
}
async function main(){const key=new URLSearchParams(location.search).get('doc');const item=library[key];const root=document.getElementById('reader-body');if(!item){root.textContent='Documento não encontrado.';return}document.title=`${item[0]} · Foco`;document.getElementById('reader-title').textContent=item[0];const url=`/source/${item[1]}`;const source=document.getElementById('reader-source');source.href=url;source.hidden=false;try{const response=await fetch(url);if(!response.ok)throw Error(`HTTP ${response.status}`);render(await response.text())}catch(error){root.textContent=`Não foi possível abrir o documento: ${error.message}`}}
main();
