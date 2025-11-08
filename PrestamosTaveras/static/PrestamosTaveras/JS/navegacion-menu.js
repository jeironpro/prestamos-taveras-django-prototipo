const showMenu = (toggleId, navId) =>{
    const toggle = document.getElementById(toggleId),
          nav = document.getElementById(navId)
 
    toggle.addEventListener('click', () =>{
        // Add show-menu class to nav menu
        nav.classList.toggle('mostrar-menu')
 
        // Add show-icon to show and hide the menu icon
        toggle.classList.toggle('mostrar-icono')
    })
 }
 
 showMenu('navegacion-botones','navegacion-menu')