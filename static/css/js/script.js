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
    }
}
