import os
import sys
import numpy as np
import yaml
import pickle

import argparse
import time
import shutil
import logging
from datetime import datetime

import matplotlib.pyplot as plt

import bnpm
import bnpm.plotting_helpers
import bnpm.path_helpers
import bnpm.ca2p_preprocessing
import bnpm.h5_handling

class z_tracker:
    def __init__(
        self,
        dir_video_exp = None,
        path_video_stack = None,
        dir_save = None,
        path_params = "/n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/params.yml",
        overwrite = False,
    ):
        """_Class to efficiently run offline z-position tracking on slurm_

        Args:
            dir_video_exp (str, optional): Directory of exp files to track. If None, specified at params.yml.
            path_video_stack (str, optional): Reference Stack file path. If None, specified at params.yml.
            dir_save (str, optional): Directory to save results. If None, specified at params.yml.
            path_params (str, optional): Master params.yml file path. Defaults to "/n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/params.yml".
            overwrite (bool, optional): If True, clear dir_save.. Defaults to False.
        """        
        # Command-line inputs
        logging.warning("Thanks for your command-line inputs!")
        self.dir_video_exp = dir_video_exp
        self.path_video_stack = path_video_stack
        self.dir_save = dir_save
        self.path_params = path_params
        self.overwrite = overwrite

        # Load params
        logging.warning("Loading Params...")
        logging.warning(self.path_params)
        with open(path_params, "rb") as param_handle:
            self.params = yaml.safe_load(param_handle)

        # ASSERT num of jobs is reasonable
        assert isinstance(self.params['z_tracking']['files_per_job'], int)

        self.get_paths_right()
        logging.warning(self.dir_video_exp)
        logging.warning(self.path_video_stack)
        logging.warning(self.dir_save)

        # If overwrite, destroy original dir_save
        if self.overwrite:
            logging.warning("!!! Destroying old results !!!")
            shutil.rmtree(self.dir_save, ignore_errors=True)

        if not os.path.exists(self.dir_save):
            logging.warning("Create dir to save!")
            os.mkdir(self.dir_save)
            shutil.copy(self.path_params, self.dir_save)
        self.dir_tmp = os.path.join(self.dir_save, "tmp")
        if not os.path.exists(self.dir_tmp):
            logging.warning("Create tmp dir!")
            os.mkdir(self.dir_tmp)
        
    def get_paths_right(self):
        """If Paths are not defined by cmdline input, load it from params.yml
        """        
        if self.dir_video_exp is None:
            self.dir_video_exp = self.params['paths']['dir_video_exp']
        
        if self.path_video_stack is None:
            self.path_video_stack = self.params['paths']['path_video_stack']

        if self.dir_save is None:
            self.dir_save = self.params['paths']['dir_save']
    
    def save_cmd(self, cmd):
        """Save single job cmd output to make sure everything works right

        Args:
            cmd (str): Single job submission command
        """        
        cmd_save = (
            self.dir_save
            + "/cmd_"
            + datetime.now().strftime("%Y%m%d-%H%M%S")
            + ".p"
        )
        with open(cmd_save, "wb") as file:
            pickle.dump(cmd, file)

    def submit_multi_process(self):
        """Submit multiple single jobs to efficiently parallelize z-position tracking
        """        
        workload = bnpm.path_helpers.find_paths(self.dir_video_exp, reMatch='exp_00001_')[:]
        if self.params['z_tracking']['files_per_job'] == -1:
            num_jobs = len(workload)
        elif self.params['z_tracking']['files_per_job'] == 0:
            num_jobs = 1
        else:
            num_jobs = (len(workload) // self.params['z_tracking']['files_per_job']) + 1

        logging.warning("Number of exp files: %d", len(workload))
        logging.warning("Number of tiff files per job: %d", self.params['z_tracking']['files_per_job'])
        logging.warning("Number of jobs to submit: %d", num_jobs)
            
        cmd_single_process = "sbatch --array=%d-%d cmd_single_process.sh%s%s%s%s" % (
            0,
            num_jobs - 1,
            " --dir-video-exp " + self.dir_video_exp,
            " --path-video-stack " + self.path_video_stack,
            " --dir-save " + self.dir_save,
            " --path-params " + self.path_params
        )
        
        self.save_cmd(cmd_single_process)
        os.system(cmd_single_process)
        # sys.exit(os.WEXITSTATUS(os.system(cmd)))

    def stack_metadata(self):
        """Load scanimage_metadata if required
        """        
        if self.params['dense_to_sparse']['inherit_metadata']:
            logging.warning("Read Stack file metadata")
            self.scanimage_metadata = bnpm.ca2p_preprocessing.get_ScanImage_tiff_metadata(self.params['paths']['path_video_stack'])
        else:
            logging.warning("Don't read Stack file metadata. I trust your param input!")
            self.scanimage_metadata = None

    def start_z_tracking(self, stack_out, positions_z, workload, job_id):
        """Track z-position with reference z-stack image

        Args:
            stack_out (numpy.ndarray): Sparse Stack for Track Reference
            positions_z (list): z_position index array
            workload (list): Full list of files to track
            job_id (int): Job number index, acquired from slurm env variable

        Returns:
            outs: Tracked z-position information
        """        
        if self.params['z_tracking']['files_per_job'] == -1:
            outs = [bnpm.ca2p_preprocessing.find_zShifts(
                stack_out,
                positions_z=positions_z,
                path_to_tiff=workload[job_id],
                frames=None,
                **self.params['z_tracking']['kwargs'],
                )]
        elif self.params['z_tracking']['files_per_job'] == 0:
            outs = [bnpm.ca2p_preprocessing.find_zShifts(
                stack_out,
                positions_z=positions_z,
                path_to_tiff=work,
                frames=None,
                **self.params['z_tracking']['kwargs']
                ) for work in workload]
        else:
            if job_id == (len(workload) // self.params['z_tracking']['files_per_job']):
                outs = [bnpm.ca2p_preprocessing.find_zShifts(
                    stack_out,
                    positions_z=positions_z,
                    path_to_tiff=work,
                    frames=None,
                    **self.params['z_tracking']['kwargs']
                ) for work in workload[job_id * self.params['z_tracking']['files_per_job']:]]
            else:
                outs = [bnpm.ca2p_preprocessing.find_zShifts(
                    stack_out,
                    positions_z=positions_z,
                    path_to_tiff=work,
                    frames=None,
                    **self.params['z_tracking']['kwargs']
                ) for work in workload[job_id * self.params['z_tracking']['files_per_job']:(job_id + 1) * self.params['z_tracking']['files_per_job']]]
        return outs

    def single_process(self):
        """Track z-position of the imaging plane for the given amount of files
        """        
        logging.warning("Loading Reference Stack file...")
        frames_zstack = bnpm.ca2p_preprocessing.import_tiffs_SI(
            self.path_video_stack,
            **self.params['import_tiff'],
        )
        
        self.stack_metadata()

        logging.warning("Transfer to Sparse Stack...")
        stack_out, positions_z, idx_slices = bnpm.ca2p_preprocessing.dense_stack_to_sparse_stack_SI(
            frames_zstack,
            scanimage_metadata=self.scanimage_metadata,
            **self.params['dense_to_sparse']['kwargs'],
        )

        logging.warning("Track Z for %d number of tiff files...", self.params['z_tracking']['files_per_job'])
        workload = bnpm.path_helpers.find_paths(self.dir_video_exp, reMatch='exp_00001_')[:]
        job_id = int(os.getenv("SLURM_ARRAY_TASK_ID"))

        outs = self.start_z_tracking(stack_out, positions_z, workload, job_id)
        logging.warning("Z-tracking done")
        tmp_save_filename = os.path.join(self.dir_tmp, ''.join(["tracker_", str(job_id), ".pkl"]))
        logging.warning("Temp saving")
        logging.warning(tmp_save_filename)

        with open(tmp_save_filename, 'wb') as tmp_handle:
            pickle.dump(outs, tmp_handle)

    def merge_process(self):
        """Merge parallelized z-position tracking results
        """        
        workload = bnpm.path_helpers.find_paths(self.dir_video_exp, reMatch='exp_00001_')[:]
        if self.params['z_tracking']['files_per_job'] == -1:
            jobs_to_be_done = len(workload)
        elif self.params['z_tracking']['files_per_job'] == 0:
            jobs_to_be_done = 1
        else:
            jobs_to_be_done = (len(workload) // self.params['z_tracking']['files_per_job']) + 1
        procrastinator = 1
        
        while procrastinator:
            single_jobs_done = bnpm.path_helpers.find_paths(self.dir_tmp, reMatch='tracker_')[:]
            if len(single_jobs_done) == jobs_to_be_done:
                logging.warning("Jobs are done! Start merging")
                procrastinator = 0
            else:
                logging.warning("Waiting for jobs to be done...taking a sip of coffee...")
                time.sleep(60)
        else:
            single_jobs_done = bnpm.path_helpers.find_paths(self.dir_tmp, reMatch='tracker_')[:]
            outs_all = []
            for out in single_jobs_done:
                with open(out, 'rb') as out_handle:
                    outs_all.append(pickle.load(out_handle))

            positions_interp, zShift_interp, z_cc_interp = [], [], []
            for outs in outs_all:
                for o in outs:
                    positions_interp.append(o[0])
                    zShift_interp.append(o[1])
                    z_cc_interp.append(o[2])

            positions_interp = np.concatenate(positions_interp).astype(np.float32)
            z_cc_interp = np.concatenate(z_cc_interp, axis=0).astype(np.float32)
            zShift_interp = zShift_interp[0].astype(np.float32)

            fig, ax = plt.subplots()
            ax.plot(positions_interp)

            results = {
                'zPositions': positions_interp,
                'zAxis': zShift_interp,
                'z_cc': z_cc_interp,
            }
            logging.warning("Saving files...")
            bnpm.h5_handling.simple_save(
                dict_to_save=results,
                path=os.path.join(self.dir_save, 'z_positions.h5'),
                verbose=True,
            )
            fig.savefig(os.path.join(self.dir_save, 'z_positions_interp.png'))

    
def z_tracking():
    """_Run by cmd_z_tracking.sh bash file. Submit cluster jobs to run single_process, then merge_process._"""
    args = cmdline_parser()
    logging.warning("Ah Hello There Tracker!")
    tracker = z_tracker(**args.__dict__)
    tracker.submit_multi_process()
    tracker.merge_process()
    
def cmd_single_process():
    """_Run by cmd_single_process.sh bash file. On each cluster, track z-position given Reference Stack image._"""
    args = cmdline_parser()
    tracker = z_tracker(**args.__dict__)
    tracker.single_process()

    
def cmdline_parser():
    parser = argparse.ArgumentParser(
        description="BMI_offline_z_tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dir-video-exp",
        dest="dir_video_exp",
        type=str,
        default=None,
        help="Directory of exp files to track",
    )
    parser.add_argument(
        "--path-video-stack",
        dest="path_video_stack",
        type=str,
        default=None,
        help="Reference Stack file path",
    )
    parser.add_argument(
        "--dir-save",
        dest="dir_save",
        type=str,
        default=None,
        help="Directory to save results",
    )
    parser.add_argument(
        "--path-params",
        dest="path_params",
        type=str,
        default="/n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/params.yml",
        help="Master params.yml file path",
    )
    parser.add_argument(
        "--overwrite",
        dest="overwrite",
        default=False,
        action="store_true",
        help="If True, clear dir_save.",
    )

    return parser.parse_args()