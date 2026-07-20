// Admin Panel State
let resultsData = [];
let questionsData = [];
let activeTab = 'results';

// DOM Elements
const resultsTableBody = document.getElementById('results-table-body');
const questionsTableBody = document.getElementById('questions-table-body');
const resultsSearch = document.getElementById('results-search-container');
const questionsSearch = document.getElementById('questions-search-container');

// Stats Elements
const statTotalAttempts = document.getElementById('stat-total-attempts');
const statAvgScore = document.getElementById('stat-avg-score');
const statHighScore = document.getElementById('stat-high-score');
const statToughestTopic = document.getElementById('stat-toughest-topic');

// Modal Elements
const questionModal = document.getElementById('question-modal');
const questionForm = document.getElementById('question-form');
const modalTitle = document.getElementById('modal-title');
const editQId = document.getElementById('edit-q-id');
const formQuestion = document.getElementById('form-question');
const formTopic = document.getElementById('form-topic');
const formCorrect = document.getElementById('form-correct');

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
    loadResults();
    loadQuestions();
});

/**
 * Tab Navigation Switcher
 */
function switchTab(tabName) {
    activeTab = tabName;
    
    // Toggle active tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const clickedBtn = document.querySelector(`.tab-btn[onclick="switchTab('${tabName}')"]`);
    if (clickedBtn) clickedBtn.classList.add('active');
    
    // Toggle views
    if (tabName === 'results') {
        document.getElementById('tab-results').classList.remove('hidden');
        document.getElementById('tab-results').classList.add('fade-in');
        document.getElementById('tab-questions').classList.add('hidden');
        
        resultsSearch.classList.remove('hidden');
        questionsSearch.classList.add('hidden');
    } else {
        document.getElementById('tab-questions').classList.remove('hidden');
        document.getElementById('tab-questions').classList.add('fade-in');
        document.getElementById('tab-results').classList.add('hidden');
        
        questionsSearch.classList.remove('hidden');
        resultsSearch.classList.add('hidden');
    }
}

/**
 * Fetch and Render Analytics Stats
 */
async function loadDashboardStats() {
    try {
        const response = await fetch('/api/admin/stats');
        if (!response.ok) throw new Error('Failed to load stats.');
        const stats = await response.json();
        
        statTotalAttempts.textContent = stats.total_attempts || 0;
        statAvgScore.textContent = `${stats.total_attempts ? stats.avg_score.toFixed(1) : 0}%`;
        statHighScore.textContent = `${stats.total_attempts ? stats.high_score.toFixed(0) : 0}%`;
        
        // Find toughest topic (topic with most mistakes in weak_topics_count)
        let toughest = 'None';
        let maxMistakes = 0;
        if (stats.weak_topics_count && Object.keys(stats.weak_topics_count).length > 0) {
            for (const [topic, count] of Object.entries(stats.weak_topics_count)) {
                if (count > maxMistakes) {
                    maxMistakes = count;
                    toughest = topic;
                }
            }
        }
        statToughestTopic.textContent = toughest;
        
    } catch (error) {
        console.error('Stats load error:', error);
    }
}

/**
 * Fetch and Render Candidate Test Results
 */
async function loadResults() {
    try {
        const response = await fetch('/api/admin/results');
        if (!response.ok) throw new Error('Failed to load results.');
        resultsData = await response.json();
        renderResultsTable(resultsData);
    } catch (error) {
        console.error('Results load error:', error);
        resultsTableBody.innerHTML = `<tr><td colspan="7" class="loading-placeholder text-wrong">Failed to load candidate results from database.</td></tr>`;
    }
}

function renderResultsTable(data) {
    if (!data || data.length === 0) {
        resultsTableBody.innerHTML = `<tr><td colspan="7" class="loading-placeholder">No test results found in the database.</td></tr>`;
        return;
    }
    
    resultsTableBody.innerHTML = '';
    data.forEach(row => {
        const tr = document.createElement('tr');
        
        // Format Date
        let dateStr = 'N/A';
        if (row.created_at) {
            try {
                const dateObj = new Date(row.created_at);
                dateStr = dateObj.toLocaleDateString() + ' ' + dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            } catch (e) {
                dateStr = row.created_at;
            }
        }
        
        // Build Weak Topics Badges
        let weakBadges = '';
        if (row.weak_topics && row.weak_topics.length > 0) {
            // Deduplicate
            const uniqueWeak = [...new Set(row.weak_topics)];
            weakBadges = uniqueWeak.map(t => `<span class="tag-pill tag-weak" style="margin-right: 0.25rem; margin-bottom: 0.25rem;">${escapeHtml(t)}</span>`).join('');
        } else {
            weakBadges = '<span style="color:#10b981; font-size:0.8rem; font-weight:600;">🎉 Perfect!</span>';
        }
        
        // Grade Class mapping for styling
        const gradeClass = 'grade-' + row.grade.replace('+', 'plus').toLowerCase();
        
        tr.innerHTML = `
            <td>
                <div class="row-candidate-name">${escapeHtml(row.candidate_name)}</div>
                <div style="font-size:0.75rem; color:var(--text-secondary);">User ID: ${row.user_id}</div>
            </td>
            <td class="row-date">${dateStr}</td>
            <td class="score-badge">${row.score}</td>
            <td style="font-weight:600; color:#cbd5e1;">${row.percentage.toFixed(1)}%</td>
            <td><span class="grade-value ${gradeClass}" style="font-size: 1.15rem; font-weight: 800;">${row.grade}</span></td>
            <td>
                <div style="display:flex; flex-wrap:wrap; max-width: 250px;">
                    ${weakBadges}
                </div>
            </td>
            <td style="text-align: center;">
                <button class="btn-delete-row" title="Delete attempt" onclick="deleteAttempt(${row.id})">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                </button>
            </td>
        `;
        resultsTableBody.appendChild(tr);
    });
}

/**
 * Filter Results by Name
 */
function filterResults() {
    const query = document.getElementById('search-input').value.toLowerCase().trim();
    if (!query) {
        renderResultsTable(resultsData);
        return;
    }
    
    const filtered = resultsData.filter(row => 
        row.candidate_name.toLowerCase().includes(query) || 
        row.grade.toLowerCase().includes(query) ||
        (row.weak_topics && row.weak_topics.some(t => t.toLowerCase().includes(query)))
    );
    renderResultsTable(filtered);
}

/**
 * Delete a Test Result Attempt
 */
async function deleteAttempt(resultId) {
    if (!confirm('Are you sure you want to permanently delete this candidate result attempt?')) return;
    
    try {
        const response = await fetch(`/api/admin/results/${resultId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Deletion failed.');
        
        // Refresh stats & results
        loadDashboardStats();
        loadResults();
    } catch (error) {
        console.error('Delete result error:', error);
        alert('Failed to delete candidate result.');
    }
}

/**
 * Fetch and Render Questions
 */
async function loadQuestions() {
    try {
        const response = await fetch('/api/admin/questions');
        if (!response.ok) throw new Error('Failed to load questions.');
        questionsData = await response.json();
        renderQuestionsTable(questionsData);
    } catch (error) {
        console.error('Questions load error:', error);
        questionsTableBody.innerHTML = `<tr><td colspan="5" class="loading-placeholder text-wrong">Failed to load questions database.</td></tr>`;
    }
}

function renderQuestionsTable(data) {
    if (!data || data.length === 0) {
        questionsTableBody.innerHTML = `<tr><td colspan="5" class="loading-placeholder">No questions found in the database. Add some!</td></tr>`;
        return;
    }
    
    questionsTableBody.innerHTML = '';
    data.forEach(q => {
        const tr = document.createElement('tr');
        
        // Format options list with highlight on correct answer
        const optionsList = q.options.map(opt => {
            const isCorrect = opt.trim().toLowerCase() === q.answer.trim().toLowerCase();
            return isCorrect 
                ? `<li style="color:#34d399; font-weight: 600;">✅ ${escapeHtml(opt)}</li>` 
                : `<li style="color:var(--text-secondary); opacity: 0.85;">• ${escapeHtml(opt)}</li>`;
        }).join('');
        
        tr.innerHTML = `
            <td><strong style="color:var(--text-secondary);">${q.id}</strong></td>
            <td>
                <div class="question-text-cell">${escapeHtml(q.question)}</div>
                <ul style="list-style: none; margin-top: 0.5rem; padding-left: 0.25rem; font-size: 0.82rem;">
                    ${optionsList}
                </ul>
            </td>
            <td><span class="topic-badge-cell">${escapeHtml(q.topic)}</span></td>
            <td><span style="color:#10b981; font-weight:600;">${escapeHtml(q.answer)}</span></td>
            <td style="text-align: center;">
                <div style="display:flex; gap:0.25rem; justify-content:center;">
                    <button class="btn-edit-row" title="Edit question" onclick="openEditModal(${q.id})">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                    </button>
                    <button class="btn-delete-row" title="Delete question" onclick="deleteQuestion(${q.id})">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                    </button>
                </div>
            </td>
        `;
        questionsTableBody.appendChild(tr);
    });
}

/**
 * Filter Questions by Text / Topic
 */
function filterQuestions() {
    const query = document.getElementById('q-search-input').value.toLowerCase().trim();
    if (!query) {
        renderQuestionsTable(questionsData);
        return;
    }
    
    const filtered = questionsData.filter(q => 
        q.question.toLowerCase().includes(query) || 
        q.topic.toLowerCase().includes(query) ||
        q.options.some(opt => opt.toLowerCase().includes(query))
    );
    renderQuestionsTable(filtered);
}

/**
 * Delete Question
 */
async function deleteQuestion(qId) {
    if (!confirm('Are you sure you want to delete this question? It will be removed from future quiz evaluations.')) return;
    
    try {
        const response = await fetch(`/api/admin/questions/${qId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Deletion failed.');
        
        loadQuestions();
        loadDashboardStats();
    } catch (error) {
        console.error('Delete question error:', error);
        alert('Failed to delete question.');
    }
}

/**
 * Open Modal - Add Mode
 */
function openAddModal() {
    modalTitle.textContent = 'Add New Question';
    editQId.value = '';
    questionForm.reset();
    
    // Setup AI panel for Generate mode
    document.getElementById('ai-generate-controls').classList.remove('hidden');
    document.getElementById('ai-modify-controls').classList.add('hidden');
    document.getElementById('ai-topic').value = '';
    document.getElementById('ai-prompt').value = '';
    document.getElementById('ai-difficulty').value = 'Intermediate';
    hideAiStatus();

    questionModal.classList.remove('hidden');
}

/**
 * Open Modal - Edit Mode
 */
function openEditModal(qId) {
    const q = questionsData.find(item => item.id === qId);
    if (!q) return;
    
    modalTitle.textContent = 'Edit Question';
    editQId.value = q.id;
    formQuestion.value = q.question;
    formTopic.value = q.topic;
    
    // Fill Options
    q.options.forEach((opt, idx) => {
        const optInput = document.getElementById(`form-opt-${idx}`);
        if (optInput) optInput.value = opt;
    });
    
    // Select correct option letter
    let correctLetter = '';
    const idx = q.options.findIndex(opt => opt.trim().toLowerCase() === q.answer.trim().toLowerCase());
    if (idx !== -1) {
        correctLetter = ['A', 'B', 'C', 'D'][idx];
    }
    
    formCorrect.value = correctLetter;
    
    // Setup AI panel for Modify mode
    document.getElementById('ai-generate-controls').classList.add('hidden');
    document.getElementById('ai-modify-controls').classList.remove('hidden');
    document.getElementById('ai-instruction').value = '';
    hideAiStatus();

    questionModal.classList.remove('hidden');
}

/**
 * Close Modal
 */
function closeModal() {
    questionModal.classList.add('hidden');
    hideAiStatus();
}

/**
 * Display AI status messages (success/error)
 */
function showAiStatus(message, type) {
    const statusBox = document.getElementById('ai-status-box');
    if (!statusBox) return;
    statusBox.textContent = message;
    statusBox.className = 'ai-status-box ' + type;
    statusBox.classList.remove('hidden');
}

function hideAiStatus() {
    const statusBox = document.getElementById('ai-status-box');
    if (!statusBox) return;
    statusBox.classList.add('hidden');
    statusBox.className = 'ai-status-box';
}

/**
 * AI Tool: Generate a new question and pre-fill form
 */
async function generateQuestionWithAI() {
    const topic = document.getElementById('ai-topic').value.trim() || 'General';
    const difficulty = document.getElementById('ai-difficulty').value;
    const prompt = document.getElementById('ai-prompt').value.trim();

    const btn = document.getElementById('btn-ai-generate');
    const spinner = document.getElementById('ai-generate-spinner');

    // Toggle loading states
    btn.disabled = true;
    spinner.classList.remove('hidden');
    hideAiStatus();

    try {
        const response = await fetch('/api/admin/ai/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, difficulty, prompt })
        });

        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.error || 'Failed to generate question with AI.');
        }

        // Fill form fields
        document.getElementById('form-question').value = result.question;
        document.getElementById('form-topic').value = result.topic;
        
        // Fill options
        if (result.options && result.options.length >= 4) {
            result.options.forEach((opt, idx) => {
                const input = document.getElementById(`form-opt-${idx}`);
                if (input) input.value = opt;
            });
        }

        // Match answer to option letter (A, B, C, D)
        const idx = result.options.findIndex(opt => opt.trim().toLowerCase() === result.answer.trim().toLowerCase());
        if (idx !== -1) {
            document.getElementById('form-correct').value = ['A', 'B', 'C', 'D'][idx];
        } else {
            document.getElementById('form-correct').value = 'A'; // fallback to first
        }

        showAiStatus('✨ Question successfully generated and pre-filled below!', 'success');
    } catch (err) {
        console.error('AI generation error:', err);
        showAiStatus('❌ ' + err.message, 'error');
    } finally {
        btn.disabled = false;
        spinner.classList.add('hidden');
    }
}

/**
 * AI Tool: Modify an existing question in the form based on instructions
 */
async function modifyQuestionWithAI() {
    const instruction = document.getElementById('ai-instruction').value.trim();
    if (!instruction) {
        alert('Please enter a modification instruction.');
        return;
    }

    const question = document.getElementById('form-question').value.trim();
    const topic = document.getElementById('form-topic').value.trim() || 'General';
    const options = [
        document.getElementById('form-opt-0').value.trim(),
        document.getElementById('form-opt-1').value.trim(),
        document.getElementById('form-opt-2').value.trim(),
        document.getElementById('form-opt-3').value.trim()
    ];

    const correctLetter = document.getElementById('form-correct').value;
    const correctIdx = ['A', 'B', 'C', 'D'].indexOf(correctLetter);
    if (correctIdx === -1) {
        alert('Please select the current correct option before modifying.');
        return;
    }
    const answer = options[correctIdx];

    const btn = document.getElementById('btn-ai-modify');
    const spinner = document.getElementById('ai-modify-spinner');

    // Toggle loading states
    btn.disabled = true;
    spinner.classList.remove('hidden');
    hideAiStatus();

    try {
        const response = await fetch('/api/admin/ai/modify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, options, answer, topic, instruction })
        });

        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.error || 'Failed to modify question with AI.');
        }

        // Fill form fields with updated values
        document.getElementById('form-question').value = result.question;
        document.getElementById('form-topic').value = result.topic;
        
        // Fill options
        if (result.options && result.options.length >= 4) {
            result.options.forEach((opt, idx) => {
                const input = document.getElementById(`form-opt-${idx}`);
                if (input) input.value = opt;
            });
        }

        // Match answer to option letter (A, B, C, D)
        const idx = result.options.findIndex(opt => opt.trim().toLowerCase() === result.answer.trim().toLowerCase());
        if (idx !== -1) {
            document.getElementById('form-correct').value = ['A', 'B', 'C', 'D'][idx];
        } else {
            document.getElementById('form-correct').value = 'A'; // fallback to first
        }

        showAiStatus('🪄 Question successfully updated by AI!', 'success');
    } catch (err) {
        console.error('AI modification error:', err);
        showAiStatus('❌ ' + err.message, 'error');
    } finally {
        btn.disabled = false;
        spinner.classList.add('hidden');
    }
}

/**
 * Save Question (Insert or Update)
 */
async function saveQuestion() {
    const qId = editQId.value;
    const isEdit = !!qId;
    
    const questionText = formQuestion.value.trim();
    const topic = formTopic.value.trim() || 'General';
    
    // Gather Options
    const options = [
        document.getElementById('form-opt-0').value.trim(),
        document.getElementById('form-opt-1').value.trim(),
        document.getElementById('form-opt-2').value.trim(),
        document.getElementById('form-opt-3').value.trim()
    ];
    
    // Map selected Correct letter (A, B, C, D) to actual Option text
    const correctLetter = formCorrect.value;
    const idx = ['A', 'B', 'C', 'D'].indexOf(correctLetter);
    if (idx === -1) {
        alert('Please select the correct option.');
        return;
    }
    const answer = options[idx];
    
    const payload = {
        question: questionText,
        topic: topic,
        options: options,
        answer: answer
    };
    
    const url = isEdit ? `/api/admin/questions/${qId}` : '/api/admin/questions';
    const method = isEdit ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Failed to save question.');
        }
        
        closeModal();
        loadQuestions();
        loadDashboardStats();
    } catch (error) {
        console.error('Save question error:', error);
        alert(error.message || 'An error occurred while saving the question.');
    }
}

/**
 * Utility to escape HTML strings to prevent XSS injection
 */
function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
