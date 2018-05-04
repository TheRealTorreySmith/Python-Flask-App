// HIDES THE SEND TEXT MESSAGE BUTTON
$('#send-text-button').hide()

// CLEARS INPUT FIELDS ON DASHBOARD
const clearFields = () => {
  $('#voiceMessageInput').val('')
  $('#phoneNumberInput').val('')
}

// INPUTS NUMBERS ON IPHONE BUTTON CLICKS
$('.num').click(function () {
  let num = $(this)
  let text = $.trim(num.find('.txt').clone().children().remove().end().text())
  let telNumber = $('#phoneNumberInput')
  if ($(telNumber).val().length < 10) {
    $(telNumber).val(telNumber.val() + text)
  }
})

const clickMessageButton = () => {
  $('#send-text-button').show()
  $('#make-call-button').hide()
  $('.phone-select-button').css('color', '#0069d9')
  $('.phone-select-button').css('background-color', '')
  $('.message-select-button').css('color', 'white')
  $('.message-select-button').css('background-color', '#28a745')
}

const clickPhoneButton = () => {
  $('#make-call-button').show()
  $('#send-text-button').hide()
  $('.phone-select-button').css('color', 'white')
  $('.phone-select-button').css('background-color', '#0069d9')
  $('.message-select-button').css('color', '#28a745')
  $('.message-select-button').css('background-color', '')
}

// DOCUMENT READY
$(document).ready(() => {

  $('.clear-fields').click(clearFields)
  $('.message-select-button').click(clickMessageButton)
  $('.phone-select-button').click(clickPhoneButton)
})
