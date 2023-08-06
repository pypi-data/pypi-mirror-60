import json
from scheduler_tools.types import Pathlike
from pathlib import Path
import getpass


class PrefectPreferences:
    """
    This class handles reading of a ~/.prefect/ssh.json file. This file has settings for the
    name of the gateway, the username to authenticate with, the path to the local ssh identity
    file.
    """

    def __init__(self, path: Pathlike = None):
        """

        :param path:
        """
        self._path = None

        if path is None:
            path = self.default_path() / "ssh.json"

        if not Path(path).expanduser().exists():
            raise FileNotFoundError

        self._path = Path(path).parent

        with open(path.expanduser(), "r") as f_in:
            self._data = json.load(f_in)

        self._check_json_obj()
        self._add_name_if_needed()
        self._add_known_hosts_if_needed()

    def default_path(self) -> Path:
        if self._path is None:
            print("loading default .aics_dask path")
            self._path = Path("~/.aics_dask")
        print(f"path: {self._path}")
        return self._path

    @property
    def gateway_url(self):
        return self._data['gateway']['url']

    @property
    def username(self):
        return self._data['gateway']['user']

    @property
    def identity_file(self):
        return self._data['gateway']['identityfile']

    @property
    def known_hosts(self):
        return self._data['known_hosts']

    def write_ssh_pid(self, pid):
        with open(str(self.ssh_pid_path()), 'w') as fp:
            fp.write(str(pid))

    def read_ssh_pid(self) -> [str, type(None)]:
        pid = None
        if self.ssh_pid_path().expanduser().exists():
            pid = open(str(self.ssh_pid_path().expanduser()), 'r').read()
        return pid

    def remove_ssh_pid(self):
        if self.ssh_pid_path().exists():
            self.ssh_pid_path().unlink()

    def ssh_pid_path(self):
        return self.default_path().expanduser() / "ssh_pid.txt"

    def cluster_job_id_path(self):
        return self.default_path().expanduser() / "cluster_job_id.txt"

    def read_prefect_job_id(self) -> [str, type(None)]:
        job_id = None
        if self.cluster_job_id_path().exists():
            job_id = open(str(self.cluster_job_id_path().expanduser()), 'r').read()
        return job_id

    def write_prefect_job_id(self, job_id):
        print(f"jobid: {job_id}")
        with open(str(self.cluster_job_id_path().expanduser()), 'w') as fp:
            fp.write(str(job_id))

    def remove_prefect_job_id(self):
        if self.cluster_job_id_path().exists():
            self.cluster_job_id_path().unlink()

    def cluster_pid_path(self):
        # this needs to be made dynamic
        return self.default_path().relative_to(Path().home()) / "pidfile"

    @property
    def local_dask_port(self):
        return self._data['dask_port']

    @property
    def local_dashboard_port(self):
        return self._data['dashboard_port']

    # private methods

    def _check_json_obj(self):
        assert "gateway" in self._data
        assert "url" in self._data["gateway"]
        assert "identityfile" in self._data["gateway"]
        # user can be optional and assume the local username extends to the gateway

    def _add_name_if_needed(self):
        if "user" not in self._data["gateway"]:
            self._data["gateway"]["user"] = getpass.getuser()

    def _add_known_hosts_if_needed(self):
        if "known_hosts" not in self._data:
            self._data["known_hosts"] = Path('~/.ssh/known_hosts').expanduser().resolve()

