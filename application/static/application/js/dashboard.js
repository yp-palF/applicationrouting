function hamburgerClick() {
    document.getElementById("sidebar").style.transitionDuration = "0.4s"; 
    if(document.getElementById("sidebar").style.width == "221px"){
        document.getElementById("main").style.transitionDuration = "0.4s";  
        document.getElementById("sidebar").style.width = "50px";
        document.getElementById("main").style.marginLeft = "50px";
        document.getElementById("sideLinks").style.display = "none";    
        document.getElementById("main").style.backgroundColor = "#F0F690";  
    } 
    else{
        document.getElementById("main").style.transitionDuration = "1s"; 
        document.getElementById("sidebar").style.width = "221px";
        document.getElementById("main").style.marginLeft = "120px";  
        document.getElementById("sideLinks").style.display = "block";   
        document.getElementById("main").style.backgroundColor = "rgba(0,0,0,0.3)";

    }
}
function newApp() {
    document.getElementById("sideLinks").action="/createApplication";
    document.getElementById("sideLinks").submit()
}
function allApplication() {
    document.getElementById("sideLinks").action="/allapplication";
    document.getElementById("sideLinks").submit()
}
function dashboard() {
    document.getElementById("sideLinks").action="/dashboard";
    document.getElementById("sideLinks").submit()
}
function myFunction() {
    document.getElementById("myDropdown").classList.toggle("show");
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('#sidebar') && !event.target.matches('#hamburger')) {
        document.getElementById("main").style.transitionDuration = "0.4s";  
        document.getElementById("sidebar").style.width = "50px";
        document.getElementById("main").style.marginLeft = "50px";
        document.getElementById("sideLinks").style.display = "none";    
        document.getElementById("main").style.backgroundColor = "#F0F690"; 
    }
    if (!event.target.matches('.dropbtn')) {
        document.getElementById("myDropdown").classList.remove("show");
    }
}