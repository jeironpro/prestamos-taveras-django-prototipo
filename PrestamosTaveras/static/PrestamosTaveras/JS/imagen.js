const file = document.getElementById('cedula');

file.addEventListener('change', (e) => {
    if (e.target.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            file.style.backgroundImage = `url(${e.target.result})`;
            file.style.backgroundSize = '440px 300px';
            file.style.backgroundPosition = 'center';
            file.style.backgroundRepeat = 'no-repeat';
            
        };
        reader.readAsDataURL(e.target.files[0]);
    } else {
        file.style.backgroundImage = 'none';
    }
})