// DEFAULT HIDES THE SUBMIT BUTTON
$('#send-text-button').hide()
$('#make-call-button').hide()

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

const clickMessageButton = (event) => {
  event.preventDefault()
  $('.submit-button-spacer').hide()
  $('#send-text-button').show()
  $('#make-call-button').hide()
  $('.phone-select-button').css('color', '#0069d9')
  $('.phone-select-button').css('background-color', '')
  $('.message-select-button').css('color', 'white')
  $('.message-select-button').css('background-color', '#28a745')
  $('.call-check').prop('checked', false)
  $('.text-check').prop('checked', true)
  setTimeout(() => {$('.close').trigger('click')},1500)
}

const clickPhoneButton = (event) => {
  event.preventDefault()
  $('#make-call-button').show()
  $('#send-text-button').hide()
  $('.phone-select-button').css('color', 'white')
  $('.phone-select-button').css('background-color', '#0069d9')
  $('.message-select-button').css('color', '#28a745')
  $('.message-select-button').css('background-color', '')
  $('.call-check').prop('checked', true)
  $('.text-check').prop('checked', false)
  setTimeout(() => {$('.close').trigger('click')},1500)
}

// DOCUMENT READY
$(document).ready(() => {
  $('.clear-fields').click(clearFields)
  $('.logout-button').click(clearFields)
  $('.message-select-button').click(clickMessageButton)
  $('.phone-select-button').click(clickPhoneButton)
})
