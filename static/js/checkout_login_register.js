function changePasswordHideVisible(Id, e) {
  e.classList.toggle("fa-eye-slash"); 
  e.classList.toggle("fa-eye"); 
  let password = document.getElementById(Id);
  password.setAttribute("type", password.getAttribute("type") === "password" ? "text" : "password");
};

// Permet de se concentrer automatiquement sur le champ email à l'ouverture de la page
document.addEventListener('DOMContentLoaded', () => {
    const emailInput = document.getElementById('email');
    if (emailInput) {
    emailInput.focus();
    }
  }
);