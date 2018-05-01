
const hideAlert = () => {
  $('.alert').hide()
}

$(document).ready(() => {
  $('#inputUsername').click(hideAlert)
  $('#inputPassword').click(hideAlert)
})
