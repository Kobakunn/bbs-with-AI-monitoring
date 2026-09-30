const screens=document.querySelectorAll(".screen");let currentUser=null,editingId=null,deletingId=null;
let posts=[
{id:1,userId:"kobayashi",name:"小林",content:"NLPを使った掲示板を作っています！",createdAt:"2026/09/28 11:30"},
{id:2,userId:"tanaka",name:"田中",content:"BERTについて勉強しています。",createdAt:"2026/09/28 11:35"},
{id:3,userId:"yamada",name:"山田",content:"FlaskでWebアプリを作ってみました！",createdAt:"2026/09/28 11:42"}];
const users=[{username:"kobayashi",password:"password",displayName:"小林"},{username:"tanaka",password:"password",displayName:"田中"}];

function show(name){screens.forEach(s=>s.classList.remove("active"));document.getElementById("screen-"+name).classList.add("active");window.scrollTo(0,0)}
function esc(v){return String(v).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;")}
function dateNow(){const d=new Date(),p=n=>String(n).padStart(2,"0");return `${d.getFullYear()}/${p(d.getMonth()+1)}/${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`}
function renderHeader(){document.getElementById("current-user").textContent=currentUser?currentUser.displayName+" さん":"";document.getElementById("logout-btn").style.display=currentUser?"block":"none"}
function renderPosts(){if(!currentUser)return show("login");document.getElementById("list-user").textContent=currentUser.displayName;document.getElementById("post-list").innerHTML=posts.map(p=>{const own=p.userId===currentUser.username;return `<article class="post-card"><div class="post-meta"><span class="post-name">名前：${esc(p.name)}</span><span class="post-date">投稿日時：${esc(p.createdAt)}</span></div><p class="post-content">${esc(p.content)}</p>${own?`<div class="post-actions"><button class="btn primary edit" data-id="${p.id}">修正</button><button class="btn danger delete" data-id="${p.id}">削除</button></div>`:`<div class="other">他ユーザーの投稿</div>`}</article>`}).join("")}

document.addEventListener("click",e=>{
 const b=e.target.closest("[data-screen]");if(b){e.preventDefault();const n=b.dataset.screen;if((n==="list"||n==="create")&&!currentUser)return show("login");if(n==="list")renderPosts();show(n)}
 const eb=e.target.closest(".edit");if(eb){editingId=+eb.dataset.id;const p=posts.find(x=>x.id===editingId);if(!p||p.userId!==currentUser.username)return alert("この投稿を修正する権限がありません。");document.getElementById("edit-name").value=p.name;document.getElementById("edit-content").value=p.content;document.getElementById("edit-count").textContent=p.content.length;show("edit")}
 const db=e.target.closest(".delete");if(db){deletingId=+db.dataset.id;const p=posts.find(x=>x.id===deletingId);if(!p||p.userId!==currentUser.username)return alert("この投稿を削除する権限がありません。");show("delete")}
});

document.getElementById("login-form").addEventListener("submit",e=>{e.preventDefault();const u=document.getElementById("login-username").value.trim(),pw=document.getElementById("login-password").value,found=users.find(x=>x.username===u&&x.password===pw);if(!found)return document.getElementById("login-error").textContent="ユーザー名またはパスワードが正しくありません。";currentUser=found;document.getElementById("login-error").textContent="";e.target.reset();document.getElementById("create-name").value=currentUser.displayName;renderHeader();renderPosts();show("list")});
document.getElementById("logout-btn").addEventListener("click",()=>{currentUser=null;renderHeader();show("login")});

document.getElementById("register-form").addEventListener("submit",e=>{e.preventDefault();const pw=document.getElementById("register-password").value,cf=document.getElementById("register-confirm").value;if(pw!==cf)return document.getElementById("register-error").textContent="パスワードが一致していません。";if(pw.length<8)return document.getElementById("register-error").textContent="パスワードは8文字以上で入力してください。";alert("ユーザー登録が完了しました。（モック）");e.target.reset();show("login")});

document.getElementById("create-form").addEventListener("submit",e=>{e.preventDefault();const name=document.getElementById("create-name").value.trim(),content=document.getElementById("create-content").value.trim();if(!name||!content)return;posts.unshift({id:Date.now(),userId:currentUser.username,name,content,createdAt:dateNow()});e.target.reset();document.getElementById("create-name").value=currentUser.displayName;document.getElementById("create-count").textContent="0";show("complete")});
document.getElementById("edit-form").addEventListener("submit",e=>{e.preventDefault();const p=posts.find(x=>x.id===editingId);if(!p||p.userId!==currentUser.username)return alert("この投稿を修正する権限がありません。");p.name=document.getElementById("edit-name").value.trim();p.content=document.getElementById("edit-content").value.trim();editingId=null;renderPosts();show("list")});
document.getElementById("confirm-delete").addEventListener("click",()=>{const p=posts.find(x=>x.id===deletingId);if(!p||p.userId!==currentUser.username)return alert("この投稿を削除する権限がありません。");posts=posts.filter(x=>x.id!==deletingId);deletingId=null;renderPosts();show("list")});
document.getElementById("create-content").addEventListener("input",e=>document.getElementById("create-count").textContent=e.target.value.length);
document.getElementById("edit-content").addEventListener("input",e=>document.getElementById("edit-count").textContent=e.target.value.length);
renderHeader();show("login");