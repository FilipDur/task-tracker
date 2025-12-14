import threading
import time

class CLIInterface:
    
    def __init__(self, task_manager):
        self.manager = task_manager
        self.running = True
    
    def show_menu(self):
        print("\n" + "="*50)
        print("📋 HLAVNÍ MENU")
        print("="*50)
        print("1. Přidat úkol")
        print("2. Zobrazit všechny úkoly")
        print("3. Zobrazit čekající úkoly")
        print("4. Označit úkol jako hotový")
        print("5. Smazat úkol")
        print("6. Statistiky")
        print("7. Export do JSON")
        print("8. Ukázat běžící vlákna")
        print("9. Konec")
        print("="*50)
    
    def add_task_dialog(self):
        print("\n➕ PŘIDAT ÚKOL")
        name = input("Název úkolu: ").strip()
        
        if not name:
            print("❌ Název nesmí být prázdný!")
            return
        
        print("\nVyber prioritu:")
        print("1. 🔴 Vysoká")
        print("2. 🟡 Střední")
        print("3. 🔵 Nízká")
        
        choice = input("Tvá volba (1-3, enter=střední): ").strip()
        
        if choice == "1":
            priority = "vysoká"
        elif choice == "3":
            priority = "nízká"
        else:
            priority = "střední"
        
        task = self.manager.add_task(name, priority)
        print(f"✅ Úkol přidán (ID: {task.id})")
    
    def show_tasks(self, only_pending=False):
        tasks = self.manager.get_all_tasks()
        
        if not tasks:
            print("\n📭 Žádné úkoly")
            return
        
        if only_pending:
            tasks = [t for t in tasks if not t.completed]
            title = "⏳ CEKAJÍCÍ ÚKOLY"
        else:
            title = "📋 VŠECHNY ÚKOLY"
        
        print(f"\n{title}")
        print("-"*50)
        
        for task in tasks:
            status = "✅" if task.completed else "⭕"
            priority_icon = "🔴" if task.priority.value == "vysoká" else \
                           "🟡" if task.priority.value == "střední" else "🔵"
            
            print(f"{task.id:3}. {status} {priority_icon} {task.name}")
            print(f"     Vytvořeno: {task.created}")
            if task.completed:
                print(f"     Dokončeno: {task.completed_at}")
            print()
    
    def complete_task_dialog(self):
        self.show_tasks(only_pending=True)
        
        try:
            task_id = int(input("\nID úkolu k dokončení: "))
            if self.manager.complete_task(task_id):
                print(f"✅ Úkol {task_id} dokončen!")
            else:
                print(f"❌ Úkol {task_id} nenalezen!")
        except ValueError:
            print("❌ Zadej číslo!")
    
    def delete_task_dialog(self):
        self.show_tasks()
        
        try:
            task_id = int(input("\nID úkolu ke smazání: "))
            if self.manager.delete_task(task_id):
                print(f"🗑️ Úkol {task_id} smazán!")
            else:
                print(f"❌ Úkol {task_id} nenalezen!")
        except ValueError:
            print("❌ Zadej číslo!")
    
    def show_stats(self):
        stats = self.manager.get_stats()
        
        print("\n📊 STATISTIKY")
        print("="*30)
        print(f"Celkem úkolů: {stats['total']}")
        print(f"Dokončených: {stats['completed']}")
        print(f"Čekajících: {stats['pending']}")
        
        if stats['total'] > 0:
            percent = stats['completed'] / stats['total'] * 100
            print(f"Procento dokončení: {percent:.1f}%")
        
        print("\n🔸 Podle priority:")
        for prio, count in stats['priorities'].items():
            icon = "🔴" if prio == "vysoká" else "🟡" if prio == "střední" else "🔵"
            print(f"   {icon} {prio}: {count}")
    
    def export_dialog(self):
        filename = input("\nNázev souboru pro export (např. backup.json): ").strip()
        if not filename.endswith('.json'):
            filename += '.json'
        
        thread = self.manager.export_to_json(filename)
        print(f"🔄 Export spuštěn ve vlákně: {thread.name}")
        print("   (můžeš pokračovat v práci)")
    
    def show_threads(self):
        print("\n🧵 BĚŽÍCÍ VLÁKNA")
        print("="*30)
        
        threads = threading.enumerate()
        for i, thread in enumerate(threads, 1):
            status = "🟢" if thread.is_alive() else "🔴"
            print(f"{i}. {status} {thread.name} (daemon: {thread.daemon})")
        
        print(f"\nCelkem: {len(threads)} vláken")
    
    def run(self):
        print("\n🎮 Ovládání: Stačí zadat číslo 1-9")
        
        while self.running:
            self.show_menu()
            
            try:
                choice = input("\nTvá volba: ").strip()
                
                if choice == "1":
                    self.add_task_dialog()
                elif choice == "2":
                    self.show_tasks()
                elif choice == "3":
                    self.show_tasks(only_pending=True)
                elif choice == "4":
                    self.complete_task_dialog()
                elif choice == "5":
                    self.delete_task_dialog()
                elif choice == "6":
                    self.show_stats()
                elif choice == "7":
                    self.export_dialog()
                elif choice == "8":
                    self.show_threads()
                elif choice == "9":
                    print("\n👋 Ukončuji program...")
                    self.manager.stop()
                    self.running = False
                else:
                    print("❌ Zadej číslo 1-9!")
            
            except KeyboardInterrupt:
                print("\n\n⚠️  Přerušeno uživatelem")
                self.manager.stop()
                break
            except Exception as e:
                print(f"❌ Chyba: {e}")