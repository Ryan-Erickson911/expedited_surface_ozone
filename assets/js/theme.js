const lightTheme = "assets/css/light.css";
const darkTheme = "assets/css/dark.css";
const mainTheme = "assets/css/main.css";
const sunIcon = "assets/imgs/svgs/SunIcon.svg";
const moonIcon = "assets/imgs/svgs/MoonIcon.svg";
const cloudIcon = "assets/imgs/svgs/mesign.webp";
const gitL = "assets/imgs/svgs/GitHubLight.webp";
const gitD = "assets/imgs/svgs/GitHubDark.webp";
const themeIcon = document.getElementById("doc-icon");
const gitIcon = document.getElementById("gitIcon");
let movement = 1;

function changeTheme() {
  const theme = document.getElementById("doc-theme");
  if (theme.getAttribute("href") === mainTheme) {
    theme.setAttribute("href", lightTheme);
    themeIcon.setAttribute("src", sunIcon);
    gitIcon.setAttribute("src", gitD);
  } else if (theme.getAttribute("href") === lightTheme) {
    theme.setAttribute("href", darkTheme);
    themeIcon.setAttribute("src", moonIcon);
    gitIcon.setAttribute("src", gitL);
  } else {
    theme.setAttribute("href", mainTheme);
    themeIcon.setAttribute("src", cloudIcon);
    gitIcon.setAttribute("src", gitL);
  }
}