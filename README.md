# z_position_tracker
This function tracks the z position of the 2p imaging plane frame by frame, using a reference z-stack file. The original function was created by Rich Hakim in 2023.

# How to run the code
### 1. Modify the following lines of code to make it work on your local system.
- /n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/cmd_single_process.sh
  - Line 3, #SBATCH --output=YOUR SLURM_OUT PATH
  - Line 12-14, Match module version to your system
  - Line 16, Activate your environment
  - Line 18, cd to your z_position_tracker dir
- /n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/cmd_z_tracking.sh
  - Line 3, #SBATCH --output=YOUR SLURM_OUT PATH
  - Line 11-12, Match module version to your system
  - Line 14, Activate your environment
  - Line 16, cd to your z_position_tracker dir
- /n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/slurm_z_tracking.py
  - Line 27, Change the default path_params
  - Line 318, Change the default path_params
  
### 2. Carefully double-check your params.yml file.
  
### 3. You are now ready to run z-tracking by entering just one command-line input!
- Default: sbatch /n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/cmd_z_tracking.sh
- You can change the slurm output directory by entering: sbatch --output=YOUR_SLURM_OUT_DIR /n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/cmd_z_tracking.sh
- You can also input directories in the command-line input. The command-line input will overwrite the params.yml input.
  - Example: sbatch /n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/cmd_z_tracking.sh --dir-video-exp /n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/tester/exp
