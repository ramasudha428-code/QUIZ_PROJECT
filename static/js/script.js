// Quiz State
let candidateName = '';
let userId = null;
let questions = [];
let currentIndex = 0;
let answers = {};

// DOM Elements
const welcomeCard = document.getElementById('welcome-card');
const quizCard = document.getElementById('quiz-card');
const nameInput = document.getElementById('candidate-name');
const questionCounter = document.getElementById('question-counter');
const topicTag = document.getElementById('topic-tag');
const progressBar = document.getElementById('progress-bar');
const questionText = document.getElementById('question-text');
const optionsContainer = document.getElementById('options-container');
const btnPrev = document.getElementById('btn-prev');
const btnNext = document.getElementById('btn-next');
const btnNextIcon = document.getElementById('btn-next-icon');
const submitLoader = document.getElementById('submit-loader');

/**
 * Start the quiz after validating name
 */
async function startQuiz() {
    const name = nameInput.value.trim();
    if (!name) {
        alert('Please enter your name to begin the quiz.');
        return;
    }
    
    candidateName = name;
    
    // Show spinner
    submitLoader.classList.remove('hidden');
    
    try {
        const startResponse = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name })
        });
        if (!startResponse.ok) {
            const errorData = await startResponse.json();
            throw new Error(errorData.error || 'Failed to start quiz.');
        }

        const startData = await startResponse.json();
        if (startData.status !== 'success') {
            throw new Error(startData.error || 'Quiz start failed.');
        }

        userId = startData.user_id || null;

        const response = await fetch('/api/questions');
        if (!response.ok) {
            throw new Error('Failed to retrieve quiz questions.');
        }
        
        questions = await response.json();
        
        if (questions.length === 0) {
            alert('No questions available in the database.');
            submitLoader.classList.add('hidden');
            return;
        }
        
        // Hide loader
        submitLoader.classList.add('hidden');
        
        // Switch screens with transition
        welcomeCard.classList.add('hidden');
        quizCard.classList.remove('hidden');
        quizCard.classList.add('fade-in');
        
        // Load first question
        currentIndex = 0;
        loadQuestion(currentIndex);
        
    } catch (error) {
        console.error(error);
        alert('An error occurred while starting the quiz. Please try again.');
        submitLoader.classList.add('hidden');
    }
}

/**
 * Render question at specified index
 */
function loadQuestion(index) {
    const q = questions[index];
    
    // Update labels
    questionCounter.textContent = `Question ${index + 1} of ${questions.length}`;
    topicTag.textContent = q.topic || 'General';
    
    // Update progress bar
    const progressPercent = ((index + 1) / questions.length) * 100;
    progressBar.style.width = `${progressPercent}%`;
    
    // Set question text
    questionText.textContent = q.question;
    
    // Clear and build options
    optionsContainer.innerHTML = '';
    const letters = ['A', 'B', 'C', 'D'];
    
    q.options.forEach((option, idx) => {
        const optionLetter = letters[idx] || (idx + 1).toString();
        const optionCard = document.createElement('button');
        optionCard.type = 'button';
        optionCard.className = 'option-card';
        optionCard.id = `option-${idx}`;
        
        // Highlight if already selected
        if (answers[q.id] === option) {
            optionCard.classList.add('selected');
        }
        
        optionCard.innerHTML = `
            <span class="option-letter">${optionLetter}</span>
            <span class="option-text">${escapeHtml(option)}</span>
        `;
        
        optionCard.addEventListener('click', () => {
            selectOption(q.id, option, optionCard);
        });
        
        optionsContainer.appendChild(optionCard);
    });
    
    // Enable/Disable Back button
    btnPrev.disabled = index === 0;
    
    // Update Next/Submit button design
    if (index === questions.length - 1) {
        btnNext.className = 'btn btn-primary btn-submit-ready';
        btnNext.querySelector('span').textContent = 'Submit Quiz';
        btnNextIcon.innerHTML = `
            <polyline points="20 6 9 17 4 12"></polyline>
        `;
    } else {
        btnNext.className = 'btn btn-primary';
        btnNext.querySelector('span').textContent = 'Next';
        btnNextIcon.innerHTML = `
            <line x1="5" y1="12" x2="19" y2="12"></line>
            <polyline points="12 5 19 12 12 19"></polyline>
        `;
    }
}

/**
 * Handle option selection
 */
function selectOption(qId, selectedText, selectedCard) {
    // Save answer
    answers[qId] = selectedText;
    
    // Update UI selected classes
    const siblings = optionsContainer.querySelectorAll('.option-card');
    siblings.forEach(card => card.classList.remove('selected'));
    selectedCard.classList.add('selected');
    
    // Micro-animation: subtle pop scale
    selectedCard.style.transform = 'scale(0.98)';
    setTimeout(() => {
        selectedCard.style.transform = '';
    }, 100);
}

/**
 * Navigate to next question or submit quiz
 */
function nextQuestion() {
    // If not answered, prompt user warning but allow navigation
    const currentQuestion = questions[currentIndex];
    if (!answers[currentQuestion.id]) {
        if (!confirm('You have not selected an answer for this question. Do you want to continue?')) {
            return;
        }
        answers[currentQuestion.id] = ''; // Store empty answer
    }

    if (currentIndex < questions.length - 1) {
        currentIndex++;
        loadQuestion(currentIndex);
    } else {
        submitQuiz();
    }
}

/**
 * Navigate to previous question
 */
function prevQuestion() {
    if (currentIndex > 0) {
        currentIndex--;
        loadQuestion(currentIndex);
    }
}

/**
 * Submit answers to API and redirect
 */
async function submitQuiz() {
    // Check if there are unanswered questions
    const unansweredCount = questions.filter(q => !answers[q.id]).length;
    if (unansweredCount > 0) {
        if (!confirm(`You have left ${unansweredCount} questions unanswered. Submit anyway?`)) {
            return;
        }
    }
    
    // Show loading overlay
    submitLoader.classList.remove('hidden');
    
    try {
        const response = await fetch('/api/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: candidateName,
                user_id: userId,
                answers: answers
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit quiz.');
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Redirect to results template page
            window.location.href = `/result/${data.result_id}`;
        } else {
            alert('Error: ' + (data.error || 'Submission failed.'));
            submitLoader.classList.add('hidden');
        }
        
    } catch (error) {
        console.error(error);
        alert('An error occurred during submission. Please try again.');
        submitLoader.classList.add('hidden');
    }
}

/**
 * Utility to escape HTML strings
 */
function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
