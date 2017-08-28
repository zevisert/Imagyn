
function validEmail(email) { // see:
  var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
  return re.test(email);
}

// get all data in form and return object
function getFormData() {
  var elements = document.getElementById("gform").elements; // all form elements
  var fields = Object.keys(elements).map(function(k) {
    if(elements[k].name !== undefined) {
      return elements[k].name;
    // special case for Edge's html collection
    }else if(elements[k].length > 0){
      return elements[k].item(0).name;
    }
  }).filter(function(item, pos, self) {
    return self.indexOf(item) == pos && item;
  });
  var data = {};
  fields.forEach(function(k){
    data[k] = elements[k].value;
    var str = ""; // declare empty string outside of loop to allow
                  // it to be appended to for each item in the loop
    if(elements[k].type === "checkbox"){ // special case for Edge's html collection
      str = str + elements[k].checked + ", "; // take the string and append
                                              // the current checked value to
                                              // the end of it, along with
                                              // a comma and a space
      data[k] = str.slice(0, -2); // remove the last comma and space
                                  // from the  string to make the output
                                  // prettier in the spreadsheet
    }else if(elements[k].length){
      for(var i = 0; i < elements[k].length; i++){
        if(elements[k].item(i).checked){
          str = str + elements[k].item(i).value + ", "; // same as above
          data[k] = str.slice(0, -2);
        }
      }
    }
  });
  return data;
}

function handleFormSubmit(token) {  // handles form submit without any jquery
  var data = getFormData();         // get the values submitted in the form
  var url = "https://script.google.com/macros/s/AKfycbx4ZZL1Rwvck6iyStArJdjtXiOm0jmoijcZJMH0_HcOkChggns/exec";

  var xhr = new XMLHttpRequest();
  xhr.open('POST', url);
  // xhr.withCredentials = true;
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onreadystatechange = function() {
    if (xhr.readyState == XMLHttpRequest.DONE) {
      if (JSON.parse(xhr.responseText).result == true){
        document.getElementById('gform').style.display = 'none'; // hide form
        document.getElementById('thankyou_message').style.display = 'block';
      } else {
        document.getElementById('recaptcha-failed').style.display = 'inline-block';
        grecaptcha.reset();
      }
    }

    return;
  };

  // url encode form data for sending as post data
  var encoded = Object.keys(data).map(function(k) {
    return encodeURIComponent(k) + '=' + encodeURIComponent(data[k])
  }).join('&')
  xhr.send(encoded);
}

function validate(event) {
  event.preventDefault();
  var data = getFormData(); // get the values submitted in the form

  if( !validEmail(data.Email) ) {   // if email is not valid show error
    document.getElementById('email-invalid').style.display = 'block';
  } else {
    document.getElementById('email-invalid').style.display = 'none';
    grecaptcha.execute(); // this will call handleFormSubmit as a callback
  }
}


function onload() {
  var element = document.getElementById('submit');
  element.onclick = validate;
}

document.addEventListener('DOMContentLoaded', onload, false);
