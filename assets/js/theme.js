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
const msidew = document.getElementById("mainSidebar");
const toplogos = document.getElementById("logosandhome");
const menuicon = document.getElementById("motionbutton");
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


const contactheader = document.getElementById("contactheader");
function hideheaders() {
  var calcspace = document.body.offsetHeight - window.pageYOffset - document.getElementById("footer").offsetHeight - 153
  let elms = document.querySelectorAll('[id="scrollheader"]');
  if ((window.innerHeight + window.pageYOffset) >= document.body.offsetHeight+102-document.getElementById("footer").offsetHeight) {
    contactheader.style.display = "block";
    contactheader.style.height = calcspace+"px";
    for(var i = 0; i < elms.length; i++)   
      elms[i].style.top = "-100px";
  } else if ((window.innerHeight + window.pageYOffset) >= document.body.offsetHeight-3) {    
    contactheader.style.display = "block";
    contactheader.style.height = calcspace+"px";
    for(var i = 0; i < elms.length; i++)   
      elms[i].style.top = "-100px";
  } else {
    contactheader.style.display = "none";
    contactheader.style.height = "0px";
    for(var i = 0; i < elms.length; i++)   
      elms[i].style.top = "102px";
  }

}

window.addEventListener("resize", checkmargins);
window.addEventListener("scroll", checkmargins);
window.addEventListener("resize", hideheaders);
window.addEventListener("scroll", hideheaders);
menuicon.onclick=NavControl;