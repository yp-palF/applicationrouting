function hamburgerClick() {
    if(document.getElementById("sidebar").style.width == "250px"){
        document.getElementById("sidebar").style.width = "50px";
        document.getElementById("main").style.marginLeft = "50px";
        document.getElementById("sideLinks").style.display = "none";    
        document.getElementById("main").style.backgroundColor = "#F0F690";    
    } 
    else{
        document.getElementById("sidebar").style.width = "250px";
        document.getElementById("main").style.marginLeft = "250px";  
        document.getElementById("sideLinks").style.display = "block";   
        document.getElementById("main").style.backgroundColor = "rgba(0,0,0,0.3)";
    }
}
window.onclick = function(event) {
    if (!event.target.matches('#sidebar') && !event.target.matches('#hamburger')) {
        document.getElementById("sidebar").style.width = "50px";
        document.getElementById("main").style.marginLeft = "50px";
        document.getElementById("sideLinks").style.display = "none";    
        document.getElementById("main").style.backgroundColor = "#F0F690"; 
    }
} 