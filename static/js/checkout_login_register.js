function changePasswordHideVisible(Id, e) {
  e.classList.toggle("fa-eye-slash"); 
  e.classList.toggle("fa-eye"); 
  let password = document.getElementById(Id);
  password.setAttribute("type", password.getAttribute("type") === "password" ? "text" : "password");
};

document.addEventListener('DOMContentLoaded', function () {
  const firstInput = document.querySelector('form input');
  if (firstInput) firstInput.focus();
});