const API_BASE = "http://127.0.0.1:8000/api"; // Adjust if needed

function switchTab(tabId) {
    // Buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(tabId === 'generate' ? 'tab-gen' : 'tab-hist').classList.add('active');

    // Content
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(tabId === 'generate' ? 'generate-section' : 'history-section').classList.add('active');

    if (tabId === 'history') {
        loadHistory();
    }
}

async function generateQuiz() {
    const urlInput = document.getElementById('wiki-url');
    // Split by newlines and filter empty strings
    const urls = urlInput.value.split('\n').map(u => u.trim()).filter(u => u.length > 0);

    if (urls.length === 0) {
        showError("Please enter at least one valid URL");
        return;
    }

    // Reset UI
    document.getElementById('quiz-result').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('error-msg').classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ urls: urls }) // Send as list
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        const data = await response.json();
        renderQuiz(data, 'quiz-result');
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('quiz-result').classList.remove('hidden');

    } catch (err) {
        document.getElementById('loading').classList.add('hidden');
        showError(err.message);
    }
}


// --- Interactive Quiz Logic ---

function renderQuiz(data, containerId) {
    const container = document.getElementById(containerId);

    // Summary
    const titleEl = container.querySelector('#article-title') || document.getElementById('article-title');
    const summaryEl = container.querySelector('#article-summary') || document.getElementById('article-summary');
    const entitiesEl = container.querySelector('#key-entities') || document.getElementById('key-entities');
    const questionsEl = container.querySelector('#questions-container') || document.getElementById('questions-container');
    const topicsEl = container.querySelector('#related-topics') || document.getElementById('related-topics');

    // Reset Score State for this container
    if (questionsEl) {
        questionsEl.dataset.total = data.quiz.length;
        questionsEl.dataset.correct = 0;
        questionsEl.dataset.attempted = 0;

        // Remove existing score card if any
        const existingScore = container.querySelector('.score-card');
        if (existingScore) existingScore.remove();

        const scoreCard = document.createElement('div');
        scoreCard.className = 'card score-card hidden';
        scoreCard.innerHTML = `<h3>Quiz Score: <span id="score-val-${containerId}">0</span> / ${data.quiz.length}</h3>`;

        // Insert after summary or title
        const insertAnchor = summaryEl || titleEl;
        if (insertAnchor && insertAnchor.parentNode) {
            insertAnchor.parentNode.after(scoreCard);
        }
    }

    if (titleEl) titleEl.innerText = data.title;
    if (summaryEl) summaryEl.innerText = data.summary;

    if (entitiesEl) {
        entitiesEl.innerHTML = '';
        const allEntities = [
            ...(data.key_entities.people || []),
            ...(data.key_entities.organizations || []),
            ...(data.key_entities.locations || [])
        ];
        allEntities.forEach(ent => {
            const span = document.createElement('span');
            span.innerText = ent;
            entitiesEl.appendChild(span);
        });
    }

    if (questionsEl) {
        questionsEl.innerHTML = '';
        data.quiz.forEach((q, index) => {
            const qCard = document.createElement('div');
            qCard.className = 'card question-card';

            const diffClass = `diff-${q.difficulty.toLowerCase()}`;

            // Escape quotes for checkAnswer arguments
            const safeAnswer = q.answer.replace(/'/g, "\\'").replace(/"/g, "&quot;");

            const optionsHtml = q.options.map((opt, i) => {
                const safeOpt = opt.replace(/'/g, "\\'").replace(/"/g, "&quot;");
                return `<li class="option-item" onclick="checkAnswer(this, '${safeOpt}', '${safeAnswer}', 'answer-${index}-${containerId}', '${containerId}')">${opt}</li>`;
            }).join('');

            qCard.innerHTML = `
                <div class="header" style="overflow:auto;">
                    <span class="difficulty ${diffClass}">${q.difficulty}</span>
                </div>
                <div class="question-text">Q${index + 1}: ${q.question}</div>
                <ul class="options-list">
                    ${optionsHtml}
                </ul>
                <div class="answer-section hidden" id="answer-${index}-${containerId}">
                    <span class="correct-answer">Answer: ${q.answer}</span>
                    <p class="explanation">${q.explanation}</p>
                </div>
            `;
            questionsEl.appendChild(qCard);
        });
    }

    if (topicsEl) {
        topicsEl.innerHTML = '';
        data.related_topics.forEach(topic => {
            const li = document.createElement('li');
            li.innerText = topic;
            topicsEl.appendChild(li);
        });
    }
}

function checkAnswer(element, selected, correct, answerId, containerId) {
    // If already clicked (sibling has class disabled? or parent has class answered?)
    if (element.parentNode.classList.contains('answered')) return;

    const optionsList = element.parentNode;
    optionsList.classList.add('answered'); // Mark question as answered

    // Disable all options
    Array.from(optionsList.children).forEach(li => li.classList.add('disabled'));

    // Check Logic
    if (selected === correct) {
        element.classList.add('selected-correct');
        updateScore(containerId, 1);
    } else {
        element.classList.add('selected-wrong');
        // Highlight correct one
        Array.from(optionsList.children).forEach(li => {
            if (li.innerText === correct) {
                li.classList.add('correct-highlight');
            }
        });
        updateScore(containerId, 0);
    }
    // Reveal Answer
    document.getElementById(answerId).classList.remove('hidden');
}

function updateScore(containerId, isCorrect) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // For main interface or modal, we know where questions are
    let qContainer = container.querySelector('#questions-container') || document.getElementById('modal-questions');

    if (!qContainer) return;

    let correct = parseInt(qContainer.dataset.correct || 0);
    let attempted = parseInt(qContainer.dataset.attempted || 0);

    attempted++;
    if (isCorrect) correct++;

    qContainer.dataset.correct = correct;
    qContainer.dataset.attempted = attempted;

    // Update Display
    const scoreVal = document.getElementById(`score-val-${containerId}`);
    if (scoreVal) scoreVal.innerText = correct;

    // Show score card if hidden
    const scoreCard = container.querySelector('.score-card');
    if (scoreCard) scoreCard.classList.remove('hidden');
}

// --- History & Modal Logic ---

async function loadHistory() {
    const tbody = document.querySelector('#history-table tbody');
    tbody.innerHTML = '<tr><td colspan="4">Loading...</td></tr>';

    try {
        const response = await fetch(`${API_BASE}/history`);
        const history = await response.json();

        tbody.innerHTML = '';
        if (history.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4">No history found.</td></tr>';
            return;
        }

        history.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item.id}</td>
                <td><a href="${item.url}" target="_blank">${item.title}</a></td>
                <td>${new Date(item.created_at).toLocaleString()}</td>
                <td><button class="view-btn" onclick="openDetails(${item.id})">Details</button></td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4" class="error">Failed to load history: ${err.message}</td></tr>`;
    }
}

async function openDetails(id) {
    try {
        const response = await fetch(`${API_BASE}/quiz/${id}`);
        const data = await response.json();

        const modalBody = document.getElementById('modal-body');
        modalBody.innerHTML = `
            <div class="card summary-card">
                <h2 id="modal-title"></h2>
                <p id="modal-summary"></p>
                <div class="tags" id="modal-entities"></div>
            </div>
            <div id="modal-questions"></div>
            <div class="card related-card">
                <h3>Related Topics</h3>
                <ul id="modal-topics"></ul>
            </div>
        `;

        // Use the unified renderer, targeting the specific IDs we just created in the modal
        // Note: renderQuiz expects a containerId, but here we can just pass the modal-body ID
        // However, our renderQuiz looks for specific IDs *anywhere* in the container. 
        // We need to adhere to the renderQuiz contract.

        // Actually, renderQuiz uses querySelector on container.
        // So we can pass 'modal-body' as containerId.
        // But we need to ensure the IDs inside modalBody mimic the main page or we update renderQuiz to handle classes.

        // HACK: To save lines, we manually set text here as before, OR we ensure renderQuiz works.
        // renderQuiz checks for #key-entities etc. 
        // in openDetails, we used id="modal-entities".
        // Let's just fix the IDs in the modalBody HTML above to match what renderQuiz expects, 
        // but wait, IDs must be unique. If we have duplicate IDs (one in hidden tab, one in modal), querySelector might fail?
        // querySelector on container finds the *first* match inside container.
        // getElementById finds global unique.

        // Let's use the manual population for safety, adapted to new interactive logic.

        document.getElementById('modal-title').innerText = data.title;
        document.getElementById('modal-summary').innerText = data.summary;

        const entEl = document.getElementById('modal-entities');
        const allEntities = [
            ...(data.key_entities.people || []),
            ...(data.key_entities.organizations || []),
            ...(data.key_entities.locations || [])
        ];
        allEntities.forEach(ent => {
            const span = document.createElement('span');
            span.innerText = ent;
            entEl.appendChild(span);
        });

        // Questions with Interaction
        const qContainer = document.getElementById('modal-questions');
        // Reset score logic for modal
        qContainer.dataset.total = data.quiz.length;
        qContainer.dataset.correct = 0;
        qContainer.dataset.attempted = 0;

        // Add score card to modal
        const existingScore = document.getElementById('modal-score-card');
        if (existingScore) existingScore.remove();

        const scoreCard = document.createElement('div');
        scoreCard.id = 'modal-score-card';
        scoreCard.className = 'card score-card hidden';
        scoreCard.innerHTML = `<h3>Quiz Score: <span id="score-val-modal-body">0</span> / ${data.quiz.length}</h3>`;
        document.querySelector('#modal-entities').parentNode.after(scoreCard);

        data.quiz.forEach((q, index) => {
            const qCard = document.createElement('div');
            qCard.className = 'card question-card';
            const diffClass = `diff-${q.difficulty.toLowerCase()}`;
            // Escape quotes for checkAnswer arguments
            const safeAnswer = q.answer.replace(/'/g, "\\'").replace(/"/g, "&quot;");

            const optionsHtml = q.options.map((opt, i) => {
                const safeOpt = opt.replace(/'/g, "\\'").replace(/"/g, "&quot;");
                // Pass 'modal-body' as containerId
                return `<li class="option-item" onclick="checkAnswer(this, '${safeOpt}', '${safeAnswer}', 'modal-answer-${index}', 'modal-body')">${opt}</li>`;
            }).join('');

            qCard.innerHTML = `
                <div class="header">
                    <span class="difficulty ${diffClass}">${q.difficulty}</span>
                </div>
                <div class="question-text">Q${index + 1}: ${q.question}</div>
                <ul class="options-list">
                    ${optionsHtml}
                </ul>
                <div class="answer-section hidden" id="modal-answer-${index}">
                    <span class="correct-answer">Answer: ${q.answer}</span>
                    <p class="explanation">${q.explanation}</p>
                </div>
            `;
            qContainer.appendChild(qCard);
        });

        const topicEl = document.getElementById('modal-topics');
        data.related_topics.forEach(topic => {
            const li = document.createElement('li');
            li.innerText = topic;
            topicEl.appendChild(li);
        });

        document.getElementById('details-modal').classList.remove('hidden');

    } catch (err) {
        alert("Failed to load details: " + err.message);
    }
}

function closeModal() {
    document.getElementById('details-modal').classList.add('hidden');
}

function showError(msg) {
    const el = document.getElementById('error-msg');
    el.innerText = msg;
    el.classList.remove('hidden');
}

// --- Dark Mode Logic ---
// --- Dark Mode Logic ---
document.addEventListener('DOMContentLoaded', () => {
    console.log("Initializing Dark Mode Logic...");
    const themeBtn = document.getElementById('theme-toggle');
    const body = document.body;

    // Check Local Storage
    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-mode');
        if (themeBtn) themeBtn.innerText = '☀️';
    }

    if (themeBtn) {
        themeBtn.addEventListener('click', (e) => {
            console.log("Theme toggle clicked!");

            // 1. Get Geometry
            const rect = themeBtn.getBoundingClientRect();
            const x = rect.left + rect.width / 2;
            const y = rect.top + rect.height / 2;

            // 2. Setup Overlay
            const overlay = document.getElementById('theme-transition');
            // Determine target color based on CURRENT state (we are about to switch)
            const isCurrentlyDark = body.classList.contains('dark-mode');
            const targetColor = isCurrentlyDark ? '#f3f4f6' : '#111827'; // Light Gray or Dark Blue

            overlay.style.backgroundColor = targetColor;
            overlay.style.left = `${x}px`; // Center on button
            overlay.style.top = `${y}px`;
            overlay.style.width = '10px';
            overlay.style.height = '10px';
            overlay.style.transform = 'translate(-50%, -50%) scale(0)';
            overlay.style.borderRadius = '50%';
            overlay.style.position = 'fixed';

            // Calculate scale needed to cover screen
            // Max distance to corner
            const maxDist = Math.max(x, window.innerWidth - x) ** 2 + Math.max(y, window.innerHeight - y) ** 2;
            const radius = Math.sqrt(maxDist);
            const scale = (radius * 2) / 10; // 10 is initial width

            // 3. Animate
            // Force reflow
            void overlay.offsetWidth;

            overlay.style.transition = 'transform 0.5s ease-in-out';
            overlay.style.transform = `translate(-50%, -50%) scale(${scale})`;

            // 4. On Finish
            // We wait for transition to end, THEN toggle class and reset overlay.
            // Actually, to make it seamless: 
            // - Overlay covers screen.
            // - We swap body class behind it.
            // - We fade out overlay? No, we just hide it because body is now same color.

            setTimeout(() => {
                body.classList.toggle('dark-mode');
                const isDark = body.classList.contains('dark-mode');
                themeBtn.innerText = isDark ? '☀️' : '🌙';
                localStorage.setItem('theme', isDark ? 'dark' : 'light');

                // Hide overlay instantly (it matches the bg now)
                overlay.style.transition = 'none';
                overlay.style.transform = 'translate(-50%, -50%) scale(0)';
            }, 500); // 500ms matches css transition
        });
    } else {
        console.error("Theme toggle button not found!");
    }
});
