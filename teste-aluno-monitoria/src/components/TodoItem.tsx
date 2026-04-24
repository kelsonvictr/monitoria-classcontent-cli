import { Task } from '../types'

// Componente que renderiza um item da lista
// TODO: adicionar botão de deletar

type TodoItemProps = {
  task: Task
  onToggle: (id: number) => void
}

function TodoItem({ task, onToggle }: TodoItemProps) {
  return (
    <li
      className="flex items-center gap-3 p-3 bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-700"
      onClick={() => onToggle(task.id)}
    >
      <input
        type="checkbox"
        checked={task.completed}
        onChange={() => onToggle(task.id)}
        className="w-5 h-5 accent-violet-500"
      />
      <span className={task.completed ? 'line-through text-gray-500' : 'text-white'}>
        {task.title}
      </span>
    </li>
  )
}

export default TodoItem
