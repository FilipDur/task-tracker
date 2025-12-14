import os
import json
from task_manager import TaskManager
from cli_interface import CLIInterface

def main():
    print("=" * 50)
    print("🎯 TASK TRACKER S VLÁKNY")
    print("=" * 50)
    print("Ukládá data do JSON, práce s vlákny, statistiky")
    print()
    
    if not os.path.exists("tasks.json"):
        with open("tasks.json", "w", encoding="utf-8") as f:
            json.dump({"tasks": []}, f, indent=2)
        print("✅ Vytvořen nový tasks.json soubor")
    
    manager = TaskManager()
    
    interface = CLIInterface(manager)
    interface.run()
    
    print("\n👋 Program ukončen. Data uložena v tasks.json")

if __name__ == "__main__":
    main()