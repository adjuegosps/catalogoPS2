import os
import re
import unicodedata

# 1. Definimos la parte de arriba del HTML
html_inicio = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo PS2 - Modern Retro con Portadas</title>
    
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">

    <style>
        :root {
            --bg-color: #0d0e15;
            --bg-card: rgba(255, 255, 255, 0.03);
            --text-main: #e0e6ed;
            --text-muted: #8b9eb7;
            --ps2-blue: #003791;
            --neon-blue: #00d2ff;
        }

        body {
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(0, 55, 145, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 85% 30%, rgba(157, 0, 255, 0.08) 0%, transparent 50%);
            color: var(--text-main);
            font-family: 'Rajdhani', sans-serif;
            margin: 0;
            padding: 40px 20px;
            min-height: 100vh;
        }

        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background: var(--bg-color); }
        ::-webkit-scrollbar-thumb { background: #2a3441; border-radius: 5px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--neon-blue); }

        h1 {
            text-align: center;
            color: #ffffff;
            font-size: 3.5em;
            font-weight: 700;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 4px;
            text-shadow: 0 0 15px var(--ps2-blue), 0 0 30px var(--neon-blue);
        }

        .subtitulo {
            text-align: center;
            color: var(--text-muted);
            font-size: 1.2em;
            margin-bottom: 40px;
            letter-spacing: 1px;
        }

        .contenedor-buscador {
            text-align: center;
            margin-bottom: 50px;
            position: relative;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }

        #buscador {
            width: 100%;
            padding: 15px 25px;
            font-size: 18px;
            font-family: 'Rajdhani', sans-serif;
            background-color: rgba(0, 0, 0, 0.5);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 30px;
            outline: none;
            box-sizing: border-box;
            transition: all 0.4s ease;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        }

        #buscador:focus {
            border-color: var(--neon-blue);
            background-color: rgba(0, 0, 0, 0.8);
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.3);
            transform: scale(1.02);
        }

        /* === AJUSTES DE GRID PARA 7 TARJETAS POR LÍNEA === */
        .lista-juegos {
            list-style-type: none;
            padding: 0;
            margin: 0 auto;
            /* Quitamos el max-width para que aproveche todo el ancho del monitor */
            width: 95%; 
            display: grid;
            /* Reducimos el ancho mínimo de la tarjeta a 150px para que entren 7 en monitores estándar (1080p) */
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            /* Reducimos el espacio entre tarjetas */
            gap: 15px;
        }

        .lista-juegos li {
            background-color: var(--bg-card);
            border-radius: 8px; /* Bordes un poco menos redondeados al ser más chicas */
            border: 1px solid rgba(255,255,255,0.05);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            cursor: pointer;
        }

        .portada {
            width: 100%;
            aspect-ratio: 215 / 300; /* Coincide exactamente con la proporción de tus imágenes */
            object-fit: cover;
            border-bottom: 2px solid rgba(255, 255, 255, 0.05);
            transition: transform 0.4s ease, filter 0.4s ease;
        }

        .titulo-juego {
            /* Achicamos padding y tamaño de fuente para que encaje mejor en tarjetas más pequeñas */
            padding: 10px 8px;
            text-align: center;
            font-size: 14px; 
            font-weight: 600;
            letter-spacing: 0.5px;
            min-height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            /* Esto evita que nombres larguísimos rompan la tarjeta, añadiendo puntos suspensivos si es necesario,
               aunque con flex a veces es mejor dejar que el texto haga varias líneas. Dejamos que haga múltiples líneas por ahora. */
        }

        .lista-juegos li:hover {
            transform: translateY(-5px); /* Elevación un poco más sutil */
            background-color: #121620;
            border-color: var(--neon-blue);
            box-shadow: 
                0 8px 15px rgba(0, 0, 0, 0.5),
                0 0 10px rgba(0, 210, 255, 0.2);
        }

        .lista-juegos li:hover .portada {
            transform: scale(1.05);
            filter: brightness(1.1);
        }

        .lista-juegos li:hover .titulo-juego {
            color: var(--neon-blue);
            text-shadow: 0 0 8px rgba(0, 210, 255, 0.5);
        }

        /* Ajustes para móviles/tablets */
        @media (max-width: 1200px) {
            .lista-juegos { grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); }
        }
        @media (max-width: 768px) {
            h1 { font-size: 2.5em; }
            .lista-juegos { grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); }
            .titulo-juego { font-size: 12px; }
        }
    </style>
</head>
<body>

    <h1>PlayStation 2</h1>
    <div class="subtitulo">Catálogo Oficial de Juegos</div>
    
    <div class="contenedor-buscador">
        <input type="text" id="buscador" onkeyup="filtrarJuegos()" placeholder="Buscar un juego...">
    </div>

    <ul id="lista" class="lista-juegos">
"""

# 2. Script de búsqueda del HTML (Mejorado para compatibilidad con símbolos raros)
html_fin = r"""    </ul>

    <script>
        function normalizarTexto(texto) {
            // 1. Quitar acentos
            let n = texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
            // 2. Eliminar puntos y apóstrofes (ej: G.U. -> gu)
            n = n.replace(/[.']/g, "");
            // 3. Reemplazar cualquier símbolo que NO sea letra o número por espacios (ej: 1//Rebirth -> 1 rebirth)
            n = n.replace(/[^a-z0-9]/g, " ");
            // 4. Limpiar espacios múltiples y bordes
            return n.replace(/\s+/g, " ").trim();
        }

        function filtrarJuegos() {
            var input, filter, ul, li, i, txtValue;
            input = document.getElementById('buscador');
            filter = normalizarTexto(input.value); 
            ul = document.getElementById('lista');
            li = ul.getElementsByTagName('li');

            requestAnimationFrame(() => {
                for (i = 0; i < li.length; i++) {
                    var titulo = li[i].querySelector('.titulo-juego');
                    if (titulo) {
                        txtValue = normalizarTexto(titulo.textContent || titulo.innerText);
                        if (txtValue.indexOf(filter) > -1) {
                            li[i].style.display = "flex"; 
                        } else {
                            li[i].style.display = "none";
                        }
                    }
                }
            });
        }
    </script>
</body>
</html>
"""

# Limpieza general de strings (¡AQUÍ ESTÁ LA MAGIA PARA .hack//G.U.!)
def normalizar_nombre(nombre):
    n = nombre.lower()
    
    # 1. Quitamos los acentos (á -> a)
    n = ''.join(c for c in unicodedata.normalize('NFD', n) if unicodedata.category(c) != 'Mn')
    
    # 2. Borramos puntos y apóstrofes (para que g.u. sea gu, .hack sea hack, don't sea dont)
    n = n.replace('.', '').replace("'", "").replace("’", "")
    
    # 3. Todo lo que NO sea letra o número, lo cambiamos por ESPACIOS (para que 1//Rebirth sea 1 rebirth)
    n = re.sub(r'[^a-z0-9]', ' ', n)
    
    # 4. Limpiamos espacios dobles (ej: "hack  gu" -> "hack gu")
    n = ' '.join(n.split())
    
    return n

# Función de Matching
def encontrar_mejor_imagen(juego_norm, mapa_imagenes):
    # 1. Match Exacto
    if juego_norm in mapa_imagenes:
        return mapa_imagenes[juego_norm]

    mejor_imagen = "no_existe.jpg" 
    mejor_score = 0.0

    for img_norm, archivo_real in mapa_imagenes.items():
        # Agregamos espacios para buscar palabras enteras
        juego_espacios = f" {juego_norm} "
        img_espacios = f" {img_norm} "
        
        # 2. Match de Substring
        if img_espacios in juego_espacios or juego_espacios in img_espacios:
            l_min = min(len(img_norm), len(juego_norm))
            l_max = max(len(img_norm), len(juego_norm))
            score = 0.85 + (0.15 * (l_min / l_max)) 
            
            if score > mejor_score:
                mejor_score = score
                mejor_imagen = archivo_real
        else:
            # 3. Match de Palabras
            j_palabras = set(juego_norm.split())
            i_palabras = set(img_norm.split())
            
            if j_palabras and i_palabras:
                interseccion = j_palabras.intersection(i_palabras)
                if interseccion:
                    score_palabras = len(interseccion) / max(len(j_palabras), len(i_palabras))
                    
                    if score_palabras > mejor_score and score_palabras >= 0.60:
                        mejor_score = score_palabras
                        mejor_imagen = archivo_real

    return mejor_imagen

print("Iniciando el proceso de generación del catálogo...")

if not os.path.exists("covers"):
    os.makedirs("covers")
    print("Se creó la carpeta 'covers'. Coloca tus imágenes ahí.")

# Leer la carpeta de portadas y hacer el "mapa"
mapa_imagenes = {}
try:
    archivos_en_covers = os.listdir("covers")
    for archivo in archivos_en_covers:
        if archivo.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            nombre_base = os.path.splitext(archivo)[0]
            nombre_norm = normalizar_nombre(nombre_base)
            mapa_imagenes[nombre_norm] = archivo 
except FileNotFoundError:
    pass 

# Procesar el archivo de texto y generar el HTML
try:
    with open("juegos.txt", "r", encoding="utf-8-sig") as archivo_txt:
        lineas = archivo_txt.readlines()
        
    juegos_procesados = 0

    with open("catalogo_completo.html", "w", encoding="utf-8") as archivo_html:
        archivo_html.write(html_inicio)
        
        for linea in lineas:
            juego = linea.strip()
            
            if juego:
                if juego.startswith("*") or juego.startswith("-"):
                    juego = juego[1:].strip()
                
                if not juego.startswith("#") and juego.lower() != "letra":
                    
                    juego_norm = normalizar_nombre(juego)
                    archivo_img_final = encontrar_mejor_imagen(juego_norm, mapa_imagenes)
                    
                    tarjeta_html = f"""        <li>
            <img src="covers/{archivo_img_final}" alt="Portada de {juego}" class="portada" loading="lazy" onerror="this.src='https://via.placeholder.com/215x300/1a1a1a/00d2ff?text=PS2+Cover'">
            <div class="titulo-juego">{juego}</div>
        </li>\n"""
                    
                    archivo_html.write(tarjeta_html)
                    juegos_procesados += 1
                    
        archivo_html.write(html_fin)

    print(f"¡Éxito! Se ha creado 'catalogo_completo.html' con {juegos_procesados} juegos.")
    print("El diseño se ajustó para mostrar ~7 tarjetas por línea con aspecto 215x300.")

except FileNotFoundError:
    print("Error: No se encontró el archivo 'juegos.txt'. Asegúrate de que esté en la misma carpeta.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")
    
input("Presiona ENTER para salir...")