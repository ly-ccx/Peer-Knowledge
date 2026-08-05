const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const state={decision:false,permission:false,result:false,memory:false,patch:false,evidence:false};
const crumbs={home:'行动',tasks:'任务',cognition:'项目认知',automation:'自动化',skills:'Skills',task:'任务现场','computer-use':'Computer Use',result:'Result Package'};
const toast=$('#toast'),toastText=$('#toastText');
function notify(text){toastText.textContent=text;toast.classList.add('show');clearTimeout(window.__toast);window.__toast=setTimeout(()=>toast.classList.remove('show'),1900)}
function showView(name){$$('.page').forEach(p=>p.classList.toggle('active',p.dataset.page===name));$$('.nav').forEach(n=>n.classList.toggle('active',n.dataset.viewTarget===name));document.body.dataset.view=name;$('#pageCrumb').textContent=crumbs[name]||name;window.scrollTo(0,0)}
function actionCount(){const n=$$('.action-row:not(.resolved)').length;$('#homeCount').textContent=n;$('#actionCount').textContent=`${n} 个交接点`;$('#emptyInbox').classList.toggle('visible',n===0)}
function openCognitionTab(tab){showView('cognition');$$('[data-cognition-tab]').forEach(b=>b.classList.toggle('active',b.dataset.cognitionTab===tab));$$('[data-cognition-panel]').forEach(p=>p.classList.toggle('active',p.dataset.cognitionPanel===tab))}
$$('[data-view-target]').forEach(b=>b.addEventListener('click',()=>showView(b.dataset.viewTarget)));
$$('[data-open-task]').forEach(b=>b.addEventListener('click',()=>showView('task')));
$$('[data-open-result]').forEach(b=>b.addEventListener('click',()=>showView('result')));
$$('[data-open-automation]').forEach(b=>b.addEventListener('click',()=>showView('automation')));
$$('[data-cognition-tab]').forEach(b=>b.addEventListener('click',()=>openCognitionTab(b.dataset.cognitionTab)));
$$('[data-task-mode]').forEach(b=>b.addEventListener('click',()=>{$$('[data-task-mode]').forEach(x=>x.classList.toggle('active',x===b));$$('[data-task-panel]').forEach(p=>p.classList.toggle('active',p.dataset.taskPanel===b.dataset.taskMode))}));
$$('[data-workbench-tab]').forEach(b=>b.addEventListener('click',()=>{$$('[data-workbench-tab]').forEach(x=>x.classList.toggle('active',x===b));$$('[data-workbench-pane]').forEach(p=>p.classList.toggle('active',p.dataset.workbenchPane===b.dataset.workbenchTab));$('#workbenchTitle').textContent={plan:'GoalPlan',browser:'Browser Session',files:'Workspace Files',documents:'Documents'}[b.dataset.workbenchTab]}));
$$('[data-filter-group="tasks"] [data-filter]').forEach(b=>b.addEventListener('click',()=>{const f=b.dataset.filter;$$('[data-filter-group="tasks"] [data-filter]').forEach(x=>x.classList.toggle('active',x===b));$$('.task-row').forEach(r=>r.hidden=f!=='all'&&r.dataset.status!==f)}));
$('#taskSearch').addEventListener('input',e=>{const q=e.target.value.toLowerCase();$$('.task-row').forEach(r=>r.hidden=q&&!r.textContent.toLowerCase().includes(q))});
$('#approveDecision').addEventListener('click',()=>{state.decision=true;$('[data-action="decision"]').classList.add('resolved');$('#decisionStatus').textContent='已批准 · Peer 继续执行';actionCount();notify('决策已批准，行动权交回 Peer')});
$('#grantPermission').addEventListener('click',()=>{state.permission=true;$('[data-action="permission"]').classList.add('resolved');$('#runCount').textContent='2';actionCount();notify('已从 Checkpoint #24 安全恢复')});
$('#acceptResult').addEventListener('click',()=>{state.result=true;$('[data-action="review"]').classList.add('resolved');$('#resultMemoryState').textContent='已提交审查';$('#resultSkillState').textContent='已提交审查';$('#memoryCount').textContent='3';$('#patchCount').textContent='2';actionCount();notify('结果已接受，学习候选已提交审查');setTimeout(()=>openCognitionTab('changes'),650)});
$('#acceptCognition').addEventListener('click',e=>{state.memory=true;e.currentTarget.textContent='已接受';e.currentTarget.disabled=true;$('#memoryBadge').textContent='13';notify('认知变更已确认并保留来源')});
$('#approvePatch').addEventListener('click',e=>{state.patch=true;e.currentTarget.textContent='灰度中 · 10%';e.currentTarget.disabled=true;$('#patchCount').textContent='0';notify('Skill Patch 已进入 10% 灰度，可随时回滚')});
$('#reviewMemory').addEventListener('click',()=>openCognitionTab('changes'));
function openComputer(){showView('computer-use')}
$('#openComputerUse').addEventListener('click',openComputer);$('#browserComputerUse').addEventListener('click',openComputer);
$('#completeComputerUse').addEventListener('click',e=>{state.evidence=true;e.currentTarget.textContent='✓ Evidence 已生成';e.currentTarget.disabled=true;notify('断言通过，截图与 DOM Evidence 已保存')});
$('#newTask').addEventListener('click',()=>notify('打开新任务委托 Composer'));
actionCount();window.peer3={state,showView,openCognitionTab};
