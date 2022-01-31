This repository contains the replication code for the working paper ["Algorithmic and Human Collusion"](https://tofewe.github.io/Algorithmic_and_Human_Collusion_Tobias_Werner.pdf).
It utilizes the build automation tool [waf](https://waf.io/apidocs/tutorial.html) with the [econ-project-template](https://github.com/OpenSourceEconomics/econ-project-templates).

The paper is currently under review, and the experimental data will be available soon. 

This repository does not contain the simulations or the application to run the experiments. To run the simulations that are described in the paper, please see [here](https://github.com/ToFeWe/qpricesim) and [here](https://github.com/ToFeWe/q-learning-simulation-code). The oTree application for the online experiments is [here](https://github.com/ToFeWe/AlgoCollusionApp).

# Getting started

1. Place the simulation data in src/original_data/simulation_data and the experimental data in src/original_data/experiment_data
2. Create a local environment 
3. Install the qpricesim package  
```terminal
pip install git+https://github.com/ToFeWe/qpricesim.git
```
4. Install all other python package requirements 
```terminal
pip install -r requirements.txt
```
5. Configure the project and install additional software that is necessary (LaTeX, R, etc.).
```terminal
python waf.py configure
```
6. Invoke the build process
```terminal
python waf.py build
```
