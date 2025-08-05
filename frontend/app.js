// API Configuration - FIXED to use backend port directly
const API_BASE_URL = 'http://localhost:8003/api';  // Points to backend port

// State
let currentLanguage = 'en';
let generatedBlueprint = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    checkBackendHealth();
});

// Check backend health on load
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) {
            console.warn('Backend health check failed');
        }
    } catch (error) {
        console.error('Backend not available:', error);
        showError('Backend service is not available. Please ensure the server is running.');
    }
}

function initializeEventListeners() {
    // Form submission
    document.getElementById('blueprintForm').addEventListener('submit', handleFormSubmit);
    
    // Language toggle
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', (e) => handleLanguageChange(e.target.dataset.lang));
    });
}

async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    
    // Fix: Get the form values correctly
    formData.set('description', document.getElementById('description').value);
    formData.set('business_type', document.getElementById('businessType').value || '');
    formData.set('launch_location', document.getElementById('location').value || 'UAE');
    formData.set('budget', document.getElementById('budget').value || '');
    formData.set('timeline', document.getElementById('timeline').value || '');
    formData.set('involvement_preference', document.querySelector('input[name="involvement"]:checked').value);
    formData.set('preferred_language', currentLanguage === 'ar' ? 'Arabic' : 'English');
    
    // Show loading state
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/generate-blueprint`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate blueprint');
        }
        
        const blueprint = await response.json();
        generatedBlueprint = blueprint;
        
        displayBlueprint(blueprint);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to generate blueprint. Please try again.');
    } finally {
        hideLoading();
    }
}

function displayBlueprint(blueprint) {
    const resultsSection = document.getElementById('resultsSection');
    
    // Handle empty data gracefully
    const phases = blueprint.phases || [];
    const serviceRecommendations = blueprint.service_recommendations || [];
    const agencyShowcase = blueprint.agency_showcase || {};
    const competitors = blueprint.competitors || [];
    const creativeTouches = blueprint.creative_touches || [];
    const nextSteps = blueprint.next_steps || [];
    
    resultsSection.innerHTML = `
        <!-- Executive Summary -->
        <div class="card">
            <h2>📋 Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="label">Project Name:</span>
                    <span class="value">${blueprint.project_name || 'Your Project'}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Business Type:</span>
                    <span class="value">${blueprint.business_type || 'General Business'}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Target Market:</span>
                    <span class="value">${blueprint.target_market || 'UAE Market'}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Launch Mode:</span>
                    <span class="value">${blueprint.launch_mode || 'Hybrid'}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Timeline:</span>
                    <span class="value">${blueprint.timeline || '3-6 months'}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Budget Estimate:</span>
                    <span class="value">${blueprint.budget_estimate || 'To be determined'}</span>
                </div>
            </div>
        </div>

        <!-- Project Phases -->
        ${phases.length > 0 ? `
        <div class="card">
            <h2>📊 Multi-Phase Action Plan</h2>
            <div class="phases-timeline">
                ${phases.map((phase, index) => `
                    <div class="phase-card">
                        <div class="phase-number">${index + 1}</div>
                        <h3>${phase.phase_name}</h3>
                        <p class="phase-objective">${phase.objective}</p>
                        
                        <div class="phase-details">
                            <div class="detail-section">
                                <h4>Deliverables:</h4>
                                <ul>
                                    ${phase.deliverables.map(d => `<li>${d}</li>`).join('')}
                                </ul>
                            </div>
                            
                            <div class="detail-section">
                                <h4>Creative Recommendations:</h4>
                                <ul>
                                    ${phase.creative_recommendations.map(c => `<li>${c}</li>`).join('')}
                                </ul>
                            </div>
                            
                            <div class="phase-meta">
                                <span class="duration">⏱ ${phase.estimated_duration}</span>
                                <span class="budget">💰 ${phase.budget_range}</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
        ` : ''}

        <!-- Service Recommendations -->
        ${serviceRecommendations.length > 0 ? `
        <div class="card">
            <h2>🛠 Service Line Recommendations</h2>
            ${serviceRecommendations.map(service => `
                <div class="service-card">
                    <h3>${service.name}</h3>
                    <p><strong>Why Essential:</strong> ${service.why_essential}</p>
                    <p><strong>Deliverables:</strong> ${service.deliverables.join(', ')}</p>
                    <div class="service-meta">
                        <span>💰 ${service.budget_range}</span>
                        <span>⏱ ${service.timeline}</span>
                    </div>
                </div>
            `).join('')}
        </div>
        ` : ''}

        <!-- Agency Showcase -->
        ${Object.keys(agencyShowcase).length > 0 ? `
        <div class="card">
            <h2>🏢 Recommended Agencies</h2>
            ${Object.entries(agencyShowcase).map(([service, agencies]) => `
                <div class="agency-section">
                    <h3>For ${service}:</h3>
                    <div class="agency-grid">
                        ${agencies.map(agency => `
                            <div class="agency-card">
                                <h4>${agency.name}</h4>
                                <div class="match-score">${Math.round(agency.match_fit_score * 100)}% Match</div>
                                <p><strong>Key Strengths:</strong></p>
                                <ul>
                                    ${agency.key_strengths.map(s => `<li>${s}</li>`).join('')}
                                </ul>
                                <p><strong>Experience:</strong> ${agency.relevant_experience}</p>
                                <p><strong>Availability:</strong> ${agency.availability}</p>
                                <p class="why-consider">${agency.why_consider}</p>
                            </div>
                        `).join('')}
                    </div>
                    <button class="btn btn-secondary" onclick="requestMatchmaking()">
                        💡 Not sure whom to pick? Let us shortlist 3 best-fit agencies for you
                    </button>
                </div>
            `).join('')}
        </div>
        ` : ''}

        <!-- Competitors -->
        ${competitors.length > 0 ? `
        <div class="card">
            <h2>🎯 Competitor Watchlist</h2>
            <div class="competitor-list">
                ${competitors.map(comp => `
                    <div class="competitor-item">
                        <strong>${comp.name}</strong>
                        <span>${comp.location}</span>
                        <span class="comp-type">${comp.type}</span>
                        ${comp.website ? `<a href="${comp.website}" target="_blank">Visit</a>` : ''}
                    </div>
                `).join('')}
            </div>
        </div>
        ` : ''}

        <!-- Creative Touches -->
        ${creativeTouches.length > 0 ? `
        <div class="card">
            <h2>✨ Creative Touches & Add-Ons</h2>
            <ul class="creative-list">
                ${creativeTouches.map(touch => `<li>${touch}</li>`).join('')}
            </ul>
        </div>
        ` : ''}

        <!-- Next Steps -->
        <div class="card">
            <h2>👉 Next Steps</h2>
            <ol class="next-steps">
                ${nextSteps.length > 0 ? 
                    nextSteps.map(step => `<li>${step}</li>`).join('') :
                    '<li>Review your generated blueprint</li><li>Contact our team for implementation</li>'
                }
            </ol>
            
            <div class="cta-buttons">
                <button class="btn btn-primary" onclick="requestMatchmaking()">
                    🎯 Get 3 Best-Fit Agency Matches
                </button>
                <button class="btn btn-secondary" onclick="bookConcierge()">
                    📅 Book a Free Session with Project Concierge
                </button>
                <button class="btn btn-secondary" onclick="downloadPDF()">
                    📄 Download Blueprint (PDF)
                </button>
            </div>
        </div>
    `;
    
    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function handleLanguageChange(lang) {
    currentLanguage = lang;
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });
    
    // Toggle RTL for Arabic
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    
    // Update UI text
    if (lang === 'ar') {
        document.querySelector('h1').textContent = '🚀 مولد مخطط مشروع Topsdraw بالذكاء الاصطناعي';
    } else {
        document.querySelector('h1').textContent = '🚀 Topsdraw AI Blueprint Generator';
    }
}

function showLoading() {
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('resultsSection').classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loadingState').classList.add('hidden');
}

function showError(message) {
    // Better error display
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <div style="background: #fee; border: 1px solid #fcc; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
            <strong>Error:</strong> ${message}
        </div>
    `;
    document.querySelector('.input-section').prepend(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Action functions
function requestMatchmaking() {
    alert('Matchmaking request submitted! We will contact you within 24 hours.');
}

function bookConcierge() {
    window.open('https://calendly.com/topsdraw-concierge', '_blank');
}

function downloadPDF() {
    if (generatedBlueprint) {
        // Create a text version of the blueprint
        const text = `
TOPSDRAW PROJECT BLUEPRINT
========================
Project Name: ${generatedBlueprint.project_name}
Business Type: ${generatedBlueprint.business_type}
Target Market: ${generatedBlueprint.target_market}
Timeline: ${generatedBlueprint.timeline}
Budget: ${generatedBlueprint.budget_estimate}

Generated on: ${new Date(generatedBlueprint.generated_at).toLocaleString()}
        `;
        
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Topsdraw_Blueprint_${Date.now()}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    } else {
        alert('No blueprint to download yet. Please generate one first.');
    }
}