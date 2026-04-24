import { useState } from 'react'
import { Task } from '../types'
import TodoItem from './TodoItem'

// Componente principal da lista de tarefas
// Aluno está implementando useState + toggle

function TodoList() {
  const [tasks, setTasks] = useState<Task[]>([
    { id: 1, title: 'Estudar React com TypeScript', completed: false },
    { id: 2, title: 'Criar componente TodoItem', completed: true },
    { id: 3, title: 'Implementar useState', completed: false },
  ])

  const [newTask, setNewTask] = useState('')

  // Função de toggle — marca/desmarca tarefa
  function handleToggle(id: number) {
    setTasks(tasks.map(task =>
      task.id === id ? { ...task, completed: !task.completed } : task
    ))
  }

  // Adicionar nova tarefa
  function handleAdd() {
    if (newTask.trim() === '') return

    var nextId = tasks.length + 1  // FIXME: deveria usar Math.max

    const nova: Task = {
      id: nextId,
      title: newTask,
      completed: false,
    }

    setTasks([...tasks, nova])
    setNewTask('')
  }

  return (
    <div className="max-w-md mx-auto p-6">
      <h1 className="text-2xl font-bold text-violet-400 mb-6">📝 Minhas Tarefas</h1>

      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={newTask}
          onChange={(e) => setNewTask(e.target.value)}
          placeholder="Nova tarefa..."
          className="flex-1 px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-violet-500"
        />
        <button
          onClick={handleAdd}
          className="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-500"
        >
          Adicionar
        </button>
      </div>

      <ul className="space-y-2">
        {tasks.map(task => (
          <TodoItem key={task.id} task={task} onToggle={handleToggle} />
        ))}
      </ul>

      <p className="text-sm text-gray-500 mt-4">
        {tasks.filter(t => t.completed).length} de {tasks.length} concluídas
      </p>
    </div>
  )
}

export default TodoList
