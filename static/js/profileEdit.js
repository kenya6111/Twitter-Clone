window.addEventListener("load", function () {
  //ファイルアップロード時
  document.getElementById("file-upload-head-image").addEventListener('change', (e)=>{
      //画像がアップロードされている場合
      if(e.target.files.length > 0 ){
          document.getElementById("head-image").src =  URL.createObjectURL(e.target.files[0]);
      }
  })
  document.getElementById("file-upload-image").addEventListener('change', (e)=>{
      //画像がアップロードされている場合
      if(e.target.files.length > 0 ){
          document.getElementById("image").src =  URL.createObjectURL(e.target.files[0]);
      }
  })
});
