const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const toast=$('#toast'), toastText=$('#toastText');
let detailOrigin='tasks';
function notify(text){toastText.textContent=text;toast.classList.add('show');clearTimeout(window.__toast);window.__toast=setTimeout(()=>toast.classList.remove('show'),1800)}
function showView(name){
  $$('.view').forEach(v=>v.classList.toggle('active',v.dataset.view===name));
  $$('.nav[data-view]').forEach(n=>n.classList.toggle('active',n.dataset.view===name));
  document.body.dataset.state=name;
  window.scrollTo(0,0);
}
function openTask(origin){detailOrigin=origin||document.body.dataset.state||'tasks';showView('canvas');setTimeout(()=>$('.n-decision')?.classList.add('focus'),80)}
function openReview(origin){detailOrigin=origin||document.body.dataset.state||'history';showView('review')}
function bindWorkbench(root){
  $$('.wb-tabs button[data-pane]',root).forEach(button=>button.addEventListener('click',()=>{
    const pane=button.dataset.pane;
    $$('.wb-tabs button[data-pane]',root).forEach(item=>item.classList.toggle('active',item===button));
    $$('.wb-pane[data-pane]',root).forEach(item=>item.classList.toggle('active',item.dataset.pane===pane));
  }));
}
function bindFilters(group){
  const container=$(`[data-filter-group="${group}"]`);
  if(!container)return;
  const view=container.closest('.view');
  const records=$$('[data-status]',view);
  $$('button[data-filter]',container).forEach(button=>button.addEventListener('click',()=>{
    const filter=button.dataset.filter;
    $$('button[data-filter]',container).forEach(item=>item.classList.toggle('active',item===button));
    records.forEach(record=>record.hidden=filter!=='all'&&record.dataset.status!==filter);
  }));
}

document.querySelectorAll('button.nav[data-view], button.text-action[data-view]').forEach(button=>button.addEventListener('click',event=>{event.stopPropagation();showView(button.dataset.view)}));
$$('[data-open-task]').forEach(element=>element.addEventListener('click',()=>openTask(document.body.dataset.state)));
$$('[data-review-result]').forEach(element=>element.addEventListener('click',()=>openReview(document.body.dataset.state)));
$$('.detail-back').forEach(button=>button.addEventListener('click',()=>showView(button.dataset.back||detailOrigin)));
$$('[data-workbench]').forEach(bindWorkbench);
bindFilters('tasks');bindFilters('history');

$('#approveDecision')?.addEventListener('click',()=>{notify('决策已批准 · 行动权交给 Peer');$('.n-decision')?.classList.remove('focus');$('.n-evidence')?.classList.add('focus')});
$('#acceptResult')?.addEventListener('click',()=>{notify('结果已验收 · 本轮任务进入历史');setTimeout(()=>showView('history'),550)});
$('#continueTask')?.addEventListener('click',()=>{showView('canvas');notify('已回到同一任务现场，可继续提出修订')});
$$('[data-continue-history]').forEach(button=>button.addEventListener('click',event=>{event.stopPropagation();openTask('history');notify('已在同一任务中创建新的 Run')}));
$('#newTask')?.addEventListener('click',()=>notify('新任务将从 Conversation 中建立 Goal Contract'));
$$('.workspace').forEach(workspace=>workspace.addEventListener('click',()=>{$$('.workspace').forEach(item=>item.classList.remove('active'));workspace.classList.add('active');notify(`切换到 ${workspace.dataset.workspace} Workspace`)}));
$$('.search-box input').forEach(input=>input.addEventListener('input',()=>{const query=input.value.trim().toLowerCase();const view=input.closest('.view');$$('[data-status]',view).forEach(record=>record.hidden=query&&!record.textContent.toLowerCase().includes(query))}));
window.peerPrototype={showView,openTask,openReview};
