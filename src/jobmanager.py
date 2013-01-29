import yaml
import os

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
        if os.path.isfile(self._filepath):
            self._jobs = yaml.load(open(self._filepath,'r'))
        else:
            self._jobs = {}
            
    def has_jobs(self, jobtype):
        return jobtype in self._jobs and len(self._jobs[jobtype]) > 0
        
    def jobs(self, jobtype, status=TODO):
        for job, status in self._jobs[jobtype].items(): 
            if status == TODO:
                yield job

    def job_count(self, status=TODO):
        total = 0
        for v in self._jobs.values():
            total += len([i for i in v.values() if i == status])
        return total
    
    def complete_job(self, job, jobtype):
        self._jobs[jobtype][job] = DONE
        
    def set_job_status(self, job, jobtype, status):
        self._jobs[jobtype][job] = status
        
    def get_completed(self, jobtype):
        jobs = self._jobs[jobtype] 
        return [job for job in jobs if jobs[job] == DONE]
    
    def add_job(self, job, jobtype, overwrite=False):
        if jobtype not in self._jobs:
            self._jobs[jobtype] = {}
        if job not in self._jobs[jobtype] or overwrite:
            self._jobs[jobtype][job] = TODO
        
    def add_jobs(self, joblist, jobtype, overwrite=False):
        for job in joblist:
            self.add_job(job, jobtype, overwrite)
            
    def save(self):
        with open(self._filepath,'w') as f:
            yaml.dump(self._jobs, f, default_flow_style=False)
