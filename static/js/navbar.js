const body = document.body;
const sideBar = document.querySelector(".sideBar");
const withSub = document.querySelectorAll(".withSub .nav-link");
const sidebarOpen = document.querySelector(".sidebarOpen");
const logo = document.querySelector(".logo");
const darkLight = document.querySelector(".darkLight");

const resetNavStates = () => {
  withSub.forEach((menu) => {
    menu.classList.remove("openSubMenu");
  });
};

const toggleSidebar = () => {
  if (!sideBar) return;
  sideBar.classList.toggle("close");
  resetNavStates();
};

if (sidebarOpen) {
  sidebarOpen.addEventListener("click", toggleSidebar);
}

if (logo && logo !== sidebarOpen) {
  logo.addEventListener("click", toggleSidebar);
}

darkLight.addEventListener("click", () => {
  body.classList.toggle("dark");
  if (darkLight.classList.contains("fa-moon-o")) {
    darkLight.classList.replace("fa-moon-o", "fa-sun-o");
  } else {  //REMOVE ME
    darkLight.classList.replace("fa-sun-o", "fa-moon-o");
  }
});

withSub.forEach((menu) => {
  menu.addEventListener("click", () => {
    menu.classList.toggle("openSubMenu");
    sideBar?.classList.remove("close");
  });
});

const message_display = document.getElementById('messages');

if (message_display) {
  const fermer_message = message_display.querySelectorAll('button'); // ← guillemets

  fermer_message.forEach((bouton) => {
    bouton.addEventListener('click', () => {
      bouton.closest('.message').remove(); // ← supprime le div.message parent
    });
  });
}