
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
const retweetUrl = location.origin + "/retweet"

async function retweet(event,tweetId, redirectPath,loginUserId,parentTweetId){
  event.stopPropagation();
  event.preventDefault();
  const csrftoken = getCookie("csrftoken");

  const body = new URLSearchParams()
  body.append('tweet_id', tweetId)
  body.append('user_id', loginUserId)
  await fetch(retweetUrl,{
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


async function disRetweet(event,tweetId,redirectPath,loginUserId,originTweetId,parentTweetId){
  event.stopPropagation();
  event.preventDefault();
  const csrftoken = getCookie("csrftoken");

  const body = new URLSearchParams()
  body.append('tweet_id', tweetId)
  body.append('origin_tweet_id', originTweetId)
  body.append('user_id', loginUserId)

  await fetch(retweetUrl,{
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

const followUrl = location.origin + "/follow"

async function followUnfollow (loginuserId,TweetUserId,is_follow){
  event.stopPropagation();
  event.preventDefault();
  const csrftoken = getCookie("csrftoken");

  const body = new URLSearchParams()
  body.append('login_user_id', loginuserId)
  body.append('tweet_user_id', TweetUserId)
  body.append('is_follow', is_follow)

  await fetch(followUrl,{
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrftoken
    },
    body: body
  })
  .then((response) => response.json())
  .then((data) => {
    window.location=location.origin+"/main"
  })
  .catch(error => {
    console.error(error);
  });

}


const bookmarkUrl = location.origin + "/bookmark"

async function bookmark (tweetId,loginUserId){
  event.stopPropagation();
  event.preventDefault();
  const csrftoken = getCookie("csrftoken");

  const body = new URLSearchParams()
  body.append('tweet_id', tweetId)
  body.append('user_id', loginUserId)

  await fetch(bookmarkUrl,{
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrftoken
    },
    body: body
  })
  .then((response) => response.json())
  .then((data) => {
    window.location=location.origin+"/main"
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