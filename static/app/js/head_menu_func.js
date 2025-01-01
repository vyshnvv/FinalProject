//Ham-menu 
const btn_ham = document.querySelector("#btn_ham");
const header = document.querySelector(".header")
const overlay = document.querySelector(".overlay")
const fadeElems = document.querySelectorAll(".has-fade");


btn_ham.addEventListener("click", function () {
    
    if (header.classList.contains("open")) { //Close ham menu
        header.classList.remove("open");
        fadeElems.forEach(function (element) {
            element.classList.remove("fade-in")
            element.classList.add("fade-out")
            overlay.classList.remove("fade-in")
            overlay.classList.add("fade-out")
        });

    }
    else { //Open ham menu
        header.classList.add("open");
        fadeElems.forEach(function (element) {
            element.classList.remove("fade-out")
            element.classList.add("fade-in")
        });

    }
});