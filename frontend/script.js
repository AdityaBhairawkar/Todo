const todoInput = document.getElementById('todoInput');
const addBtn = document.getElementById('addTodoBtn');
const todoList = document.getElementById('todoList');

let todos = [];

// Render todos
function render() {
    todoList.innerHTML = '';
    todos.forEach(t => {
        const li = document.createElement('li');
        li.innerHTML = `
            <input type="checkbox" ${t.completed ? 'checked' : ''}/>
            ${t.text}
            <button>Delete</button>
        `;
        const checkbox = li.querySelector('input');
        const deleteBtn = li.querySelector('button');

        checkbox.addEventListener('change', () => toggleTodo(t.id, !t.completed));
        deleteBtn.addEventListener('click', () => deleteTodo(t.id));

        todoList.appendChild(li);
    });
}

// API calls
function fetchTodos() {
    fetch(`${API_URL}`)
        .then(res => res.json())
        .then(data => { todos = data; render(); });
}

function addTodo() {
    const text = todoInput.value.trim();
    if (!text) return;
    fetch(`${API_URL}`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({text, completed:false})
    })
    .then(res => res.json())
    .then(todo => { todos.unshift(todo); render(); todoInput.value=''; });
}

function toggleTodo(id, completed) {
    fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({completed})
    }).then(() => fetchTodos());
}

function deleteTodo(id) {
    fetch(`${API_URL}/${id}`, { method: 'DELETE' })
    .then(() => fetchTodos());
}

// Event listeners
addBtn.addEventListener('click', addTodo);
todoInput.addEventListener('keypress', e => { if(e.key==='Enter') addTodo(); });

// Initial load
fetchTodos();
