# task_module.py

def add_task(task_name, task_list):
    if not task_name:
        raise ValueError("Task name is required")


    # if any(task["name"] == task_name for task in task_list):
    #     raise ValueError(f"Task with name '{task_name}' already exists.")


    new_task = {
        "id": len(task_list) + 1,
        "name": task_name,
        "completed": False
    }
    task_list.append(new_task)
    return new_task


if __name__ == "__main__":
    print("--- Simple Task Management Application ---")
    print("Enter 'show' to view tasks, 'exit' to quit.")

    my_tasks = []

    while True:
        user_input = input("\nEnter task name to add: ").strip()  # .strip() removes leading/trailing whitespace

        if user_input.lower() == 'exit':
            print("Thank you for using the Task Management App. Goodbye!")
            break
        elif user_input.lower() == 'show':
            print("\n--- Your Task List ---")
            if not my_tasks:
                print("Your task list is empty.")
            else:
                for task in my_tasks:
                    status = "Completed" if task["completed"] else "Pending"
                    print(f"ID: {task['id']}, Name: {task['name']}, Status: {status}")
            continue

        try:
            added_task = add_task(user_input, my_tasks)
            print(f"✓ Successfully added task:  '{added_task['name']}'.")
        except ValueError as e:
            print(f"✗ Input error: {e}")

