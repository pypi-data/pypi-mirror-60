import yaml

from jolt.tasks import Parameter, Task, TaskGenerator, TaskRegistry
from jolt import log
from jolt import loader

log.verbose("[YamlTask] Loaded")

class YamlLoader(TaskGenerator):

    def _load_yaml(self):
        files = []
        path = os.getcwd()
        while not files:
            files = glob.glob(fs.path.join(path, "*.yaml"))
            for file in files:
                with open(file) as f:
                    import yaml
                    obj = yaml.safe_load_all(f)
                    obj = [o for o in obj]

                for doc in obj:
                    task = doc.get("task")

                    class YamlTask(Task):
                        _run_commands = []
                        _publish_files = []

                        def run(self, d, t):
                            for cmd in self._run_commands:
                                t.run(cmd)

                        def publish(self, a, t):
                            for pf in self._publish_files:
                                a.collect(pf)

                    YamlTask.name = task["name"]
                    YamlTask.requires = task.get("requires", [])

                    for req in task.get("params", []):
                        setattr(YamlTask, req["name"], Parameter(values=req.get("values", None)))

                    for cmd in task.get("commands", []):
                        YamlTask._run_commands.append(cmd)

                    for pf in task.get("publish", {}).get("files", []):
                        YamlTask._publish_files.append(pf)

                    self._tasks.append(YamlTask)

            if files:
                self._path = path
                break
            opath = path
            path = fs.path.dirname(path)
            if path == opath:
                break
        return self._tasks, self._tests

    def generate(self):
        return []
