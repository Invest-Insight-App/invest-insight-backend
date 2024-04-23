# FastAPI Backend Project

This backend is built using the FastAPI framework.
For detailed documentation on FastAPI, visit: [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Option 1: Setting Up Environment (venv)

1. Create the virtual environment file:

`python3.8 -m venv env`

2. Activate the virtual environment:

`source env/bin/activate`

3. Verify that the new environment is working:

`pip freeze`

3. Install packages:

`pip install -r requirements.txt`

## Option 2: Setting Up Environment (Conda)

1. Create the Conda environment from the provided `environment.yml` file:

`conda env create -f environment.yml`

2. Activate the newly created environment:

`conda activate myenv`

3. Verify that the new environment was installed correctly:

`conda env list`

For more information on managing Conda environments, refer to the [Conda User Guide](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

## Running the FastAPI Server Locally

To start the FastAPI local server, use the following command (run from the root directory of your project):

`uvicorn main:app --reload`

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser to access the Swagger API documentation.

![Swagger API Documentation](images/investment_insight_api.png)

### Adding API Key in `.env`

If your application requires an API key from [News API](https://newsapi.org/), make sure to add it in the `.env` file. Replace placeholder with your api key

`export NEWS_API_KEY="placeholder"`

## Start Testing!

You're all set up! Happy testing!.
