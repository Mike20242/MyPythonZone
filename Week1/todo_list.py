def show_tasks(tasks):
    if not tasks:
        print("Your todo list is empty.")
    else:
        print("\n=== Todo List ===")
        for index, task in enumerate(tasks, start=1):
            print(f"{index}. {task}")
        print("=================")

def add_task(tasks):
    task = input("Enter task description: ")
    if task.strip():
        tasks.append(task)
        print("Task added.")
    else:
        print("Task cannot be empty.")

def remove_task(tasks):
    show_tasks(tasks)
    if not tasks:
        return
    
    try:
        task_num = int(input("Enter number of task to remove: "))
        if 1 <= task_num <= len(tasks):
            removed = tasks.pop(task_num - 1)
            print(f"Task '{removed}' removed.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")

def main():
    tasks = []
    while True:
        print("\n--- Todo List Menu ---")
        print("1. Show Tasks")
        print("2. Add Task")
        print("3. Remove Task")
        print("4. Exit")
        
        choice = input("Choose an option (1-4): ")
        
        if choice == '1':
            show_tasks(tasks)
        elif choice == '2':
            add_task(tasks)
        elif choice == '3':
            remove_task(tasks)
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
