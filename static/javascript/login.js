
const timedHideAlert = () => {
// setTimeout(() => $('.alert').hide(),1500)
setTimeout(() => $('.alert').addClass('fadeOut'),1600)
}

$(document).ready(() => {
  timedHideAlert()

})
