var myInput = document.getElementById("password");
var letter = document.getElementById("letter");
var capital = document.getElementById("capital");
var number = document.getElementById("number");
var length = document.getElementById("length");
var myInput2 = document.getElementById("confirm");
var match = document.getElementById("match");

myInput.onfocus = myInput2.onfocus = () => {
  document.getElementById("requirement-password-rule").style.display = "block";
}

myInput2.onfocus = () =>{
    document.getElementById("requirement-password-rule").style.display = "block";
}

myInput.onblur = () => {
  document.getElementById("requirement-password-rule").style.display = "none";
}

myInput2.onblur = () => {
  document.getElementById("requirement-password-rule").style.display = "none";
}

myInput.onkeyup = () => {
  // Validate lowercase letters
  var lowerCaseLetters = /[a-z]/g;
  if(myInput.value.match(lowerCaseLetters)) {
    letter.classList.remove("invalid");
    letter.classList.add("valid");
  } else {
    letter.classList.remove("valid");
    letter.classList.add("invalid");
  }

  // Validate capital letters
  var upperCaseLetters = /[A-Z]/g;
  if(myInput.value.match(upperCaseLetters)) {
    capital.classList.remove("invalid");
    capital.classList.add("valid");
  } else {
    capital.classList.remove("valid");
    capital.classList.add("invalid");
  }

  // Validate numbers
  var numbers = /[0-9]/g;
  if(myInput.value.match(numbers)) {
    number.classList.remove("invalid");
    number.classList.add("valid");
  } else {
    number.classList.remove("valid");
    number.classList.add("invalid");
  }

  // Validate length
  if(myInput.value.length >= 8) {
    length.classList.remove("invalid");
    length.classList.add("valid");
  } else {
    length.classList.remove("valid");
    length.classList.add("invalid");
  }
}

myInput2.onkeyup = () => {
   if(myInput.value == myInput2.value){
    match.classList.remove("invalid");
    match.classList.add("valid");
   }
   else{
   match.classList.remove("valid");
   match.classList.add("invalid");
   }
}