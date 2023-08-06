import os, json

def run_file(directory:str)->str:
    return os.path.join(directory, 'run.json')

def config_file(directory:str)->str:
    return os.path.join(directory, 'config.json')

def metrics_file(directory:str)->str:
    return os.path.join(directory, 'metrics.json')

def has_run_file(directory:str)->bool:
    return os.path.isfile(run_file(directory))

def has_config_file(directory:str)->bool:
    return os.path.isfile(config_file(directory))

def has_metrics_file(directory:str)->bool:
    return os.path.isfile(metrics_file(directory))

FILE_FNS = dict(zip(
    ['run', 'config', 'metrics'],
    [run_file, config_file, metrics_file]
))

def get_json(directory:str, which:str='config')->dict:
    file_fn = FILE_FNS[which]
    with open(file_fn(directory), 'r') as f:
        return json.load(f)

def run_status(directory:str)->bool:
    if not has_run_file(directory): return
    return get_json(directory, 'run')['status']

def is_run_failed(directory:str) -> bool:
    return run_status(directory) == 'FAILED'

def is_run_completed(directory:str) -> bool:
    return run_status(directory) == 'COMPLETED'

def is_run_running(run_file:str) -> bool:
    return run_status(directory) == 'RUNNING'

def is_sacred_experiment(directory:str)->bool:
    return (
        os.path.isdir(directory)
        and has_run_file(directory)
        and has_config_file(directory)
    )

def gather_experiments(experiments_dir:str, relative:bool=True)->list:
    experiment_names = [
        _dir
        for _dir in os.listdir(experiments_dir)
        if is_sacred_experiment(os.path.join(experiments_dir, _dir))
    ]
    if relative:
        return experiment_names
    return list(map(lambda e: os.path.join(experiments_dir, e), experiment_names))

def is_rerun(config:dict, experiment_dir) -> bool:
    if is_sacred_experiment(experiment_dir):
        other_config = get_json(experiment_dir, 'config')
        if other_config != config: return False
        if is_run_running(run_file) or is_run_completed(run_file): return True
    return False
