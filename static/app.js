const DEFAULT_VIEW = [-23.5505, -46.6333];
const DEFAULT_ZOOM = 11;
const WORLD_BOUNDS = [
  [-85, -180],
  [85, 180],
];
const DEFAULT_ROUTE = {
  start: "Av. Paulista, 1000, Bela Vista, São Paulo, SP",
  stops: [
    {
      address: "Rua Augusta, 1500, Consolação, São Paulo, SP",
      type: "pickup",
    },
    {
      address: "Rua Oscar Freire, 777, Jardins, São Paulo, SP",
      type: "pickup",
    },
    {
      address: "Parque Ibirapuera, São Paulo, SP",
      type: "stop",
    },
    {
      address:
        "Shopping Eldorado, Avenida Rebouças, 3970, Pinheiros, São Paulo, SP",
      type: "dropoff",
    },
  ],
  destination: "Aeroporto de Congonhas, São Paulo, SP",
};
const STOP_MARKER_CLASSES = {
  start: "route-marker-start",
  pickup: "route-marker-pickup",
  dropoff: "route-marker-dropoff",
  stop: "route-marker-stop",
  destination: "route-marker-destination",
};

const form = document.querySelector("#route-form");
const startInput = document.querySelector("#start-address");
const destinationInput = document.querySelector("#destination-address");
const pickupList = document.querySelector("#pickup-list");
const addPickupButton = document.querySelector("#add-pickup");
const calculateButton = document.querySelector("#calculate-route");
const statusCard = document.querySelector(".status-card");
const statusMessage = document.querySelector("#status-message");
const totalDistance = document.querySelector("#total-distance");
const routeResult = document.querySelector("#route-result");
const suggestionCache = new Map();

const map = L.map("map", {
  preferCanvas: true,
  zoomControl: true,
  minZoom: 3,
  maxBounds: WORLD_BOUNDS,
  maxBoundsViscosity: 1,
  zoomAnimation: false,
  fadeAnimation: false,
  markerZoomAnimation: false,
  inertia: false,
  worldCopyJump: false,
}).setView(DEFAULT_VIEW, DEFAULT_ZOOM);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  minZoom: 3,
  maxZoom: 17,
  noWrap: true,
  bounds: WORLD_BOUNDS,
  updateWhenIdle: true,
  updateWhenZooming: false,
  keepBuffer: 1,
  detectRetina: false,
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

let markers = [];
let previewMarkers = [];
let routeLine = null;

function createPickupInput(value = "", type = "pickup") {
  const row = document.createElement("div");
  row.className = "pickup-row";

  const typeSelect = document.createElement("select");
  typeSelect.className = "pickup-type";
  typeSelect.append(
    new Option("Coleta", "pickup"),
    new Option("Entrega", "dropoff"),
    new Option("Parada", "stop"),
  );

  const input = document.createElement("input");
  input.type = "text";
  input.className = "pickup-address";
  input.placeholder = "Endereço da parada";
  input.required = true;
  input.value = value;
  typeSelect.value = type;

  const removeButton = document.createElement("button");
  removeButton.type = "button";
  removeButton.className = "remove-pickup";
  removeButton.textContent = "X";
  removeButton.title = "Remover parada";
  removeButton.addEventListener("click", () => {
    if (pickupList.children.length > 1) {
      row.remove();
    }
  });

  row.append(typeSelect, input, removeButton);
  pickupList.appendChild(row);
  enhanceAddressInput(input);
}

function loadDefaultDemoRoute() {
  startInput.value = DEFAULT_ROUTE.start;
  destinationInput.value = DEFAULT_ROUTE.destination;
  pickupList.replaceChildren();

  for (const stop of DEFAULT_ROUTE.stops) {
    createPickupInput(stop.address, stop.type);
  }

  setStatus("Rota de exemplo carregada. Revise os endereços ou calcule a rota.");
}

function enhanceAddressInput(input) {
  const wrapper = document.createElement("div");
  wrapper.className = "address-field";
  input.parentNode?.insertBefore(wrapper, input);
  wrapper.appendChild(input);

  const suggestions = document.createElement("div");
  suggestions.className = "suggestions";
  suggestions.hidden = true;
  wrapper.appendChild(suggestions);

  let debounceId = null;
  let requestId = 0;

  input.addEventListener("input", () => {
    input.dataset.selected = "";
    input.dataset.latitude = "";
    input.dataset.longitude = "";
    window.clearTimeout(debounceId);

    const query = input.value.trim();
    if (query.length < 4) {
      hideSuggestions(suggestions);
      return;
    }

    debounceId = window.setTimeout(async () => {
      const currentRequestId = ++requestId;
      try {
        const results = await searchAddresses(query);
        if (currentRequestId !== requestId) {
          return;
        }
        renderSuggestions(input, suggestions, results);
      } catch {
        hideSuggestions(suggestions);
      }
    }, 700);
  });

  input.addEventListener("focus", () => {
    const query = input.value.trim();
    if (query.length >= 4 && suggestionCache.has(query)) {
      renderSuggestions(input, suggestions, suggestionCache.get(query));
    }
  });

  document.addEventListener("click", (event) => {
    if (!wrapper.contains(event.target)) {
      hideSuggestions(suggestions);
    }
  });
}

function setLoading(isLoading) {
  calculateButton.disabled = isLoading;
  addPickupButton.disabled = isLoading;
  calculateButton.textContent = isLoading ? "Calculando..." : "Calcular rota";

  for (const button of document.querySelectorAll(".remove-pickup")) {
    button.disabled = isLoading;
  }
}

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusCard.classList.toggle("is-error", isError);
}

function getStopsFromForm() {
  return [...document.querySelectorAll(".pickup-row")]
    .map((row) => {
      const input = row.querySelector(".pickup-address");
      const address = input.value.trim();
      const type = row.querySelector(".pickup-type").value;
      return { address, selected: selectedAddressFromInput(input), type };
    })
    .filter((stop) => stop.address);
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.detail || "A requisição falhou.");
  }

  return response.json();
}

async function geocodeAddress(address) {
  return postJson("/geocode", { address });
}

async function searchAddresses(query) {
  if (suggestionCache.has(query)) {
    return suggestionCache.get(query);
  }

  const response = await fetch(
    `/geocode/search?q=${encodeURIComponent(query)}&limit=5`,
  );
  if (!response.ok) {
    throw new Error("Não foi possível buscar sugestões.");
  }

  const results = await response.json();
  suggestionCache.set(query, results);
  return results;
}

async function fetchRoadGeometry(stops) {
  const coordinates = stops
    .map((stop) => `${stop.longitude},${stop.latitude}`)
    .join(";");
  const url = `https://router.project-osrm.org/route/v1/driving/${coordinates}?overview=full&geometries=geojson&steps=false`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Não foi possível calcular a rota pelas ruas.");
  }

  const data = await response.json();
  if (data.code !== "Ok" || !data.routes?.[0]?.geometry?.coordinates) {
    throw new Error("O OSRM não encontrou uma rota pelas ruas.");
  }

  return {
    points: data.routes[0].geometry.coordinates.map(([longitude, latitude]) => [
      latitude,
      longitude,
    ]),
    distanceKm: data.routes[0].distance / 1000,
    durationMinutes: data.routes[0].duration / 60,
  };
}

function toRouteStop(label, geocodedAddress, type = undefined) {
  return {
    label,
    address: geocodedAddress.display_name,
    latitude: geocodedAddress.latitude,
    longitude: geocodedAddress.longitude,
    type,
  };
}

function routeStopLabel(type, indexByType) {
  const baseLabels = {
    pickup: "Coleta",
    dropoff: "Entrega",
    stop: "Parada",
  };
  const label = baseLabels[type] || "Parada";
  indexByType[type] = (indexByType[type] || 0) + 1;

  return `${label} ${indexByType[type]}`;
}

function selectedAddressFromInput(input) {
  if (!input.dataset.latitude || !input.dataset.longitude) {
    return null;
  }

  return {
    address: input.value.trim(),
    display_name: input.dataset.selected || input.value.trim(),
    latitude: Number(input.dataset.latitude),
    longitude: Number(input.dataset.longitude),
    provider: "nominatim",
  };
}

function renderSuggestions(input, container, results) {
  container.replaceChildren();

  if (!results.length) {
    hideSuggestions(container);
    return;
  }

  for (const result of results) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "suggestion-option";
    button.textContent = result.display_name;
    button.addEventListener("click", () => {
      selectAddress(input, result);
      hideSuggestions(container);
    });
    container.appendChild(button);
  }

  container.hidden = false;
}

function hideSuggestions(container) {
  container.hidden = true;
  container.replaceChildren();
}

function selectAddress(input, result) {
  input.value = result.display_name;
  input.dataset.selected = result.display_name;
  input.dataset.latitude = String(result.latitude);
  input.dataset.longitude = String(result.longitude);
  addPreviewMarker(input, result);
}

function addPreviewMarker(input, result) {
  if (input.previewMarker) {
    input.previewMarker.remove();
  }

  const marker = L.circleMarker([result.latitude, result.longitude], {
    radius: 7,
    color: "#0f5268",
    fillColor: "#21a0a0",
    fillOpacity: 0.86,
    weight: 2,
  }).addTo(map);

  const popup = document.createElement("span");
  popup.textContent = result.display_name;
  marker.bindPopup(popup);

  input.previewMarker = marker;
  previewMarkers.push(marker);
  map.setView([result.latitude, result.longitude], Math.max(map.getZoom(), 14), {
    animate: false,
  });
}

function createRouteMarker(stop) {
  const markerClass = STOP_MARKER_CLASSES[stop.type] || STOP_MARKER_CLASSES.stop;
  const icon = L.divIcon({
    className: "",
    html: `<span class="route-marker ${markerClass}"><span>${stop.sequence + 1}</span></span>`,
    iconSize: [34, 42],
    iconAnchor: [17, 34],
    popupAnchor: [0, -34],
  });

  return L.marker([stop.latitude, stop.longitude], { icon });
}

function createRoutePopup(stop) {
  const popup = document.createElement("div");
  popup.className = "route-popup";

  const label = document.createElement("strong");
  label.textContent = `${stop.sequence + 1}. ${stop.label}`;

  const type = document.createElement("span");
  type.textContent = formatStopType(stop.type);

  popup.append(label, type);

  if (stop.address) {
    const address = document.createElement("small");
    address.textContent = stop.address;
    popup.append(address);
  }

  return popup;
}

function clearMap() {
  for (const marker of markers) {
    marker.remove();
  }
  markers = [];

  if (routeLine) {
    routeLine.remove();
    routeLine = null;
  }
}

function clearPreviewMarkers() {
  for (const marker of previewMarkers) {
    marker.remove();
  }
  previewMarkers = [];
}

async function renderMap(stops) {
  clearMap();
  clearPreviewMarkers();

  const stopPoints = stops.map((stop) => [stop.latitude, stop.longitude]);
  let routePoints = stopPoints;

  try {
    const roadRoute = await fetchRoadGeometry(stops);
    routePoints = roadRoute.points;
    totalDistance.textContent = `${roadRoute.distanceKm.toFixed(2)} km`;
    setStatus(
      `Rota calculada pelas ruas. Tempo estimado: ${Math.round(
        roadRoute.durationMinutes,
      )} min.`,
    );
  } catch (error) {
    setStatus(`${error.message} Mostrando linha estimada.`, true);
  }

  routeLine = L.polyline(routePoints, {
    color: "#176b87",
    weight: 3,
    opacity: 0.86,
    smoothFactor: 2,
  }).addTo(map);

  stops.forEach((stop) => {
    const marker = createRouteMarker(stop)
      .addTo(map)
      .bindPopup(createRoutePopup(stop));
    markers.push(marker);
  });

  map.fitBounds(L.latLngBounds(stopPoints), {
    padding: [48, 48],
    animate: false,
    maxZoom: 14,
  });
}

function renderResult(route) {
  totalDistance.textContent = `${route.total_distance_km.toFixed(2)} km`;
  routeResult.replaceChildren();

  for (const stop of route.stops) {
    const item = document.createElement("li");

    const number = document.createElement("span");
    number.className = "stop-number";
    number.textContent = String(stop.sequence + 1);

    const details = document.createElement("div");
    details.className = "stop-details";

    const title = document.createElement("strong");
    title.textContent = stop.label;

    const meta = document.createElement("span");
    const leg = stop.sequence === 0 ? "início" : `+${stop.leg_distance_km} km`;
    meta.textContent = `${formatStopType(stop.type)} - ${leg} - ${
      stop.address || "sem endereço salvo"
    }`;

    details.append(title, meta);
    item.append(number, details);
    routeResult.appendChild(item);
  }
}

function formatStopType(type) {
  const labels = {
    start: "início",
    pickup: "coleta",
    dropoff: "entrega",
    stop: "parada",
    destination: "destino",
  };

  return labels[type] || type;
}

async function handleSubmit(event) {
  event.preventDefault();

  const stopsFromForm = getStopsFromForm();
  if (stopsFromForm.length === 0) {
    setStatus("Adicione pelo menos uma parada.", true);
    return;
  }

  setLoading(true);
  setStatus("Convertendo endereços em coordenadas...");

  try {
    const start =
      selectedAddressFromInput(startInput) ||
      (await geocodeAddress(startInput.value.trim()));
    const destination =
      selectedAddressFromInput(destinationInput) ||
      (await geocodeAddress(destinationInput.value.trim()));
    const stops = [];
    const indexByType = {};

    for (const stop of stopsFromForm) {
      const geocodedStop =
        stop.selected || (await geocodeAddress(stop.address));
      stops.push(
        toRouteStop(
          routeStopLabel(stop.type, indexByType),
          geocodedStop,
          stop.type,
        ),
      );
    }

    setStatus("Calculando melhor ordem das paradas...");

    const optimizedRoute = await postJson("/routes/optimize", {
      start: toRouteStop("Início", start),
      stops,
      destination: toRouteStop("Destino", destination),
    });

    renderResult(optimizedRoute);
    await renderMap(optimizedRoute.stops);
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    setLoading(false);
  }
}

addPickupButton.addEventListener("click", () => createPickupInput());
form.addEventListener("submit", handleSubmit);

enhanceAddressInput(startInput);
enhanceAddressInput(destinationInput);
loadDefaultDemoRoute();
