const clearFields = () => {
  $('#voiceMessageInput').val('')
  $('#phoneNumberInput').val('')
}



$(document).ready(() => {
  $('.clear-fields').click(clearFields)
})
