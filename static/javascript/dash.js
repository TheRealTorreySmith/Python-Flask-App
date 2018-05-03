const clearFields = () => {
  $('#voiceMessageInput').val('')
  $('#phoneNumberInput').val('')
}




$(document).ready(() => {
  $('.clear-fields').click(clearFields)

  $('.num').click(function () {
    let num = $(this)
    let text = $.trim(num.find('.txt').clone().children().remove().end().text())
    let telNumber = $('#phoneNumberInput')
    if ($(telNumber).val().length < 10) {
      $(telNumber).val(telNumber.val() + text)
    }
  })

  
})
