# MPI-rical: Data-Driven MPI Distributed Parallelism Assistance with Transformers
Automatic source-to-source parallelization of serial code for shared and distributed memory systems is a challenging task in high-performance computing.
While many attempts were made to translate serial code into parallel code for a shared memory environment --- usually using OpenMP --- none has managed to do so for a distributed memory environment. The evolving field of AI-based programming assistance tools, on the other hand, shows a promising direction that could offer an opportunity for developing an assistance tool for writing distributed memory code.
In this paper, we propose a novel approach, called MPI-rical, for inserting MPI functions using a transformer-based model trained on approximately 25,000 MPI code snippets (in C language) out of more than 50,000 code snippets in our corpus MPICodeCorpus.
In order to evaluate the performance of the model systematically, we refer to inserting MPI functions into an MPI-based parallel code as a code translation problem: defined as predicting an MPI function as well as its location in a given source code.
We evaluate MPI-rical on the MPICodeCorpus dataset, on real-world scientific code benchmarks, and even with our own compiled MPI numerical computations codes.
Our experimental results show that MPI-rical achieves an F1 score on the MPI common functions of 0.89 on the dataset test and a score of 0.68 on the benchmark. Implying that there is an understanding of how to use MPI routines.
Overall, our approach represents a significant step forward in advising MPI code through distributed memory systems writing, which can save valuable time and resources for software developers and researchers.
          
## Desired Objective  ##
![](images/objective.PNG)
A data-oriented workflow of the MPI-rical system, exemplified by a distributed Pi calculation code: Given a corpus of MPI codes, a subset of the original dataset is created --- Removed - Locations [R-L] --- in which the MPI functions are replaced by a void and the original locations are not preserved. This is also done to the xSBT representations. Accordingly, the subset [R-L] is used to train a translation model, SPT-Code, which will eventually predict the desired MPI classification for new samples of codes given in those fashions. As such, MPI-rical is useful in easing the writing of MPI codes in IDEs.

## MPI-rical Training and Evaluation  ##
![](images/model.PNG)
Overview of the model's training and evaluation. The dataset is created from MPICodeCorpus while three files constitute one example; MPI C code (label), MPI C code functions excluded, and its X-SBT (linearized AST). Our model, MPI-rical, trains and evaluates these examples. MPI-rical was pre-trained from the CodeSearchNet dataset.


# Instructions
## Requirments
First, clone the MPI-rical code provided here, the dataset subsets and SPT-Code.
```
clone https://github.com/Scientific-Computing-Lab-NRCN/MPI-rical.git
```
Then, two conda environments have to be created; SPTcode and code2mpi.
```
conda create --name <env_name> --file SPTcode
```
Then, activate your environment:
```
conda activate <env_name>
```
Download the right packages according to the official SPT-Code github: https://github.com/NougatCA/SPT-Code
and the following packages inside code2mpi environment:
```
pycparser
matplotlib
scikit-learn==0.24.2
scipy==1.7.3
python==3.7
```
code2mpi is used to pre-process and analyze the data while SPTcode is used to train and evaluate the models.


## Citation
For more information about the measures and their means of the implementations, please refer to the paper.
If you found these codes useful for your research, please consider citing: https://arxiv.org/abs/2305.09438

## Dataset
The corpus is located [here](https://drive.google.com/file/d/1lRTSbh9aitI4BdWxPI8reLpJV4WnlIWQ/view?usp=sharing)
It contains folders in the following tree structure:
```
├── User1
│   ├── Repository1
│       ├── Program1
│       ├── Program2
│       └── Outputs
│   └── Repository2
│       ├── Program1
│       └── Outputs
├── User2
│   ├── Repository1
│       ├── Program1
│       ├── Program2
│       ├── Program3
│       └── Outputs
```
1. **User** - The github's user.
2. **Repository** - One of the repositories of the current user.
3. **Program** - Contains one C main program and its headers files.
4. **Outputs** - Contains main file after preprocess and main program's AST pickle file if AST has been successfully generated.


Please note, that the pickle file can easily be created by wrapping code.c with a int main() {} and applying the pycparser parser.  

In addition, the database contains a json file that maps the folders -- each key in the json file represents a corpus record: user name, repository name, a unique id for each program and its path.
This json file can be recreated with the make/database.py script.
The three mentioned dataset-subsets have been created using the corpus.


## Running
### Configuration
Change the paths in config.yaml file to the relevant paths:
```
REPOS_ORIGIN_DIR: '/home/yourname/MPI-rical/DB/git_repos'
REPOS_MPI_DIR: '/home/yourname/MPI-rical/DB/repositories_MPI'
PROGRAMS_MPI_DIR: '/home/yourname/MPI-rical/DB/programs'
DB_DIR: '/home/yourname/MPI-rical/DB'
MPI_DIR: '/home/yourname/MPI-rical/DB/MPI'
MPI_SERIAL_DIR: '/home/yourname/MPI-rical/DB/MPI_SERIAL'
MPI_SERIAL_HEURISTICS_DIR: '/home/yourname/MPI-rical/DB/MPI_SERIAL_HEURISTICS'
MPI_SERIAL_PLACEHOLDER_DIR: '/home/yourname/MPI-rical/DB/MPI_SERIAL_PLACEHOLDER'
```
### Evaluate
To evaluate the models activate the SPTcode environment and enter the source folder: 
```
conda activate SPTcode
cd Desktop/MPI-rical/SPT-Code/Source
```
Then, run the following:
* For evaluating Translation [R-L]:
```
python main.py --only-test --task translation --translation-source-language serial_c --translation-target-language mpi_c --no-nl --batch-size 32 --max-code-len 320 --trained-vocab '/home/nadavsc/LIGHTBITS/SPT-Code/dataset/pre_trained/vocabs' --trained-model '/home/nadavsc/LIGHTBITS/SPT-Code/outputs/5_epochs_320_close_placeholder_translation/models'
```
Make sure to insert the right paths of both the model itself and the pre trained vocabs.

