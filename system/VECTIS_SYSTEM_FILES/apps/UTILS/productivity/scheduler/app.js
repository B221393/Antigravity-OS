document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const recordBtn = document.getElementById('recordBtn');
    const voiceStatus = document.getElementById('voiceStatus');
    const visualizer = document.getElementById('visualizer');
    const taskList = document.getElementById('taskList');
    const taskCountEl = document.getElementById('taskCount');
    const doneCountEl = document.getElementById('doneCount');
    const clearDoneBtn = document.getElementById('clearDoneBtn');
    const clockEl = document.getElementById('clock');
    const celebrationOverlay = document.getElementById('celebration');

    // State
    let tasks = JSON.parse(localStorage.getItem('vectis_tasks')) || [];

    // --- CLOCK ---
    function updateClock() {
        const now = new Date();
        clockEl.textContent = now.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
    }
    setInterval(updateClock, 1000);
    updateClock();

    // --- RENDER TASKS ---
    function renderTasks() {
        taskList.innerHTML = '';
        let activeCount = 0;
        let completedCount = 0;

        tasks.forEach((task, index) => {
            const li = document.createElement('li');
            li.className = `task-item ${task.completed ? 'completed' : ''}`;
            li.innerHTML = `
                <span class="task-text">${task.text}</span>
                <div class="task-actions">
                    <button class="check-btn" onclick="toggleTask(${index})">
                        <i class="fas fa-check"></i>
                    </button>
                </div>
            `;

            // Delete on long press or swipe (simulated by delete button for now? No, stick to MVP)
            // Ideally, add a delete small button if needed. 
            // For now, "Done" is the main satisfaction. 

            taskList.appendChild(li);

            if (task.completed) completedCount++;
            else activeCount++;
        });

        taskCountEl.textContent = activeCount;
        doneCountEl.textContent = completedCount;

        localStorage.setItem('vectis_tasks', JSON.stringify(tasks));
    }

    // --- ACTIONS ---
    window.toggleTask = (index) => {
        tasks[index].completed = !tasks[index].completed;
        renderTasks();

        if (tasks[index].completed) {
            triggerCelebration();
        }
    };

    function addTask(text) {
        if (!text) return;
        tasks.unshift({ text: text, completed: false, timestamp: Date.now() });
        renderTasks();
    }

    clearDoneBtn.addEventListener('click', () => {
        if (confirm("Clear completed missions?")) {
            tasks = tasks.filter(t => !t.completed);
            renderTasks();
        }
    });

    // --- VOICE INPUT ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.lang = 'ja-JP';
        recognition.continuous = false;
        recognition.interimResults = false;

        recordBtn.addEventListener('click', () => {
            recognition.start();
        });

        recognition.onstart = () => {
            voiceStatus.textContent = "🔴 聞いてます...";
            recordBtn.classList.add('listening');
            visualizer.classList.add('active');
        };

        recognition.onend = () => {
            voiceStatus.textContent = "🎙️ タップで音声入力";
            recordBtn.classList.remove('listening');
            visualizer.classList.remove('active');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            voiceStatus.textContent = "✨ 追加中...";
            setTimeout(() => {
                addTask(transcript);
                voiceStatus.textContent = "✅ " + transcript;
                setTimeout(() => { voiceStatus.textContent = "🎙️ タップで音声入力"; }, 2000);
            }, 500);
        };
    } else {
        voiceStatus.textContent = "音声入力非対応";
        recordBtn.disabled = true;
    }

    // --- CELEBRATION ---
    function triggerCelebration() {
        celebrationOverlay.classList.add('active');

        // Simple confetti logic could go here or just the overlay text
        setTimeout(() => {
            celebrationOverlay.classList.remove('active');
        }, 2000);
    }

    // Initial Render
    renderTasks();
});
