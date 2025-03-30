
const url = location.origin + "/like"

async function like(event,tweetId, redirectPath,loginUserId,parentTweetId){
  event.stopPropagation();
  event.preventDefault();
  const csrftoken = getCookie("csrftoken");

  const body = new URLSearchParams()
  body.append('tweet_id', tweetId)
  body.append('user_id', loginUserId)
  await fetch(url,{
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrftoken
    },
    body:body
  })
  .then((response) => response.json())
  .then((data) => {
    console.log(data)
    if(data.is_registered){
      if(redirectPath === 'profile'){
        window.location=location.origin+"/"+redirectPath+"?user_id="+loginUserId
      }else if(redirectPath === 'tweet_detail'){
        window.location=location.origin+"/"+redirectPath+"?tweet_id="+parentTweetId
      }else{
        window.location=location.origin+"/"+redirectPath
      }
    }else{

    }
  })
  .catch(error => {
    console.error(error);
  });
}


async function disLike(event,tweetId,redirectPath,loginUserId,parentTweetId){
  event.stopPropagation();
  event.preventDefault();
  const csrftoken = getCookie("csrftoken");

  const body = new URLSearchParams()
  body.append('tweet_id', tweetId)
  body.append('user_id', loginUserId)

  await fetch(url,{
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrftoken
    },
    body: body
  })
  .then((response) => response.json())
  .then((data) => {
    if(!data.is_registered){
      if(redirectPath === 'profile'){
        window.location=location.origin+"/"+redirectPath+"?user_id="+loginUserId
      }else if(redirectPath === 'tweet_detail'){
        window.location=location.origin+"/"+redirectPath+"?tweet_id="+parentTweetId
      }
      else{
        window.location=location.origin+"/"+redirectPath
      }
    }
  })
  .catch(error => {
    console.error(error);
  });
}


function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');