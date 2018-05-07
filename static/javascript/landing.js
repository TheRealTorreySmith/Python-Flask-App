// $('#anonymous-image').hide()

const ringPhone = () => {
  setTimeout(() => {$('#phone').addClass('shake-rotate')},1500)
  setTimeout(() => {$('#phone').removeClass('shake-rotate')},2000)
  setTimeout(() => {$('#phone').addClass('shake-rotate')},2500)
  setTimeout(() => {$('#phone').removeClass('shake-rotate')},3500)
}

const showAnonymousGuy = () => {
  setTimeout(() => {$('#anonymous-image').removeAttr('hidden')},3500)
}


$(document).ready(() => {
  ringPhone()
  showAnonymousGuy()

})
