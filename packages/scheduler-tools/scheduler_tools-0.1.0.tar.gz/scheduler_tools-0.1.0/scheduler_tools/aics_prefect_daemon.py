from dask_jobqueue import SLURMCluster
import dask, dask.distributed
from time import sleep
from datetime import datetime
from pathlib import Path

from aicsdaemon import Daemon

from .types import Pathlike


class AicsPrefectDaemon(Daemon):

    def __init__(self, slurm_prefs: dict, pidfile: Pathlike, stdin: Pathlike = None, stdout: Pathlike = None,
                 stderr: Pathlike = None, foreground: bool = False):
        super(AicsPrefectDaemon, self).__init__(pidfile=pidfile,
                                                stdout=stdout,
                                                stdin=stdin,
                                                stderr=stderr,
                                                foreground=foreground)
        print("AicsPrefectDaemon: pidfile: ", pidfile)
        open(stdout, 'w').close() if stdout else None
        self._slurm_prefs = slurm_prefs
        self._client = None
        self._localdir = Path(pidfile).parent / "logs" / datetime.now().strftime("%Y%m%d_%H:%M:%S")

    def run(self):

        cluster = SLURMCluster(cores=self._slurm_prefs['cores'],
                               memory=self._slurm_prefs['ram'],
                               walltime=self._slurm_prefs['wall_time'],
                               queue=self._slurm_prefs['queue'],
                               local_directory=self._localdir,
                               log_directory=self._localdir)
        cluster.adapt(minimum_jobs=self._slurm_prefs['min_workers'],
                      maximum_jobs=self._slurm_prefs['max_workers'])
        self._client = dask.distributed.Client(cluster)

        print(f"{cluster.scheduler_info['address']}")
        print(f"{cluster.scheduler_info['services']['dashboard']}", flush=True)

        # this enables us to put something in stdin and if so this loop will
        # exit. Thus using the stdin="filepath" argument gives us a clean way to
        # shutdown the process
        mtime = self.stdin.stat().st_mtime
        while mtime == self.stdin.stat().st_mtime:
            now = datetime.now()
            print(now)
            sleep(30)


