document.addEventListener('DOMContentLoaded', initializeMap);

// --- 1. Constantes et Variables Globales ---
const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";
// Chemin de la route Flask pour accéder au fichier JSON
const dataUrl = "/data/observations.json"; 
const svg = d3.select("#main-map");
const g = d3.select("#map-group");
const detailsPanel = document.getElementById('details-panel');

let zoomBehavior; 
let projection; 
let allObservations = []; 

// --- 2. Échelle de Couleur pour la Température ---
// Température de 5°C (jaune/orange) à 30°C (bleu-vert)
const tempColorScale = d3.scaleSequential(d3.interpolateWarm)
    .domain([5, 30]); 


// --- 3. Fonctions de Zoom (Liées aux boutons HTML) ---
window.handleZoom = (factor) => {
    svg.transition().call(zoomBehavior.scaleBy, factor);
};
window.handleReset = () => {
    svg.transition().duration(750).call(zoomBehavior.transform, d3.zoomIdentity);
};


// --- Fonction d'Affichage des Détails au Clic (MODIFIÉE) ---
function displayDetails(data) {
    
    // 1. Extraire uniquement le nom du fichier du chemin absolu
    // Ex: '/Users/.../Balaenoptera_edeni.jpg' devient 'Balaenoptera_edeni.jpg'
    const imageFileName = data.image.split('/').pop(); 

    // 2. Construire l'URL statique correcte pour Flask : /static/photos/Nom_Du_Fichier.jpg
    const imageUrl = `/static/photos/${imageFileName}`;

    const panel = document.getElementById('details-panel');
    
    panel.innerHTML = `
        <h3 class="text-xl font-bold text-blue-800">${data.common_name}</h3>
        <p class="text-sm italic text-gray-600">${data.species}</p>
        <div class="my-3 flex items-center justify-between border-t pt-3">
            <div class="text-2xl font-extrabold" style="color: ${tempColorScale(parseFloat(data.avg_temp))};">
                ${data.avg_temp}°C
            </div>
            <p class="text-sm text-gray-700">Mois: ${data.month}</p>
        </div>
        
        <p class="text-xs mt-2">Vent: ${data.avg_wind} km/h | Pluie: ${data.avg_rain} mm</p>
        
        <img src="${imageUrl}" alt="${data.common_name}" class="w-full h-24 object-cover mt-4 rounded-md shadow-md">
    `;
}


// --- 5. Fonction de Dessin des Points (Optimisée par Data Join) ---
function drawPoints(observations) {
    
    // 1. Jointure de données (Data Join)
    const points = g.selectAll(".observation-point")
        // Utilisation d'une clé unique pour permettre à D3 de suivre chaque point
        .data(observations, d => `${d.lat}-${d.lng}-${d.common_name}`);
        
    // 2. Phase EXIT : Supprimer les points qui ne sont plus dans les données filtrées
    points.exit()
        .transition().duration(200)
        .attr("r", 0) 
        .remove();

    // 3. Phase ENTER : Ajouter les nouveaux points
    points.enter()
        .append("circle")
        .attr("class", "observation-point")
        .attr("r", 0) 
        .attr("fill", d => {
            const temp = parseFloat(d.avg_temp);
            return tempColorScale(temp);
        })
        .attr("stroke", "#333333")
        .attr("stroke-width", 0.5)
        .attr("opacity", 0.85)
        .attr("transform", d => {
            const coords = projection([d.lng, d.lat]);
            // Retourne null si la projection échoue (point en dehors du monde)
            return coords ? `translate(${coords[0]},${coords[1]})` : null; 
        })
        .on("click", (event, d) => {
            displayDetails(d); 
        })
        .transition().duration(500) 
        .attr("r", 4); // Taille finale

    // 4. Phase UPDATE (Mettre à jour les points qui restent)
    points.attr("opacity", 0.85);

    console.log(`Dessin de ${observations.length} points sur la carte.`);
}

// --- 6. Logique de Filtrage ---
function applyFilters() {
    // Récupérer les valeurs sélectionnées dans les menus déroulants
    const groupFilter = document.getElementById('group-filter').value;     // Nom Commun
    const regionFilter = document.getElementById('region-filter').value;   // Région Marine
    const monthFilter = document.getElementById('season-filter').value;    // Mois

    // Filtrer le tableau d'observations complet
    let filteredData = allObservations.filter(d => {
        
        // 1. Filtrer par Nom Commun
        const matchGroup = groupFilter === 'all' || d.common_name === groupFilter;

        // 2. Filtrer par Région (Utilise la propriété d.region calculée)
        const matchRegion = regionFilter === 'all' || d.region === regionFilter;
        
        // 3. Filtrer par Mois
        const matchMonth = monthFilter === 'all' || d.month === monthFilter;

        // Retourne true si toutes les conditions sont satisfaites
        return matchGroup && matchRegion && matchMonth;
    });

    // Mettre à jour le décompte affiché à l'utilisateur
    document.getElementById('observation-count').textContent = 
        `${filteredData.length} ${filteredData.length > 1 ? 'observations trouvées' : 'observation trouvée'}.`;

    // Redessiner uniquement les points filtrés de manière optimisée (Data Join)
    drawPoints(filteredData);
}
/**
 * Détermine la région marine basée sur les coordonnées.
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 * @returns {string} Le nom de la région
 */
function assignRegion(lat, lng) {
    // Utilisons des seuils simples pour les grandes régions de l'Atlantique Nord / Méditerranée
    
    // Méditerranée (Lat: 30-45, Lng: 0-30)
    if (lat < 45 && lng > 0 && lng < 30) {
        return "Méditerranée";
    }
    // Ouest de l'Europe/Golfe de Gascogne (Lat: 40-55, Lng: -10 à 0)
    if (lat > 40 && lat < 55 && lng > -10 && lng < 0) {
        return "Atlantique Nord-Est";
    }
    // Plus au Nord (Islande, Mer du Nord)
    if (lat >= 55) {
        return "Atlantique Nord-Ouest";
    }
    // Régions plus à l'Ouest (Açores, Canaries, etc.)
    if (lng < -10) {
        return "Atlantique Central";
    }
    
    return "Autre Région / Large";
}
// Dans la fonction loadObservations :

async function loadObservations() {
    try {
        const data = await d3.json(dataUrl);
        
        // --- NOUVEAU : Traitement des données pour assigner une région ---
        allObservations = data.map(d => ({
            ...d, // Conserver toutes les propriétés existantes
            // Ajouter la nouvelle propriété 'region'
            region: assignRegion(d.lat, d.lng) 
        }));
        
        console.log(`Données chargées : ${allObservations.length} observations.`);
        
        // 1. Extraction des valeurs uniques (MODIFIÉES)
        
        const allCommonNames = [...new Set(allObservations.map(d => d.common_name))].sort();
        // --- UTILISATION DE LA NOUVELLE PROPRIÉTÉ 'region' ---
        const allRegions = [...new Set(allObservations.map(d => d.region))].sort(); 
        const allMonths = [...new Set(allObservations.map(d => d.month.toLowerCase()))].sort(); 

        // 2. Peupler les menus déroulants
        populateFilter('group-filter', 'Toutes les espèces (Nom Commun)', allCommonNames);
        populateFilter('region-filter', 'Toutes les régions marines', allRegions); // CHANGEMENT DE LABEL
        populateFilter('season-filter', 'Toutes les périodes (Mois)', allMonths);
        
        // ... (Reste du code inchangé) ...
        
        // Lier la fonction de filtrage aux événements 'change'
        document.getElementById('group-filter').addEventListener('change', applyFilters);
        document.getElementById('region-filter').addEventListener('change', applyFilters);
        document.getElementById('season-filter').addEventListener('change', applyFilters);

        applyFilters(); 

    } catch (error) {
        // ...
    }
}
// --- 8. Fonction Utilitaire pour Peupler les Menus ---
function populateFilter(elementId, defaultLabel, optionsArray) {
    const select = document.getElementById(elementId);
    let optionsHtml = `<option value="all">${defaultLabel}</option>`;
    
    optionsArray.forEach(option => {
        optionsHtml += `<option value="${option}">${option}</option>`;
    });
    
    select.innerHTML = optionsHtml;
    select.disabled = false;
}


// --- 9. Initialisation de la Carte ---
function initializeMap() {
    // Définition de la Projection
    projection = d3.geoMercator()
        .center([-10, 30]) // Atlantique / Europe
        .scale(600) 
        .translate([500, 500]);
    
    // Comportement de Zoom
    zoomBehavior = d3.zoom()
        .scaleExtent([1, 8])
        .on("zoom", (event) => {
            g.attr("transform", event.transform);
        });

    svg.call(zoomBehavior);

    // Dessin du fond de l'océan
    g.append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", 1000)
        .attr("height", 700)
        .attr("fill", "#E6F2F7");

    // Chargement et Dessin du TopoJSON des pays
    d3.json(geoUrl).then(topology => {
        const worldGeo = topojson.feature(topology, topology.objects.countries);
        const pathGenerator = d3.geoPath().projection(projection);

        g.append("g")
            .attr("class", "land")
            .selectAll("path")
            .data(worldGeo.features)
            .enter()
            .append("path")
            .attr("d", pathGenerator)
            .attr("fill", "#D4D4D8")
            .attr("stroke", "#A1A1AA")
            .attr("stroke-width", 0.2);

        // Lancement du chargement des données après le fond de carte
        loadObservations(); 

    }).catch(error => {
        console.error("Erreur lors du chargement du TopoJSON:", error);
    });
}