import yaml
import os

TODO = "TODO"
DONE = "> done"
ERROR = "> error"
DELETE = "DELETE"

class JobManager:
    """
    maintains a list of jobs in a yaml file
    jobs have job_type either of any string
    recommended job_types are constants of this module

    jobs are organized group ie. "pointstreak"
    """
    
    def __init__(self, filepath):
        self._filepath = filepath
        if os.path.isfile(self._filepath):
            self._jobs = yaml.load(open(self._filepath,'r'))
        else:
            self._jobs = {}
            
    def has_jobs(self, job_group):
        return job_group in self._jobs and len(self._jobs[job_group]) > 0
        
    def groups(self):
        for group in self._jobs.keys():
            yield group
            
    def jobs(self, job_group, do_job_type=TODO):
        for job, job_type in self._jobs[job_group].items(): 
            if job_type == do_job_type:
                yield job

    def job_count(self, job_type=TODO):
        total = 0
        for v in self._jobs.values():
            total += len([i for i in v.values() if i == job_type])
        return total
    
    def complete_job(self, job, job_group):
        if job_group not in self._jobs:
            raise StandardError("No Job Group {}".format(job_group))
        if job not in self._jobs[job_group]:
            raise StandardError("No Job {} in group {}".format(job, job_group))
        self._jobs[job_group][job] = DONE
        
    def get_completed(self, job_group):
        jobs = self._jobs[job_group] 
        return [job for job in jobs if jobs[job] == DONE]
    
    def add_job(self, job, job_group, job_type=TODO, overwrite=False):
        if job_group not in self._jobs:
            self._jobs[job_group] = {}
        if job not in self._jobs[job_group] or overwrite:
            self._jobs[job_group][job] = job_type
        else:
            raise StandardError("Job {} in group {}".format(job, job_group) +
                                "already exists with value" +
                                str(self._jobs[job_group][job])
                                )
        
    def set_job(self, job, job_group, job_type):
        """ shortcut to for changing job status """
        self.add_job(job, job_group, job_type, overwrite=True)

    def add_jobs(self, joblist, job_group, job_type=TODO, overwrite=False,):
        for job in joblist:
            self.add_job(job, job_group, job_type, overwrite)
    
    def clear_jobs(self, job_group):
        del(self._jobs[job_group])
        
    def save(self):
        with open(self._filepath,'w') as f:
            yaml.dump(self._jobs, f, default_flow_style=False)
