  function moveToProfile(relativeUrl,event){
    event.preventDefault();
    const absoluteUrl = new URL(relativeUrl, window.location.origin);
    window.location.href = absoluteUrl.href;
  }

  // モーダル要素を取得
var modal = document.getElementById("myModal");
var btn = document.getElementById("openModal");
var span = document.getElementById("closeModal");
// btn.onclick = function(event) {
//   event.stopPropagation()
//   modal.style.display = "block"; // モーダルのdisplayスタイルを"block"にして表示
// }
btn.addEventListener('click',(event)=>{
  event.stopPropagation()
  event.preventDefault()
  modal.style.display = "block"; // モーダルのdisplayスタイルを"block"にして表示
})

span.addEventListener ('click',(event)=>{
  event.stopPropagation()
  event.preventDefault()
  modal.style.display = "none"; // モーダルのdisplayスタイルを"none"にして非表示
})

window.onclick = function(event) {
  // クリックされた箇所がモーダル自体（外側）であれば
  if (event.target == modal) {
      modal.style.display = "none"; // モーダルのdisplayスタイルを"none"にして非表示
  }
}