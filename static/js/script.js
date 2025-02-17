async function traducir() {
    let texto = document.getElementById("texto").value;
    if (!texto) {
        alert("Por favor, ingresa un texto.");
        return;
    }

    let respuesta = await fetch("/traducir", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto: texto })
    });

    let datos = await respuesta.json();
    console.log("Respuesta de la API:", datos);  // Depuración

    if (datos.error) {
        document.getElementById("resultado").innerHTML = `<p style="color: red;"><strong>Error:</strong> ${datos.error}</p>`;
    } else {
        document.getElementById("resultado").innerHTML = `
            <p><strong>Hiragana:</strong> ${datos.hiragana}</p>
            <p><strong>Romanji:</strong> ${datos.romanji}</p>
            <p><strong>Traducción:</strong> ${datos.traduccion}</p>
            <p><strong>Pronunciación:</strong> ${datos.pronunciacion}</p>
        `;

        // Reproducir el audio
        const audioPlayer = document.getElementById("audioPlayer");
        const audioSource = document.getElementById("audioSource");

        if (datos.audio_url) {
            audioSource.src = datos.audio_url;
            audioPlayer.load();
            audioPlayer.style.display = "block";
            audioPlayer.play().catch(error => {
                console.error("Error al reproducir el audio:", error);
                document.getElementById("resultado").innerHTML += `<p style="color: red;">El archivo de audio ha expirado. Por favor, realiza una nueva búsqueda.</p>`;
            });
        } else {
            audioPlayer.style.display = "none";
        }
    }
}