document.addEventListener('DOMContentLoaded', initializeApp);

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
const tempColorScale = d3.scaleSequential(d3.interpolateWarm)
    .domain([5, 30]); 


// --- 3. Fonctions de Zoom (Liées aux boutons HTML) ---
window.handleZoom = (factor) => {
    svg.transition().call(zoomBehavior.scaleBy, factor);
};
window.handleReset = () => {
    svg.transition().duration(750).call(zoomBehavior.transform, d3.zoomIdentity);
};


// --- 4. Logique de Région (Fonction essentielle pour le filtre) ---
/**
 * Détermine la région marine basée sur les coordonnées.
 */
function assignRegion(lat, lng) {
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


// --- 5. Fonction d'Affichage des Détails au Clic ---
function displayDetails(data) {
    const imageFileName = data.image.split('/').pop(); 
    // Construit l'URL statique correcte pour Flask (Vérifiez si c'est 'especes' ou 'photos' !)
    const imageUrl = `/static/photos/${imageFileName}`; // Utilisé 'photos' selon votre dernier snippet

    detailsPanel.innerHTML = `
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


// --- 6. Fonction de Dessin des Points (Optimisée) ---
function drawPoints(observations) {
    const points = g.selectAll(".observation-point")
        .data(observations, d => `${d.lat}-${d.lng}-${d.common_name}`);
        
    points.exit()
        .transition().duration(200)
        .attr("r", 0) 
        .remove();

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
            return coords ? `translate(${coords[0]},${coords[1]})` : null; 
        })
        .on("click", (event, d) => {
            displayDetails(d); 
        })
        .transition().duration(500) 
        .attr("r", 4); 

    points.attr("opacity", 0.85);

    console.log(`Dessin de ${observations.length} points sur la carte.`);
}

// --- 7. Logique de Filtrage ---
function applyFilters() {
    const groupFilter = document.getElementById('group-filter').value;
    const regionFilter = document.getElementById('region-filter').value;
    const monthFilter = document.getElementById('season-filter').value;

    let filteredData = allObservations.filter(d => {
        const matchGroup = groupFilter === 'all' || d.common_name === groupFilter;
        const matchRegion = regionFilter === 'all' || d.region === regionFilter;
        const matchMonth = monthFilter === 'all' || d.month === monthFilter;

        return matchGroup && matchRegion && matchMonth;
    });

    document.getElementById('observation-count').textContent = 
        `${filteredData.length} ${filteredData.length > 1 ? 'observations trouvées' : 'observation trouvée'}.`;

    drawPoints(filteredData);
}

// --- 8. Chargement des Données et Configuration des Filtres ---
async function loadObservations() {
    try {
        const data = await d3.json(dataUrl);
        
        // Traitement pour ajouter la région à chaque observation
        allObservations = data.map(d => ({
            ...d, 
            region: assignRegion(d.lat, d.lng) 
        }));
        
        console.log(`Données chargées : ${allObservations.length} observations.`);
        
        // Extraction des valeurs uniques
        const allCommonNames = [...new Set(allObservations.map(d => d.common_name))].sort();
        const allRegions = [...new Set(allObservations.map(d => d.region))].sort(); 
        const allMonths = [...new Set(allObservations.map(d => d.month.toLowerCase()))].sort(); 

        // Peupler les menus
        populateFilter('group-filter', 'Toutes les espèces (Nom Commun)', allCommonNames);
        populateFilter('region-filter', 'Toutes les régions marines', allRegions);
        populateFilter('season-filter', 'Toutes les périodes (Mois)', allMonths);
        
        // Lier la fonction de filtrage aux événements 'change'
        document.getElementById('group-filter').addEventListener('change', applyFilters);
        document.getElementById('region-filter').addEventListener('change', applyFilters);
        document.getElementById('season-filter').addEventListener('change', applyFilters);

        // Initialisation de la carte avec les filtres par défaut
        applyFilters(); 

    } catch (error) {
        console.error("Erreur lors du chargement des données d'observation:", error);
        detailsPanel.innerHTML = `<p class="text-red-500">Erreur : Le serveur n'a pas pu charger le fichier JSON.</p>`;
    }
}

// --- 9. Fonction Utilitaire pour Peupler les Menus ---
function populateFilter(elementId, defaultLabel, optionsArray) {
    const select = document.getElementById(elementId);
    let optionsHtml = `<option value="all">${defaultLabel}</option>`;
    
    optionsArray.forEach(option => {
        optionsHtml += `<option value="${option}">${option}</option>`;
    });
    
    select.innerHTML = optionsHtml;
    select.disabled = false;
}


// --- 10. Initialisation de la Carte ---
function initializeMap() {
    projection = d3.geoMercator()
        .center([-10, 30])
        .scale(600) 
        .translate([500, 500]);
    
    zoomBehavior = d3.zoom()
        .scaleExtent([1, 8])
        .on("zoom", (event) => {
            g.attr("transform", event.transform);
        });

    svg.call(zoomBehavior);

    g.append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", 1000)
        .attr("height", 700)
        .attr("fill", "#E6F2F7");

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

        loadObservations(); 

    }).catch(error => {
        console.error("Erreur lors du chargement du TopoJSON:", error);
    });
}

// --- 11. Fonctions de Gestion des Onglets et Lancement de l'App ---

/**
 * Affiche le contenu sélectionné et met à jour l'apparence des boutons.
 */
function showContent(contentId, tabId) {
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
        content.classList.remove('block');
    });

    document.querySelectorAll('[id^="tab-"]').forEach(tab => {
        tab.classList.remove('bg-white', 'text-blue-700', 'border-blue-700');
        tab.classList.add('text-gray-600', 'border-transparent', 'hover:border-gray-400');
    });
    
    const targetContent = document.getElementById(contentId);
    if (targetContent) {
        targetContent.classList.remove('hidden');
        targetContent.classList.add('block');
    }

    const activeTab = document.getElementById(tabId);
    if (activeTab) {
        activeTab.classList.add('bg-white', 'text-blue-700', 'border-blue-700');
        activeTab.classList.remove('text-gray-600', 'border-transparent', 'hover:border-gray-400');
    }
}

/**
 * Fonction principale de lancement au chargement du DOM.
 */
function initializeApp() {
    initializeMap(); 
    showContent('map-content', 'tab-map'); // Afficher la carte par défaut au démarrage
}