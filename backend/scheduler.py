import asyncio
import time
import logging
from typing import Dict, Any, Callable, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

class TaskStatus(BaseModel):
    name: str
    running: bool
    last_run: float
    error_count: int
    last_error: Optional[str]
    interval: int
    next_run: float
    success_count: int
    avg_duration: float

class Scheduler:
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.running = False
        self.logger = logging.getLogger(__name__)
        
        # Default task configurations
        self.default_tasks = {
            "delta_check": {
                "interval": 4,  # 4 seconds
                "function": None,
                "description": "Delta calculation check"
            },
            "position_update": {
                "interval": 30,  # 30 seconds
                "function": None,
                "description": "LP position update"
            },
            "onchain_refresh": {
                "interval": 4,  # 4 seconds
                "function": None,
                "description": "On-chain data refresh"
            }
        }
    
    def add_task(self, name: str, func: Callable, interval: int, description: str = ""):
        """Add a task to the scheduler."""
        self.tasks[name] = {
            "function": func,
            "interval": interval,
            "description": description,
            "status": TaskStatus(
                name=name,
                running=False,
                last_run=0,
                error_count=0,
                last_error=None,
                interval=interval,
                next_run=time.time(),
                success_count=0,
                avg_duration=0.0
            )
        }
        self.logger.info(f"Added task: {name} (interval: {interval}s)")
    
    def remove_task(self, name: str):
        """Remove a task from the scheduler."""
        if name in self.tasks:
            del self.tasks[name]
            self.logger.info(f"Removed task: {name}")
    
    def update_task_interval(self, name: str, interval: int):
        """Update task interval."""
        if name in self.tasks:
            self.tasks[name]["interval"] = interval
            self.tasks[name]["status"].interval = interval
            self.logger.info(f"Updated task {name} interval to {interval}s")
    
    async def start(self):
        """Start the scheduler."""
        self.running = True
        self.logger.info("Starting scheduler...")
        
        # Start all tasks
        task_coroutines = []
        for name, task_info in self.tasks.items():
            task_coroutines.append(self._run_task(name, task_info))
        
        # Run all tasks concurrently
        await asyncio.gather(*task_coroutines)
    
    async def stop(self):
        """Stop the scheduler."""
        self.running = False
        self.logger.info("Stopping scheduler...")
    
    async def _run_task(self, name: str, task_info: Dict[str, Any]):
        """Run a single task in a loop."""
        status = task_info["status"]
        func = task_info["function"]
        interval = task_info["interval"]
        
        self.logger.info(f"Starting task: {name}")
        
        while self.running:
            try:
                # Check if it's time to run
                current_time = time.time()
                if current_time >= status.next_run:
                    status.running = True
                    start_time = time.time()
                    
                    # Execute task
                    if asyncio.iscoroutinefunction(func):
                        await func()
                    else:
                        func()
                    
                    # Update success metrics
                    duration = time.time() - start_time
                    status.success_count += 1
                    status.avg_duration = (status.avg_duration * (status.success_count - 1) + duration) / status.success_count
                    status.last_run = current_time
                    status.error_count = 0
                    status.last_error = None
                    
                    self.logger.debug(f"Task {name} completed in {duration:.2f}s")
                
                # Calculate next run time
                status.next_run = status.last_run + interval
                
                # Sleep until next run or stop signal
                sleep_time = max(0, status.next_run - time.time())
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                
            except Exception as e:
                status.error_count += 1
                status.last_error = str(e)
                status.last_run = time.time()
                status.next_run = status.last_run + interval
                
                self.logger.error(f"Task {name} failed: {e}")
                
                # Sleep before retry
                await asyncio.sleep(min(interval, 5))  # Max 5s retry delay
            
            finally:
                status.running = False
    
    def get_task_status(self, name: str) -> Optional[TaskStatus]:
        """Get status of a specific task."""
        if name in self.tasks:
            return self.tasks[name]["status"]
        return None
    
    def get_all_task_status(self) -> Dict[str, TaskStatus]:
        """Get status of all tasks."""
        return {name: task_info["status"] for name, task_info in self.tasks.items()}
    
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self.running
    
    def get_task_count(self) -> int:
        """Get number of tasks."""
        return len(self.tasks)

# Global scheduler instance
scheduler = Scheduler()

def get_scheduler() -> Scheduler:
    """Get the global scheduler instance."""
    return scheduler 