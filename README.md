# Mapping Saints
This is a Django-based portal for the digital humanities project, "Mapping Saints - Medieval Cults of Saints in Sweden & Finland" developed by the Gothenburg Research Infrastructure in Digital Humanities (GRIDH) at the University of Gothenburg in cooperation with Linnaeus University. 

## Local installation
To install it, you can either use a Conda distribution, such as [Anaconda](https://www.anaconda.com/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or install the requirements directly with pip. 

### Operative system support
The backend and its dependencies have been tested on Linux, e.g. Ubuntu 20.04+ and RedHat OS.

### Instructions
Clone the repository and change directory. 
```bash
git clone https://github.com/gu-gridh/saints
cd saints
```

Create a new conda environment from the `environment.yml` file using
```bash
conda env create -n saints -f environment.yml
```
This will also install the required GDAL dependency for geographical databases.

Activate the conda environment:
```bash
conda activate saints
```

Before installing Django, it is advised to first look through the Django [tutorial](https://docs.djangoproject.com/en/4.1/intro/tutorial01/) and documentation.

For a local installation, a `configs` folder with database credentials for your local database is needed.
Your local database needs the `postgis` extension which can be added as postgres user with:
```bash
\connect <databasename>
CREATE EXTENSION postgis;
```
Also, a `.env` with your local settings is needed.
Launch Django by migrating all the initial settings,
```bash
python manage.py migrate 
```
and create a suitable superuser.

```bash
python manage.py createsuperuser 
```

Run it locally via:
```bash
python manage.py runserver
```

## Current URLs

- http://localhost:8000/admin/ - Admin interface for  users and groups
- http://localhost:8000/api/ - REST API endpoints
