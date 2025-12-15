import json
import threading
import time
from datetime import datetime
from enum import Enum
from queue import Queue

class Priority(Enum):
    LOW = "nízká"
    MEDIUM = "střední"
    HIGH = "vysoká"

class Task:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.created = datetime.now().strftime("%d.%m.%Y %H:%M")
        self.completed = False
        self.completed_at = None
        self.priority = Priority.MEDIUM
        self.time_spent = 0
    
    def mark_completed(self):
        self.completed = True
        self.completed_at = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created': self.created,
            'completed': self.completed,
            'completed_at': self.completed_at,
            'priority': self.priority.value,
            'time_spent': self.time_spent
        }
    
    @classmethod
    def from_dict(cls, data):
        task = cls(data['id'], data['name'])
        task.created = data['created']
        task.completed = data['completed']
        task.completed_at = data['completed_at']
        task.priority = Priority(data['priority'])
        task.time_spent = data['time_spent']
        return task

class TaskManager:
    
    def __init__(self):
        self.tasks = []
        self.next_id = 1
        self.data_file = "tasks.json"
        
        self.lock = threading.Lock()
        self.save_queue = Queue()
        self.stop_event = threading.Event()
        
        self.load_tasks()
        
        self.auto_save_thread = threading.Thread(
            target=self._auto_save_worker,
            daemon=True
        )
        self.auto_save_thread.start()
        
        self.stats_thread = threading.Thread(
            target=self._stats_worker,
            daemon=True
        )
        self.stats_thread.start()
        
        print(f"✅ TaskManager inicializován, {len(self.tasks)} úkolů načteno")
        print("   Vlákna spuštěna: auto-save, statistics")
    
    def load_tasks(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                with self.lock:
                    self.tasks = [Task.from_dict(t) for t in data['tasks']]
                    if self.tasks:
                        self.next_id = max(t.id for t in self.tasks) + 1
        except (FileNotFoundError, json.JSONDecodeError):
            with self.lock:
                self.tasks = []
    
    def save_tasks(self):
        with self.lock:
            data = {
                'tasks': [t.to_dict() for t in self.tasks],
                'last_save': datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            }
            
        self.save_queue.put(data)
    
    def _auto_save_worker(self):
        print("   🧵 Auto-save vlákno: spuštěno")
        
        while not self.stop_event.is_set():
            try:
                data = self.save_queue.get(timeout=5)
                
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"   💾 Auto-saved: {data['last_save']}")
                self.save_queue.task_done()
                
            except:
                pass
    
    def _stats_worker(self):
        print("   🧵 Stats vlákno: spuštěno")
        
        while not self.stop_event.is_set():
            time.sleep(30)  
            
            with self.lock:
                total = len(self.tasks)
                completed = sum(1 for t in self.tasks if t.completed)
            
            if total > 0:
                print(f"   📊 Stats: {completed}/{total} dokončeno ({completed/total*100:.0f}%)")
    
    def add_task(self, name, priority="střední"):
        with self.lock:
            task = Task(self.next_id, name)
            task.priority = Priority(priority)
            self.tasks.append(task)
            self.next_id += 1
        
        self.save_tasks()
        return task
    
    def get_task(self, task_id):
        with self.lock:
            for task in self.tasks:
                if task.id == task_id:
                    return task
        return None
    
    def complete_task(self, task_id):
        task = self.get_task(task_id)
        if task:
            with self.lock:
                task.mark_completed()
            self.save_tasks()
            return True
        return False
    
    def delete_task(self, task_id):
        with self.lock:
            for i, task in enumerate(self.tasks):
                if task.id == task_id:
                    del self.tasks[i]
                    self.save_tasks()
                    return True
        return False
    
    def get_all_tasks(self):
        with self.lock:
            return self.tasks.copy()
    
    def get_stats(self):
        with self.lock:
            total = len(self.tasks)
            completed = sum(1 for t in self.tasks if t.completed)
            pending = total - completed
            
            priorities = {
                'vysoká': sum(1 for t in self.tasks if t.priority == Priority.HIGH),
                'střední': sum(1 for t in self.tasks if t.priority == Priority.MEDIUM),
                'nízká': sum(1 for t in self.tasks if t.priority == Priority.LOW)
            }
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'priorities': priorities
        }
    
    def export_to_json(self, filename):
        with self.lock:
            data = {
                'tasks': [t.to_dict() for t in self.tasks],
                'export_date': datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            }
        
        export_thread = threading.Thread(
            target=self._export_worker,
            args=(filename, data),
            name=f"Export-{filename}"
        )
        export_thread.start()
        return export_thread
    
    def _export_worker(self, filename, data):
        print(f"   🧵 Export vlákno: exportuji do {filename}")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Export dokončen: {filename}")
    
    def stop(self):
        print("🛑 Ukončuji vlákna...")
        self.stop_event.set()
        
        self.save_queue.join()
        
        self.save_tasks()
        time.sleep(1)