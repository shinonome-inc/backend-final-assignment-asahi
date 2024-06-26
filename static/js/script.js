const hearts = document.querySelectorAll('.heart');
hearts.forEach(heart => {
    heart.addEventListener('click', function() {
        this.classList.toggle('is-active');
      });

})

// CSRF対策
const getCookie = (name) => {
    if (document.cookie && document.cookie !== '') {
      for (const cookie of document.cookie.split(';')) {
          const [key, value] = cookie.trim().split('=')
          if (key === name) {
              return decodeURIComponent(value)
            }
        }
    }
  }
const csrftoken = getCookie('csrftoken')
const request =  {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'X-CSRFToken': csrftoken,
                            },
                }

const likeForms = document.querySelectorAll('.like-form');
likeForms.forEach(likeForm => {
    likeForm.addEventListener('submit', function(e) {
        e.preventDefault()
        const likeNumberElm = document.querySelector(`#like-number-${likeForm.id}`);
        const changeLikeNumber =  (data) => {
                likeNumberElm.textContent =  data.like_number  
        }
        //　ハート押下時に付与される"is-active"クラスで分岐
        if (likeForm.children[0].children[0].classList[1] == "is-active")
            fetch(`http://127.0.0.1:8000/tweets/${likeForm.id}/like/`, request
                ).then(response => {
                    return response.json()})
                .then(changeLikeNumber)
        else
            fetch(`http://127.0.0.1:8000/tweets/${likeForm.id}/unlike/`, request).then(response => {
                    return response.json()})
                .then(changeLikeNumber)
        
      });
})
