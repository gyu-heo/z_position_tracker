# z_position_tracker
Track frame-by-frame z_position of the 2p imaging plane given a reference z-stack file. Original function created by Rich Hakim 2023

# How to run the code
### 1. Change following lines of the codes so that it will work in your local system.
- /n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/cmd_single_process.sh
  - Line 3, #SBATCH --output=YOUR SLURM_OUT PATH
  - Line 12-14, Match module version to your system
  - Line 16, Activate your environment
  - Line 18, cd to z_position_tracker dir
- /n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/cmd_z_tracking.sh
  - Line 3, #SBATCH --output=YOUR SLURM_OUT PATH
  - Line 11-12, Match module version to your system
  - Line 14, Activate your environment
  - Line 16, cd to z_position_tracker dir
- /n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/slurm_z_tracking.py
  - Line 27, Change default path_params
  - Line 318, Change default path_params
  
### 2. Carefully double-check your params.yml file.
  
### 3. You are ready to run z-tracking by just one command-line input!
- Default: sbatch /n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/cmd_z_tracking.sh
- You can change slurm output dir by: sbatch --output=YOUR_SLURM_OUT_DIR /n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/cmd_z_tracking.sh
- You can also feed directories in command-line input. Command-line input will overwrite params.yml input.
  - example: sbatch /n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/cmd_z_tracking.sh --dir-video-exp /n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/tester/exp
