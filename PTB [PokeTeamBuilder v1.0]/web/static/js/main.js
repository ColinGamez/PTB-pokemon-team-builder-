// Main JavaScript for Pokemon Team Builder Web Interface

// Global variables
let socket;
let currentUser = null;
let teams = [];
let tournaments = [];

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    initializeSocket();
});

function initializeApp() {
    // Check if user is logged in
    const userElement = document.querySelector('[data-user]');
    if (userElement) {
        currentUser = JSON.parse(userElement.dataset.user);
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    console.log('Pokemon Team Builder Web App Initialized');
}

function setupEventListeners() {
    // Navigation active state
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Search functionality
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(handleSearch, 300));
    });
    
    // Auto-save functionality
    const autoSaveInputs = document.querySelectorAll('.auto-save');
    autoSaveInputs.forEach(input => {
        input.addEventListener('input', debounce(autoSave, 1000));
    });
}

function initializeSocket() {
    if (typeof io !== 'undefined') {
        socket = io();
        
        socket.on('connect', function() {
            console.log('Connected to server');
            showNotification('Connected to Pokemon Team Builder', 'success');
        });
        
        socket.on('disconnect', function() {
            console.log('Disconnected from server');
            showNotification('Connection lost. Attempting to reconnect...', 'warning');
        });
        
        socket.on('battle_update', function(data) {
            handleBattleUpdate(data);
        });
        
        socket.on('tournament_updated', function(data) {
            handleTournamentUpdate(data);
        });
        
        socket.on('notification', function(data) {
            showNotification(data.message, data.type);
        });
    }
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showNotification(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, duration);
}

function showLoading(element, show = true) {
    if (show) {
        element.innerHTML = `
            <div class="d-flex justify-content-center align-items-center p-3">
                <div class="spinner-border me-2" role="status"></div>
                <span>Loading...</span>
            </div>
        `;
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// API Functions
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, finalOptions);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Request failed:', error);
        showNotification(`Error: ${error.message}`, 'danger');
        throw error;
    }
}

// Pokemon Search
async function searchPokemon(query) {
    try {
        const data = await apiRequest(`/api/pokemon/search?q=${encodeURIComponent(query)}`);
        return data;
    } catch (error) {
        return [];
    }
}

function handleSearch(event) {
    const query = event.target.value.trim();
    const resultsContainer = document.getElementById('search-results');
    
    if (!query || query.length < 2) {
        if (resultsContainer) {
            resultsContainer.innerHTML = '';
        }
        return;
    }
    
    searchPokemon(query).then(results => {
        if (resultsContainer) {
            displaySearchResults(results, resultsContainer);
        }
    });
}

function displaySearchResults(results, container) {
    if (results.length === 0) {
        container.innerHTML = '<div class="text-muted p-2">No Pokemon found</div>';
        return;
    }
    
    const html = results.map(pokemon => `
        <div class="search-result-item p-2 border-bottom" data-pokemon-id="${pokemon.id}">
            <div class="d-flex align-items-center">
                <div class="me-3">
                    <img src="/static/images/pokemon/${pokemon.id}.png" 
                         alt="${pokemon.name}" class="pokemon-sprite" 
                         onerror="this.src='/static/images/pokemon/unknown.png'">
                </div>
                <div>
                    <strong>${pokemon.name}</strong>
                    <div class="small text-muted">
                        ${pokemon.types.map(type => 
                            `<span class="badge type-${type.toLowerCase()}">${type}</span>`
                        ).join(' ')}
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
    
    // Add click handlers
    container.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', function() {
            const pokemonId = this.dataset.pokemonId;
            selectPokemon(pokemonId);
        });
    });
}

// Team Management
async function loadTeams() {
    try {
        const data = await apiRequest('/api/teams');
        teams = data;
        return teams;
    } catch (error) {
        return [];
    }
}

async function createTeam(teamData) {
    try {
        const data = await apiRequest('/api/teams', {
            method: 'POST',
            body: JSON.stringify(teamData)
        });
        
        if (data.success) {
            teams.push(data.team);
            showNotification('Team created successfully!', 'success');
            return data.team;
        }
    } catch (error) {
        return null;
    }
}

async function updateTeam(teamId, teamData) {
    try {
        const data = await apiRequest(`/api/teams/${teamId}`, {
            method: 'PUT',
            body: JSON.stringify(teamData)
        });
        
        if (data.success) {
            const index = teams.findIndex(t => t.id === teamId);
            if (index !== -1) {
                teams[index] = data.team;
            }
            showNotification('Team updated successfully!', 'success');
            return data.team;
        }
    } catch (error) {
        return null;
    }
}

async function deleteTeam(teamId) {
    try {
        const data = await apiRequest(`/api/teams/${teamId}`, {
            method: 'DELETE'
        });
        
        if (data.success) {
            teams = teams.filter(t => t.id !== teamId);
            showNotification('Team deleted successfully!', 'success');
            return true;
        }
    } catch (error) {
        return false;
    }
}

// Tournament Functions
async function loadTournaments() {
    try {
        const data = await apiRequest('/api/tournaments');
        tournaments = data;
        return tournaments;
    } catch (error) {
        return [];
    }
}

async function joinTournament(tournamentId, teamId) {
    try {
        const data = await apiRequest(`/api/tournaments/${tournamentId}/join`, {
            method: 'POST',
            body: JSON.stringify({ team_id: teamId })
        });
        
        if (data.success) {
            showNotification('Joined tournament successfully!', 'success');
            return true;
        }
    } catch (error) {
        return false;
    }
}

// Battle System
function handleBattleUpdate(data) {
    const battleContainer = document.getElementById('battle-container');
    if (battleContainer) {
        updateBattleDisplay(data);
    }
}

function updateBattleDisplay(battleData) {
    // Update battle UI with new data
    console.log('Battle update:', battleData);
}

// Tournament System
function handleTournamentUpdate(data) {
    const tournamentContainer = document.getElementById('tournament-container');
    if (tournamentContainer) {
        updateTournamentDisplay(data);
    }
}

function updateTournamentDisplay(tournamentData) {
    // Update tournament bracket display
    console.log('Tournament update:', tournamentData);
}

// Auto-save functionality
function autoSave() {
    const form = document.querySelector('.auto-save-form');
    if (form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Save to localStorage as backup
        localStorage.setItem('auto-save-data', JSON.stringify({
            data: data,
            timestamp: new Date().toISOString()
        }));
        
        console.log('Auto-saved form data');
    }
}

// Load auto-saved data
function loadAutoSavedData() {
    const saved = localStorage.getItem('auto-save-data');
    if (saved) {
        try {
            const { data, timestamp } = JSON.parse(saved);
            const saveTime = new Date(timestamp);
            const now = new Date();
            
            // Only restore if saved within last hour
            if (now - saveTime < 3600000) {
                return data;
            }
        } catch (error) {
            console.error('Failed to load auto-saved data:', error);
        }
    }
    return null;
}

// Pokemon selection
function selectPokemon(pokemonId) {
    const event = new CustomEvent('pokemon-selected', {
        detail: { pokemonId: pokemonId }
    });
    document.dispatchEvent(event);
}

// Initialize page-specific functionality
function initializePage() {
    const page = document.body.dataset.page;
    
    switch (page) {
        case 'team-builder':
            initializeTeamBuilder();
            break;
        case 'battle':
            initializeBattle();
            break;
        case 'tournament':
            initializeTournament();
            break;
        case 'breeding':
            initializeBreeding();
            break;
    }
}

function initializeTeamBuilder() {
    // Team builder specific initialization
    console.log('Initializing team builder');
}

function initializeBattle() {
    // Battle system specific initialization
    console.log('Initializing battle system');
}

function initializeTournament() {
    // Tournament specific initialization
    console.log('Initializing tournament system');
}

function initializeBreeding() {
    // Breeding calculator specific initialization
    console.log('Initializing breeding calculator');
}

// Error handling
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    showNotification('An unexpected error occurred', 'danger');
});

// Performance monitoring
window.addEventListener('load', function() {
    const loadTime = performance.now();
    console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
});

// Export functions for use in other scripts
window.PokemonTeamBuilder = {
    apiRequest,
    searchPokemon,
    loadTeams,
    createTeam,
    updateTeam,
    deleteTeam,
    loadTournaments,
    joinTournament,
    showNotification,
    formatDate
};