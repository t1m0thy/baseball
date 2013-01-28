import yaml

TODO = "todo"
DONE = "done"

class JobManager:
    """
    maintains a list of jobs in a yaml file
    jobs have status either "todo" or "done"
    jobs can be organized job type
    
    this is setup to try and allow more job stats in the future. ie: "error", "check"
    """
    def __init__(self, filepath):
        self._filepath = filepath
        self._jobs = yaml.load(open(self._filepath,'r'))
    
    def jobs(self, jobtype, status=TODO):
        for job, status in self._jobs[jobtype].items(): 
            if status == TODO:
                yield job

    def complete_job(self, job, jobtype):
        self._jobs[jobtype][job] = DONE
        
    def set_job_status(self, job, jobtype, status):
        self._jobs[jobtype][job] = status
        
    def get_completed(self, jobtype):
        jobs = self._jobs[jobtype] 
        return [job for job in jobs if jobs[job] == DONE]
    
    def add_job(self, job, jobtype):
        self._jobs[jobtype][job] = TODO
        
    def save(self):
        with open(self._filepath,'w') as f:
            yaml.dump(self._jobs, f, default_flow_style=False)
