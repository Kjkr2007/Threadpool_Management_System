let queue = [];
let active = [];
let completed = [];
let maxThreads = 3;

function updateUI() {
    document.getElementById("queue").innerHTML =
        queue.map(t => `<li>${t}</li>`).join("");

    document.getElementById("threads").innerHTML =
        active.map(t => `<li>Running ${t}</li>`).join("");

    document.getElementById("completed").innerHTML =
        completed.map(t => `<li>${t}</li>`).join("");
}

function addTask() {
    let task = document.getElementById("taskInput").value;
    if(task === "") return;

    queue.push(task);
    document.getElementById("taskInput").value = "";

    processTasks();
    updateUI();
}

function processTasks() {
    while(active.length < maxThreads && queue.length > 0) {

        let task = queue.shift();

        // 🔥 If task is 2 → force delay in queue
        if(task == 2 && active.length > 0) {
            queue.unshift(task); // put back in queue
            return;
        }

        let time = 10; // fixed 10 seconds

        active.push(`Thread ${active.length + 1}: Task ${task} (10s)`);

        updateUI();

        setTimeout(() => {
            active = active.filter(t => !t.includes(task));
            completed.push(task);
            processTasks();
            updateUI();
        }, time * 1000);
    }
}