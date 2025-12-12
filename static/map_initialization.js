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
// --- 5. Fonction d'Affichage des Détails au Clic ---
function displayDetails(data) {
    console.log("Données:", data);
    
    // 1. Récupérer la hauteur de vague
    let waveHeight = data.avg_wave || data.avg_wave_height || data.VHM0;
    console.log("Hauteur vague:", waveHeight);
    
    const wave = interpretWaveHeight(waveHeight);
    
    // 2. Formater les données
    const month = data.month ? 
        data.month.charAt(0).toUpperCase() + data.month.slice(1) : 
        'Non spécifié';
    
    // 3. Construire l'HTML
    detailsPanel.innerHTML = `
        <!-- Message d'instruction caché -->
        <p class="text-gray-500 italic mb-4 hidden">
            Cliquez sur un point coloré sur la carte pour voir les détails.
        </p>
        
        <!-- Carte des vagues COMPACTE -->
        <div class="mb-4 p-3 rounded-lg border-l-4 ${wave.class}">
            <div class="flex items-center justify-between">
                <div>
                    <h4 class="font-bold text-gray-700 text-sm">🌊 Vagues (VHM0)</h4>
                    <p class="text-lg font-bold mt-1">${wave.text}</p>
                </div>
                <div class="text-right">
                    <p class="text-xs text-gray-600">${wave.description}</p>
                </div>
            </div>
        </div>
        
        <!-- Espèce -->
        <div class="mb-4">
            <h3 class="text-lg font-bold text-blue-800">${data.common_name || 'Observation'}</h3>
            <p class="text-sm italic text-gray-600">${data.species ? data.species.replace(/_/g, ' ') : ''}</p>
        </div>
        
        <!-- Température et Mois (compact) -->
        <div class="flex items-center justify-between mb-4 p-3 bg-blue-50 rounded-lg">
            <div class="text-center">
                <p class="text-xs text-gray-500">Température</p>
                <p class="text-2xl font-bold" style="color: ${tempColorScale(parseFloat(data.avg_temp || 0))}">
                    ${parseFloat(data.avg_temp || 0).toFixed(1)}°C
                </p>
            </div>
            <div class="h-8 w-px bg-gray-300"></div>
            <div class="text-center">
                <p class="text-xs text-gray-500">Mois</p>
                <p class="text-lg font-semibold text-gray-700">${month}</p>
            </div>
        </div>
        
        <!-- Vent et Pluie -->
        <div class="grid grid-cols-2 gap-3 mb-4">
            <div class="p-3 bg-gray-50 rounded border">
                <div class="flex items-center">
                    <span class="text-gray-500 mr-2">🌬️</span>
                    <div>
                        <p class="text-xs text-gray-500">Vent</p>
                        <p class="font-bold">${parseFloat(data.avg_wind || 0).toFixed(1)} km/h</p>
                    </div>
                </div>
            </div>
            <div class="p-3 bg-gray-50 rounded border">
                <div class="flex items-center">
                    <span class="text-gray-500 mr-2">🌧️</span>
                    <div>
                        <p class="text-xs text-gray-500">Pluie</p>
                        <p class="font-bold">${parseFloat(data.avg_rain || 0).toFixed(1)} mm</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Position -->
        <div class="text-xs text-gray-500 mb-3">
            📍 ${parseFloat(data.lat || 0).toFixed(4)}°N, ${parseFloat(data.lng || 0).toFixed(4)}°E
        </div>
        
        <!-- Image (si disponible) -->
        ${data.image && data.image !== 'default.jpg' ? `
        <div class="mt-3">
            <img src="/static/photos/${data.image}" 
                 alt="${data.common_name || 'Observation'}"
                 class="w-full h-32 object-cover rounded-lg shadow">
        </div>
        ` : ''}
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
function interpretWaveHeight(v) {
    if (v === null || v === undefined) {
        return {
            text: "Données indisponibles",
            description: "",
            class: "wave-class-0"
        };
    }

    if (v < 0.5)
        return { text: `${v.toFixed(2)} m`, description: "Conditions idéales – Mer calme", class: "wave-class-0" };
    if (v < 1)
        return { text: `${v.toFixed(2)} m`, description: "Bonne visibilité – Mer peu agitée", class: "wave-class-1" };
    if (v < 2)
        return { text: `${v.toFixed(2)} m`, description: "Mer agitée – vigilance recommandée", class: "wave-class-2" };
    if (v < 3)
        return { text: `${v.toFixed(2)} m`, description: "Mer forte – conditions difficiles", class: "wave-class-3" };

    return { text: `${v.toFixed(2)} m`, description: "Mer très forte – conditions dangereuses", class: "wave-class-4" };
}

/**
 * Fonction principale de lancement au chargement du DOM.
 */
function initializeApp() {
    initializeMap(); 
    showContent('map-content', 'tab-map'); // Afficher la carte par défaut au démarrage
}