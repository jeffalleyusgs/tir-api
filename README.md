# BIS Data Distribution API

API for distributing BIS data resulting from the data pipeline project.

### Environment Setup
- This project uses python-dotenv to manage secrets. This requires a `.env` file in the root directory with the following variables set.
    ```
    ENVIRONMENT=""
    ELASTIC_BASE_URL=""
    PUBLIC_S3_BUCKET=""
    URL_PREFIX="/sgcn"
    BASE_URL=""
    ```
  `URL_PREFIX` and `BASE_URL` are optional
- Alternatively, these can be set as local environment variables, such as in the
  case of cloud deployment.

### To Run Locally
- Using virtualenv https://virtualenv.pypa.io/en/latest/
    ```
    virtualenv --python="path/to/python3" path/to/ENV
    source path/to/ENV/bin/activate
    ```
- Then
    ```
    pip install -r requirements.txt
    python run.py
    ```

### To Run Locally With Docker
    docker-compose -f docker-compose-local.yml up --build

## Technologies Used
- Elastic Search
    - https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
- Flask
    - http://flask.palletsprojects.com/en/1.1.x/
- Flask-RESTX
    - https://github.com/python-restx/flask-restx
- BIS Data Pipeline Project
    - https://code.chs.usgs.gov/fort/bcb/pipeline/bcb-data-pipeline/blob/master/README.md
- Docusaurus (v2)
    - https://v2.docusaurus.io/

## Versioning
 This API uses semantic versioning. E.g. v1.0.0

- MAJOR version indicates an incompatible API change.
- MINOR version indicates some functionality has been added in a backwards compatible manner.
- PATCH version indicates backwards compatible bug fixes.

## API Usage
TBD

## Docs
There is a static docs site created with Docusaurus at `/docs`
- See [docs-website](/docs-website)

