const $=s=>document.querySelector(s);
const messages=$('#messages');
let history=[],busy=false,currentPage='chat',activeProject=null,currentConversationProject=null,selectedPackId=null,selectedDocumentPath=null,workspaceSummary=null;

// 4.2.1 P0: one global Read Aloud controller. Only one message may speak at a time.
let activeReader=null;
let readerSequence=0;
function setReaderIdle(reader){
 if(!reader)return;
 if(reader.button){reader.button.innerHTML='<span class="speak-icon" aria-hidden="true">🔊</span><span>Read Aloud</span>';reader.button.classList.remove('reading');reader.button.hidden=false;reader.button.setAttribute('aria-label','Read message aloud');reader.button.setAttribute('aria-pressed','false');reader.button.dataset.tooltip='Read this response aloud';}
 if(reader.status){reader.status.hidden=true;reader.status.setAttribute('aria-hidden','true');reader.status.removeAttribute('tabindex');reader.status.removeAttribute('data-tooltip');}
 if(reader.button?.parentElement){reader.button.parentElement.querySelector('.stop-reading')?.remove();}
}
function stopReading(){
 const reader=activeReader;
 activeReader=null;
 readerSequence++;
 if('speechSynthesis' in window) window.speechSynthesis.cancel();
 setReaderIdle(reader);
}
function startReading(text,button){
 if(!('speechSynthesis' in window)){return;}
 const content=String(text||'').trim();
 if(!content)return;
 if(activeReader?.button===button){stopReading();return;}
 stopReading();
 const token=++readerSequence;
 const utterance=new SpeechSynthesisUtterance(content);
 const status=button.closest('.actions')?.querySelector('[data-speaking-status]');
 activeReader={utterance,button,status,token};
 button.classList.add('reading');
 button.hidden=true;
 button.setAttribute('aria-label','Currently reading this response aloud');
 button.setAttribute('aria-pressed','true');
 if(status){status.hidden=false;status.removeAttribute('aria-hidden');status.textContent='Speaking...';status.setAttribute('tabindex','0');status.dataset.tooltip='Currently reading this response aloud';}
 const stopButton=document.createElement('button');
 stopButton.type='button';
 stopButton.className='stop-reading';
 stopButton.setAttribute('aria-label','Stop reading aloud');
 stopButton.textContent='◼ Stop';
 stopButton.dataset.tooltip='Stop audio playback';
 button.insertAdjacentElement('afterend',stopButton);
 stopButton.onclick=()=>stopReading();
 const finish=()=>{
   if(activeReader?.token!==token)return;
   activeReader=null;
   const stopButton=button.parentElement?.querySelector('.stop-reading');
   stopButton?.remove();
   setReaderIdle({button,status});
 };
 utterance.onend=finish;
 utterance.onerror=finish;
 window.speechSynthesis.speak(utterance);
}
const esc=t=>String(t??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const post=async(url,body)=>{const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body||{})});let j={};try{j=await r.json()}catch{}if(!r.ok)throw Error(j.error||`HTTP ${r.status}`);return j;};

// 4.2.1 P0: accessible destructive confirmation. Native confirm() cannot provide
// a reliable focus target, focus trap, or accessible dialog semantics.
let destructiveDialog=null;
function closeDestructiveDialog(result=false){
 const d=destructiveDialog;if(!d)return;
 destructiveDialog=null;
 document.removeEventListener('keydown',d.onKeydown,true);
 d.root.remove();
 d.restore?.focus?.();
 d.resolve(result);
}
function confirmDestructive({title,target,message,confirmLabel='Delete',cancelLabel='Cancel'}){
 return new Promise(resolve=>{
   if(destructiveDialog)closeDestructiveDialog(false);
   const restore=document.activeElement;
   const root=document.createElement('div');
   root.className='dialog-backdrop';
   root.setAttribute('role','presentation');
   root.innerHTML=`<div class="confirm-dialog" role="dialog" aria-modal="true" aria-labelledby="confirm-dialog-title" aria-describedby="confirm-dialog-description" tabindex="-1"><h2 id="confirm-dialog-title">${esc(title)}</h2><p class="confirm-target">${esc(target||'')}</p><p id="confirm-dialog-description">${esc(message)}</p><div class="confirm-actions"><button type="button" class="btn" data-dialog-cancel>${esc(cancelLabel)}</button><button type="button" class="btn danger" data-dialog-confirm>${esc(confirmLabel)}</button></div></div>`;
   document.body.appendChild(root);
   const dialog=root.querySelector('.confirm-dialog');
   const cancel=root.querySelector('[data-dialog-cancel]');
   const confirm=root.querySelector('[data-dialog-confirm]');
   const focusables=()=>[...dialog.querySelectorAll('button:not([disabled]),[href],input:not([disabled]),textarea:not([disabled]),select:not([disabled]),[tabindex]:not([tabindex="-1"])')];
   const onKeydown=e=>{
     if(e.key==='Escape'){e.preventDefault();closeDestructiveDialog(false);return;}
     if(e.key==='Tab'){
       const f=focusables();if(!f.length)return;
       const first=f[0],last=f[f.length-1];
       if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
       else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
     }
   };
   destructiveDialog={root,restore,resolve,onKeydown};
   cancel.onclick=()=>closeDestructiveDialog(false);
   confirm.onclick=()=>closeDestructiveDialog(true);
   root.addEventListener('mousedown',e=>{if(e.target===root)closeDestructiveDialog(false);});
   document.addEventListener('keydown',onKeydown,true);
   // Safety rule: destructive dialogs always open with Cancel focused.
   cancel.focus();
 });
}

function setBusy(v){busy=v;$('#send').disabled=v;$('#send').style.opacity=v?'.55':'1';}
function loadActiveProject(){try{activeProject=JSON.parse(localStorage.getItem('angel_active_project')||'null')}catch{activeProject=null}}
function setActiveProject(project){activeProject=project||null;if(activeProject)localStorage.setItem('angel_active_project',JSON.stringify(activeProject));else localStorage.removeItem('angel_active_project');updateProjectChip();refreshContext();}
function updateProjectChip(){const project=currentConversationProject;const label=project?`Project: ${project.name}`:'Global chat';const el=$('#activeProject');if(el)el.textContent=label;const hint=$('#chatProjectHint');if(hint)hint.textContent=project?` · ${label}`:' · Global conversation';}

function addMessage(who,text){
 const el=document.createElement('article');el.className='message '+(who==='Me'?'user':'');
 el.innerHTML=`<div class="meta"><b>${who==='Me'?'M':'🪽'} ${who==='Me'?'You':'Angel'}</b><span>${new Date().toLocaleTimeString([], {hour:'numeric',minute:'2-digit'})}</span></div><div class="body">${esc(text)}</div><div class="actions"><button data-copy>Copy</button><div class="speaking-indicator" data-speaking-status role="status" aria-live="polite" aria-hidden="true" hidden><span class="speaking-icon" aria-hidden="true">🔊</span><span>Speaking...</span><span class="sr-only">Reading response aloud</span></div><button data-speak aria-label="Read message aloud" aria-pressed="false" data-tooltip="Read this response aloud"><span class="speak-icon" aria-hidden="true">🔊</span><span>Read Aloud</span></button></div>`;
 el.querySelector('[data-copy]').onclick=()=>navigator.clipboard?.writeText(el.querySelector('.body').textContent||'');
 const speakButton=el.querySelector('[data-speak]');
 speakButton.setAttribute('aria-label','Read message aloud');
 speakButton.onclick=()=>startReading(el.querySelector('.body').textContent||'',speakButton);
 messages.appendChild(el);messages.scrollTop=messages.scrollHeight;return el;
}

function cacheConversation(item){if(!item?.id)return;const a=JSON.parse(localStorage.getItem('angel_conversations')||'[]').filter(x=>x.id!==item.id);localStorage.setItem('angel_conversations',JSON.stringify([{...item},...a].slice(0,200)));}
async function refreshConversationHistory(){
 try{const [cr,pr]=await Promise.all([fetch('/api/conversations').then(r=>r.json()),fetch('/api/projects').then(r=>r.json())]);
  const list=cr.conversations||[], projects=pr.projects||[]; list.forEach(cacheConversation); renderConversationTree(list,projects);
 }catch{renderConversationTree();}
}
function renderConversationTree(items,projects){
 const tree=$('#conversationTree');if(!tree)return;const q=($('#conversationSearch')?.value||'').trim().toLowerCase();
 const list=(items||JSON.parse(localStorage.getItem('angel_conversations')||'[]')).filter(x=>!q||String(x.title||'').toLowerCase().includes(q));
 const groups=new Map([['', {id:'',name:'General',items:[]}]]);
 (projects||[]).forEach(p=>groups.set(p.id,{id:p.id,name:p.name,items:[]}));
 list.forEach(item=>{const key=item.project_id||'';if(!groups.has(key))groups.set(key,{id:key,name:'Project',items:[]});groups.get(key).items.push(item);});
 tree.innerHTML='';
 for(const g of groups.values()){
   if(!g.items.length && q)continue;
   const section=document.createElement('section');section.className='conversation-group';
   const head=document.createElement('button');head.className='conversation-group-head';head.innerHTML=`<span>${g.id?'📁':'○'} ${esc(g.name)}</span><span>${g.items.length}</span>`;
   const body=document.createElement('div');body.className='conversation-group-body';
   g.items.slice(0,20).forEach(item=>body.appendChild(conversationRow(item)));
   head.onclick=()=>body.classList.toggle('collapsed');section.append(head,body);tree.appendChild(section);
 }
 if(!tree.children.length)tree.innerHTML='<div class="empty">No conversations found.</div>';
}
function conversationRow(item){
 const row=document.createElement('div');row.className='history-item';row.dataset.conversation=item.id;
 row.innerHTML=`<span class="history-title">${item.pinned?'★ ':''}${esc(item.title||'New Chat')}</span><span class="history-actions"><button title="Pin/unpin">${item.pinned?'★':'☆'}</button><button title="Delete">×</button></span>`;
 row.querySelector('.history-title').onclick=()=>loadConversation(item.id);
 row.querySelector('.history-actions button:first-child').onclick=e=>{e.stopPropagation();togglePin(item)};
 row.querySelector('.history-actions button:last-child').onclick=e=>{e.stopPropagation();deleteConversation(item.id)};
 return row;
}
async function togglePin(item){try{const j=await post('/api/conversations/pin',{conversation_id:item.id,pinned:!item.pinned});cacheConversation(j.conversation);refreshConversationHistory()}catch(e){alert(e.message)}}
async function deleteConversation(id){let target='This conversation';try{const r=await fetch('/api/conversations/'+encodeURIComponent(id));if(r.ok){const j=await r.json();target=j.conversation?.title||target;}}catch{}const ok=await confirmDestructive({title:'Delete Chat?',target,message:'This chat will be permanently deleted.',confirmLabel:'Delete Chat'});if(!ok)return;try{await post('/api/conversations/delete',{conversation_id:id});if(window.angelConversationId===id)startNewChat();refreshConversationHistory()}catch(e){alert(e.message)}}
async function createServerConversation(title,projectId=''){
 const j=await post('/api/conversations',{title,project_id:projectId||''});window.angelConversationId=j.conversation.id;
 currentConversationProject=null;
 if(j.conversation.project_id){try{const pr=await fetch('/api/projects/'+encodeURIComponent(j.conversation.project_id)).then(r=>r.json());currentConversationProject=pr.project||null}catch{}}
 cacheConversation(j.conversation);updateProjectChip();return j.conversation;
}
async function loadConversation(id){
 stopReading();
 if(busy)return;const r=await fetch('/api/conversations/'+encodeURIComponent(id));if(!r.ok)return alert('Could not load conversation.');
 const j=await r.json();window.angelConversationId=id;history=(j.messages||[]).map(x=>({role:x.role,content:x.content}));currentConversationProject=null;
 if(j.conversation?.project_id){try{const pr=await fetch('/api/projects/'+encodeURIComponent(j.conversation.project_id)).then(r=>r.json());currentConversationProject=pr.project||null}catch{currentConversationProject={id:j.conversation.project_id,name:'Project'}}}
 messages.innerHTML='';history.forEach(x=>addMessage(x.role==='user'?'Me':'Angel',x.content));renderPage('chat');cacheConversation(j.conversation);refreshConversationHistory();refreshContext();
}
async function startNewChat(){stopReading();if(busy)return;window.angelConversationId=null;history=[];currentConversationProject=null;messages.innerHTML='';renderPage('chat');updateProjectChip();$('#prompt').focus();refreshContext();}
async function send(){
 stopReading();
 if(busy)return;const input=$('#prompt'),text=input.value.trim();if(!text)return;input.value='';addMessage('Me',text);history.push({role:'user',content:text});const pending=addMessage('Angel','Thinking…');setBusy(true);
 try{
  if(!window.angelConversationId)await createServerConversation(text.slice(0,70),'');
  const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text,model:$('#model').value,conversation_id:window.angelConversationId})});
  if(!res.ok){let detail='HTTP '+res.status;try{const err=await res.json();if(err&&err.error)detail=err.error;}catch{}throw Error(detail);}const reader=res.body.getReader(),decoder=new TextDecoder();let out='';pending.querySelector('.body').textContent='';
  while(true){const {value,done}=await reader.read();if(done)break;out+=decoder.decode(value,{stream:true});pending.querySelector('.body').textContent=out;messages.scrollTop=messages.scrollHeight;}
  history.push({role:'assistant',content:out.trim()});cacheConversation({id:window.angelConversationId,title:text.slice(0,70),updated_at:new Date().toISOString(),project_id:currentConversationProject?.id||''});
  try{const info=await fetch('/api/v1/engineering/latest-for-conversation/'+encodeURIComponent(window.angelConversationId)).then(r=>r.json());if(info.rag_run)await addEvidenceCard(pending,info.rag_run.id);}catch{}
  refreshConversationHistory();refreshContext();
 }catch(e){pending.querySelector('.body').textContent='Angel error: '+e.message}finally{setBusy(false);}
}
async function addEvidenceCard(messageEl,ragId){
 const r=await fetch('/api/v1/engineering/inspect/'+encodeURIComponent(ragId));if(!r.ok)return;const j=await r.json();const count=Number(j.retrieval?.selected||0);
 const evaluation=j.evaluation? (j.evaluation.result?.status||'Evaluated'):'Not evaluated';
 const card=document.createElement('div');card.className="evidence-card collapsed";
 card.innerHTML=`<button class="evidence-toggle"><span>▸ Retrieved knowledge</span><span>${count} ${count===1?'chunk':'chunks'}</span></button><div class="evidence-details"><div class="evidence-summary">${count} knowledge ${count===1?'chunk':'chunks'} used</div><div class="evidence-meta">Retrieval scope: ${esc(j.project_context?.project?.name?'Project Knowledge':'Indexed Knowledge')} · Evaluation: ${esc(evaluation)}</div><button class="inspect-btn">Inspect Retrieval</button></div>`;
 card.querySelector('.evidence-toggle').onclick=()=>{card.classList.toggle('collapsed');card.querySelector('.evidence-toggle span:first-child').textContent=card.classList.contains('collapsed')?'▸ Retrieved knowledge':'▾ Retrieved knowledge'};
 card.querySelector('.inspect-btn').onclick=()=>openInspector(ragId);messageEl.appendChild(card);
}
async function openInspector(ragId){
 const r=await fetch('/api/v1/engineering/inspect/'+encodeURIComponent(ragId));if(!r.ok)return alert('Retrieval inspection is unavailable.');const j=await r.json();const existing=$('#inspector');if(existing)existing.remove();
 const overlay=document.createElement('div');overlay.id='inspector';overlay.className='inspector-overlay';
 overlay.innerHTML=`<aside class="inspector"><div class="inspector-head"><div><small>Evidence</small><h2>How Angel handled this question</h2></div><button class="icon-btn" id="closeInspector">×</button></div><section><label>Question</label><p>${esc(j.rag_run.question)}</p></section><section><label>Retrieval Scope</label><p>${esc(j.project_context?.project?.name||'Indexed Knowledge')}</p></section><section><label>Retrieval</label><div class="inspector-stats"><span><b>${j.retrieval.candidates}</b> candidates</span><span><b>${j.retrieval.selected}</b> selected</span><span><b>${j.retrieval.rejected}</b> rejected</span></div></section><section><label>Context</label><p>${j.context.chunks} chunks · ${j.context.tokens||0} approximate tokens</p></section><section><label>Answer</label><pre>${esc(j.answer||'')}</pre></section><section><label>Sources</label>${(j.evidence||[]).map(x=>`<div class="inspector-evidence"><b>${esc(x.evidence?.document?.title||'Knowledge source')}</b><p>${esc(x.evidence?.passage||'')}</p></div>`).join('')||'<p>Angel did not retrieve knowledge for this response.</p>'}</section><section><label>Evaluation</label><p>${j.evaluation?esc(j.evaluation.result?.status||'Evaluated'):'Not evaluated'}</p></section></aside>`;
 document.body.appendChild(overlay);overlay.querySelector('#closeInspector').onclick=()=>overlay.remove();overlay.onclick=e=>{if(e.target===overlay)overlay.remove()};
}

async function refreshContext(){
 const panel=$('#contextPanel');if(!panel)return;
 try{
  const pid=currentConversationProject?.id||activeProject?.id||'';
  const url='/api/workspace/summary'+(pid?'?project_id='+encodeURIComponent(pid):'');
  const j=await fetch(url).then(r=>r.json());workspaceSummary=j;
  panel.innerHTML=renderContext(j);if(!panel.classList.contains('hidden'))bindContextActions();
 }catch{panel.innerHTML='<div class="context-head"><b>Angel Context</b><button id="closeContext">×</button></div><div class="context-empty">Context is temporarily unavailable.</div>';}
}
function renderContext(j){
 const p=j.project||null;const k=j.knowledge||{};const skills=j.skills||[];const tools=j.tools||[];
 return `<div class="context-head"><div><span class="eyebrow">ACTIVE CONTEXT</span><h3>Angel Context</h3></div><button id="closeContext">×</button></div>
 <div class="context-block"><label>Project</label><b>${esc(p?.name||'No project')}</b><small>${p?'Project workspace':'Global conversation'}</small></div>
 <div class="context-block"><label>Conversation</label><b>${esc(j.conversation?.title||'New Chat')}</b><small>${j.conversation?.project_id?'Project-scoped':'Unscoped'}</small></div>
 <div class="context-block"><label>Knowledge</label><b>${k.documents||0} documents</b><small>${k.chunks||0} retrieval chunks indexed</small></div>
 <div class="context-block"><label>Skills</label><b>${skills.length} available</b><small>${skills.slice(0,3).map(esc).join(' · ')||'Capability inventory'}</small></div>
 <div class="context-block"><label>Retrieval Scope</label><b>${p?'Project Knowledge':'Indexed Knowledge'}</b><small>Resolved from persisted conversation scope</small></div>
 <div class="context-block"><label>Model</label><b>${esc(j.model?.name||'Unknown')}</b><small>${esc(j.model?.backend||'Local backend')} · ${j.model?.context||'Context capacity unknown'}</small></div>`;
}
function bindContextActions(){$('#closeContext')?.addEventListener('click',()=>$('#contextPanel').classList.add('hidden'));}
async function toggleContext(){const p=$('#contextPanel');p.classList.toggle('hidden');if(!p.classList.contains('hidden')){await refreshContext();bindContextActions()}}

function renderHome(){
 const c=$('#pageContent');c.classList.remove('hidden');messages.classList.add('hidden');
 const p=activeProject;const name=p?.name||'Angel Nexus';
 c.innerHTML=`<div class="home-page"><div class="home-hero"><span class="eyebrow">ANGEL NEXUS 4.2</span><h1>What are we working on?</h1><p>One assistant, one workspace, one context. Start with a conversation or enter a project workspace.</p><div class="home-actions"><button class="btn primary" id="homeAsk">Ask Angel</button><button class="btn" id="homeKnowledge">Search Knowledge</button></div></div>
 <div class="home-grid"><div class="home-card"><span>Active Workspace</span><b>${esc(name)}</b><small>${p?'Project context selected':'No project selected'}</small></div><div class="home-card knowledge-home-card"><span>Knowledge</span><b>${workspaceSummary?.knowledge?.cards?esc(workspaceSummary.knowledge.cards):'Ready'}</b><small>${workspaceSummary?.knowledge?.cards?`${esc(workspaceSummary.knowledge.cards)} knowledge cards available · ${esc(workspaceSummary?.knowledge?.documents||0)} user documents indexed`:'Knowledge library ready'}</small></div></div>
 <div class="recent-work"><div class="section-title"><h2>Recent Work</h2><button class="text-btn" id="homeChats">View chats</button></div><div id="homeRecent"></div></div></div>`;
 $('#homeAsk').onclick=()=>{renderPage('chat');$('#prompt').focus()};
 $('#homeKnowledge').onclick=()=>renderPage('knowledge');
 $('#homeChats').onclick=()=>renderPage('chat');
 renderHomeRecent();
}
async function renderHomeRecent(){const el=$('#homeRecent');if(!el)return;try{const j=await fetch('/api/conversations').then(r=>r.json());const rows=(j.conversations||[]).slice(0,5);el.innerHTML=rows.map(x=>`<button class="recent-row" data-id="${esc(x.id)}"><span>${esc(x.title||'New Chat')}</span><small>${x.project_id?'Project chat':'General'}</small></button>`).join('')||'<div class="empty">No recent work yet.</div>';el.querySelectorAll('[data-id]').forEach(b=>b.onclick=()=>loadConversation(b.dataset.id));}catch{el.innerHTML='<div class="empty">Recent work unavailable.</div>'}}

async function renderSkills(){
 const c=$('#pageContent');c.classList.remove('hidden');messages.classList.add('hidden');c.innerHTML='<div class="simple-page"><div class="knowledge-head"><div><h2>Skills</h2><p>Capabilities available to Angel in this build.</p></div></div><div id="skillsGrid" class="skills-grid">Loading…</div></div>';
 try{const cap=await fetch('/api/capabilities').then(r=>r.json());const caps=cap.capabilities||[];$('#skillsGrid').innerHTML=`<div class="skills-column"><h3>Angel Skills</h3>${caps.map(x=>`<div class="skill-card"><b>${esc(x.name||x.id||'Capability')}</b><small>${esc(x.description||'Available Angel capability')}</small></div>`).join('')||'<div class="empty">No skills available.</div>'}</div>`}catch(e){$('#skillsGrid').textContent='Skills are temporarily unavailable.'}
}

function renderPage(page){
 stopReading();
 currentPage=page;
 document.querySelectorAll('.side-link').forEach(b=>b.classList.toggle('active',b.dataset.page===page));
 const content=$('#pageContent');content.classList.add('hidden');messages.classList.remove('hidden');
 if(page==='chat'){updateProjectChip();return}
 if(page==='home'){renderHome();return}
 messages.classList.add('hidden');content.classList.remove('hidden');
 if(page==='knowledge')renderKnowledge();
 else if(page==='projects')renderProjects();
 else if(page==='skills')renderSkills();
 else content.innerHTML='<div class="simple-page"><div class="knowledge-head"><div><span class="eyebrow">SETTINGS</span><h2>Settings</h2><p>Current user-facing controls for Angel Nexus.</p></div></div><div class="simple-card"><b>Angel Nexus 4.2.1</b><p>Unified Workspace release. Existing 4.1.1 state ownership and runtime behavior remain authoritative.</p></div><div class="simple-card"><b>Future ideas</b><p>Memory remains part of Angel’s internal persistence system, but it is intentionally hidden from the main user navigation in this release. Memory UX can be revisited in a future release without changing the current workspace.</p></div></div>';
}

async function renderProjects(){
 const c=$('#pageContent');c.innerHTML='<div>Loading Projects…</div>';const [j,summary]=await Promise.all([fetch('/api/projects').then(r=>r.json()),fetch('/api/workspace/summary').then(r=>r.json())]);const projects=j.projects||[];j.knowledge=summary.knowledge||{};
 c.innerHTML=`<div class="simple-page project-page"><div class="knowledge-head"><div><span class="eyebrow">WORKSPACES</span><h2>Projects</h2><p>Projects are persistent workspaces. Opening one changes navigation context only; it never rewrites your current conversation.</p></div><button class="btn primary" id="newProject">＋ Create Project</button></div><div class="project-grid">${projects.map(p=>`<article class="workspace-card ${activeProject?.id===p.id?'active':''}"><div class="workspace-card-head"><div><span class="workspace-icon">📁</span><h3>${esc(p.name)}</h3></div><span class="scope-badge">${activeProject?.id===p.id?'Active workspace':'Workspace'}</span></div><p>${esc(p.description||'Focused Angel workspace')}</p><div class="metric-grid"><div><b>${p.conversation_count||0}</b><small>Chats</small></div><div><b>${j.knowledge?.documents||0}</b><small>Knowledge</small></div><div><b>0</b><small>Files</small></div></div><div class="workspace-context-row"><span>Retrieval Scope</span><b>Project Knowledge</b></div><div class="project-actions"><button class="btn" data-project="${esc(p.id)}">${activeProject?.id===p.id?'Workspace Selected':'Open Workspace'}</button><button class="btn primary" data-start-project="${esc(p.id)}">Start Project Chat</button><button class="btn danger" data-delete-project="${esc(p.id)}" title="Delete this project">Delete</button></div></article>`).join('')||'<div class="empty">No projects yet. Create one when a body of work needs its own workspace.</div>'}</div></div>`;
 $('#newProject').onclick=async()=>{const name=prompt('Project name:');if(!name)return;const description=prompt('Short description (optional):','Focused Angel workspace')||'';try{const made=await post('/api/projects',{name,description});setActiveProject(made.project);renderProjects()}catch(e){alert(e.message)}};
 c.querySelectorAll('[data-project]').forEach(b=>b.onclick=()=>{const p=projects.find(x=>x.id===b.dataset.project);setActiveProject(p);renderProjects()});
 c.querySelectorAll('[data-start-project]').forEach(b=>b.onclick=async()=>{const p=projects.find(x=>x.id===b.dataset.startProject);if(!p)return;try{await createServerConversation('New '+p.name+' Chat',p.id);currentConversationProject=p;history=[];messages.innerHTML='';renderPage('chat');$('#prompt').focus();refreshContext()}catch(e){alert(e.message)}});
 c.querySelectorAll('[data-delete-project]').forEach(b=>b.onclick=async e=>{e.stopPropagation();const p=projects.find(x=>x.id===b.dataset.deleteProject);if(!p)return;const count=Number(p.conversation_count||0);const ok=await confirmDestructive({title:'Delete Project?',target:p.name,message:count?`This removes the project workspace and keeps its ${count} conversation${count===1?'':'s'} in Global chat history.`:'This removes the project workspace. This action cannot be undone.',confirmLabel:'Delete Project'});if(!ok)return;try{await post('/api/projects/'+encodeURIComponent(p.id)+'/delete',{});if(activeProject?.id===p.id){setActiveProject(null);}if(currentConversationProject?.id===p.id){currentConversationProject=null;updateProjectChip();}await refreshConversationHistory();renderProjects();}catch(err){alert(err.message)}});
}

async function renderKnowledge(){const c=$('#pageContent');c.innerHTML='<div>Loading Knowledge Center…</div>';const j=await fetch('/api/knowledge').then(r=>r.json());const x=j.center||{};if(selectedPackId && !(x.packs||[]).some(p=>p.id===selectedPackId)){selectedPackId=null;selectedDocumentPath=null;}c.innerHTML=`<div class="knowledge-head"><div><h2>Knowledge Center</h2><p>Teach Angel with Markdown and knowledge packs. Select a pack to inspect its documents, then open a document in the editor.</p></div><div class="actions-row"><button class="btn primary" id="importPack">＋ Import Pack</button><button class="btn" id="importMd">＋ Import Markdown</button><button class="btn" id="importFolder">＋ Import Folder</button><button class="btn" id="newKnowledge">＋ New Knowledge File</button><button class="btn" id="newCategory">＋ New Category</button><button class="btn" id="reindex">↻ Rebuild Index</button></div></div><div class="stats"><div class="stat"><b>${j.status?.total_cards||0}</b><small>Knowledge cards</small></div><div class="stat"><b>${x.documents||0}</b><small>User documents</small></div><div class="stat"><b>${x.chunks||0}</b><small>Retrieval chunks</small></div><div class="stat"><b>${(x.packs||[]).length}</b><small>Knowledge packs</small></div><div class="stat"><b>${esc(x.indexed_at||'Not indexed')}</small></div></div><div class="knowledge-search"><input id="knowledgeSearch" placeholder="Search your knowledge…"></div><div class="knowledge-grid"><div class="knowledge-list"><h3>Library</h3><div id="docList"></div><h3 style="margin-top:18px">Packs</h3><div id="packList"></div></div><div class="knowledge-editor"><h3 id="editorHeading">${selectedPackId?'Select a document':'Select a document'}</h3><div class="editor-title"><input id="docPath" placeholder="knowledge file path" disabled><button class="btn" id="saveDoc" disabled>Save</button><button class="btn danger" id="deleteDoc" disabled>Delete</button></div><textarea id="docContent" placeholder="Select a Markdown document, or create a new one." disabled></textarea></div></div>`;bindKnowledge(x);}
function bindKnowledge(x){const docs=x.files||[],docList=$('#docList'),packList=$('#packList');const activePack=(x.packs||[]).find(p=>p.id===selectedPackId)||null;const packDocs=activePack?docs.filter(d=>d.source==='pack'&&d.pack===activePack.id):[];docList.innerHTML=selectedPackId?(packDocs.map(d=>`<div class="doc ${selectedDocumentPath===d.path?'active':''}" data-doc="${esc(d.path)}"><b>${esc(d.title)}</b><small>${esc(d.path)}</small></div>`).join('')||'<div class="empty">This pack contains no Markdown documents.</div>'):(docs.filter(d=>d.source==='user').map(d=>`<div class="doc ${selectedDocumentPath===d.path?'active':''}" data-doc="${esc(d.path)}"><b>${esc(d.title)}</b><small>${esc(d.path)}</small></div>`).join('')||'<div class="empty">No standalone knowledge yet.</div>');packList.innerHTML=(x.packs||[]).map(p=>`<div class="pack ${selectedPackId===p.id?'active':''}" data-pack="${esc(p.id)}"><div><b>${esc(p.name)}</b><small>v${esc(p.version)} · ${p.documents} docs · ${p.chunks} chunks</small><small>${esc(p.description||p.category||'Knowledge pack')}</small></div><button class="btn danger pack-delete" data-delete-pack="${esc(p.id)}" title="Remove this entire knowledge pack">Remove</button></div>`).join('')||'<div class="empty">No packs imported.</div>';docList.querySelectorAll('[data-doc]').forEach(el=>el.onclick=()=>openDoc(el.dataset.doc));packList.querySelectorAll('[data-pack]').forEach(el=>el.onclick=e=>{if(e.target.closest('[data-delete-pack]'))return;selectedPackId=el.dataset.pack;selectedDocumentPath=null;renderKnowledge();});packList.querySelectorAll('[data-delete-pack]').forEach(b=>b.onclick=async e=>{e.stopPropagation();const p=(x.packs||[]).find(item=>item.id===b.dataset.deletePack);if(!p)return;const ok=await confirmDestructive({title:'Remove Knowledge Pack?',target:p.name,message:'Its documents will be removed from future retrieval. Historical conversations, projects, RAG Runs, and evidence are preserved.',confirmLabel:'Remove Pack'});if(!ok)return;try{const r=await post('/api/knowledge/pack',{pack_id:p.id});if(selectedPackId===p.id){selectedPackId=null;selectedDocumentPath=null;}renderKnowledge();}catch(err){alert(err.message)}});$('#importPack').onclick=()=>$('#zipPack').click();$('#importMd').onclick=()=>$('#mdFiles').click();$('#importFolder').onclick=()=>$('#mdFolder').click();$('#newKnowledge').onclick=()=>newDoc();$('#newCategory').onclick=async()=>{const name=prompt('Category name:');if(!name)return;await post('/api/knowledge/category',{name});renderKnowledge()};$('#reindex').onclick=async()=>{await post('/api/knowledge/reindex',{});renderKnowledge()};$('#knowledgeSearch').oninput=async e=>{const q=e.target.value.trim();if(!q){bindKnowledge(x);return;}const r=await fetch('/api/knowledge/search?q='+encodeURIComponent(q)).then(r=>r.json());docList.innerHTML=(r.results||[]).map(d=>`<div class="doc" data-doc="${esc(d.source||d.path||'')}"><b>${esc(d.title)}</b><small>${esc(d.source||'')}</small></div>`).join('')||'<div class="empty">No matching knowledge.</div>';docList.querySelectorAll('[data-doc]').forEach(el=>el.onclick=()=>openDoc(el.dataset.doc));};}
async function openDoc(path){try{const j=await fetch('/api/knowledge/file?path='+encodeURIComponent(path)).then(r=>r.json());if(j.error)throw Error(j.error);selectedDocumentPath=path;$('#editorHeading').textContent=path;$('#docPath').value=path;$('#docContent').value=j.content;$('#docPath').disabled=false;$('#docContent').disabled=false;$('#saveDoc').disabled=false;$('#deleteDoc').disabled=false;$('#saveDoc').onclick=async()=>{try{const saved=await post('/api/knowledge/file',{path:$('#docPath').value,content:$('#docContent').value});selectedDocumentPath=saved.document.path;renderKnowledge();setTimeout(()=>openDoc(selectedDocumentPath),0);}catch(e){alert(e.message)}};$('#deleteDoc').onclick=async()=>{const ok=await confirmDestructive({title:'Delete Knowledge Document?',target:path,message:'This document will be removed from future retrieval and the index will be rebuilt.',confirmLabel:'Delete Document'});if(!ok)return;try{await post('/api/knowledge/file',{path,delete:true});selectedDocumentPath=null;renderKnowledge();}catch(e){alert(e.message)}};}catch(e){selectedDocumentPath=null;alert(e.message)}}
function newDoc(){selectedPackId=null;selectedDocumentPath=null;const path=prompt('New Markdown path (example: Custom/my-knowledge.md):','Custom/new-knowledge.md');if(!path)return;$('#editorHeading').textContent='New Knowledge';$('#docPath').value=path;$('#docContent').value='# New Knowledge\n\nWrite what you want Angel to know here.\n';$('#docPath').disabled=false;$('#docContent').disabled=false;$('#saveDoc').disabled=false;$('#deleteDoc').disabled=true;$('#saveDoc').onclick=async()=>{try{const saved=await post('/api/knowledge/file',{path:$('#docPath').value,content:$('#docContent').value});selectedDocumentPath=saved.document.path;renderKnowledge();setTimeout(()=>openDoc(selectedDocumentPath),0);}catch(e){alert(e.message)}}}
async function importMarkdown(files){const list=[];for(const file of files){if(!file.name.toLowerCase().endsWith('.md'))continue;list.push({path:file.webkitRelativePath||file.name,content:await file.text()});}if(!list.length)return;try{await post('/api/knowledge/import',{files:list});renderKnowledge();}catch(e){alert(e.message)}}
$('#mdFiles').onchange=e=>importMarkdown([...e.target.files]);$('#mdFolder').onchange=e=>importMarkdown([...e.target.files]);$('#zipPack').onchange=async e=>{const file=e.target.files[0];if(!file)return;try{const bytes=new Uint8Array(await file.arrayBuffer());let binary='';for(let i=0;i<bytes.length;i+=0x8000)binary+=String.fromCharCode(...bytes.subarray(i,i+0x8000));await post('/api/knowledge/import',{zip_base64:btoa(binary)});renderKnowledge();}catch(err){alert(err.message)}};

const fetchJsonWithTimeout=async(url,ms=4000)=>{
 const controller=new AbortController();
 const timer=setTimeout(()=>controller.abort(),ms);
 try{const r=await fetch(url,{signal:controller.signal});const j=await r.json();if(!r.ok)throw Error(`HTTP ${r.status}`);return j}
 finally{clearTimeout(timer)}
};
async function refreshStatus(){
 let s=null;
 try{s=await fetchJsonWithTimeout('/api/status');}
 catch{
  $('#backendState').textContent='● Backend unavailable';
  $('#backendState').classList.add('offline');
  $('#modelState').textContent='Model unavailable';
  $('#miniBackend').textContent='Unavailable';
  $('#miniModel').textContent='Status check failed';
  workspaceSummary={...(workspaceSummary||{}),model:{name:'Unavailable',backend:'Unavailable',context:'Unknown'}};
 }
 if(s){
  const connected=!!s.ollama;
  $('#backendState').textContent=connected?'● Local backend connected':'● Local backend offline';
  $('#backendState').classList.toggle('offline',!connected);
  $('#modelState').textContent=`Model: ${s.model_name||'llama3.2:3b'}`;
  $('#miniBackend').textContent=connected?'Local':'Offline';
  $('#miniModel').textContent=s.model_name||'llama3.2:3b';
  workspaceSummary={...(workspaceSummary||{}),model:{name:s.model_name||'llama3.2:3b',backend:connected?'LocalAI/Ollama':'Offline',context:s.context_capacity||'8K context'}};
 }
 try{
  const k=await fetchJsonWithTimeout('/api/knowledge');
  workspaceSummary={...(workspaceSummary||{}),knowledge:{...(k.center||{}),cards:Number(k.status?.total_cards||0)}};
 }catch{
  workspaceSummary={...(workspaceSummary||{}),knowledge:{documents:0,chunks:0,packs:[],cards:0}};
 }
}
$('#contextToggle').onclick=toggleContext;
$('#send').onclick=send;
$('#newChatSide').onclick=startNewChat;
$('#prompt').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});
$('#voice').onclick=()=>{const R=window.SpeechRecognition||window.webkitSpeechRecognition;if(!R)return alert('Voice input is unavailable here.');const r=new R();r.onresult=e=>$('#prompt').value=e.results[0][0].transcript;r.start()};
document.querySelectorAll('[data-page]').forEach(b=>b.onclick=()=>renderPage(b.dataset.page));
window.addEventListener('beforeunload',stopReading);
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopReading();});
$('#conversationSearch').oninput=refreshConversationHistory;
loadActiveProject();
refreshStatus();
refreshConversationHistory();
refreshContext();
renderPage('home');

// currently opened chat blank until the user sends a message.
