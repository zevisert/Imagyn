## Imagyn

### Running image-collection.ipynb
* Download and install Anaconda3
* Create a virtual environment `conda create -f environment.yml`
* Activate the imagyn environment you just created `activate imagyn` on windows or `source activate imagyn` on everything else
* Run the notebook `jupyter notebook`

### Running Luigi Pipeline
in Capstone/project/luigi

run:
python3 pipeline.py RunAll --keyword toucan --imgCount 20 --exact 70 --similar 20 --unrelated 10 --local-scheduler

keyword: get images that match keyword
imgCount: # of images downloaded
exact: number of exact images downloaded
similar: number of similar images downloaded
unrelated: number of unrelated images downloaded

