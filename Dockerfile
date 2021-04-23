
#
# == Build the static Docusaurus docs
#
ARG node_image=node
ARG node_image_tag=10.15
ARG python_image=python
ARG python_image_tag=3.7-slim-buster

FROM ${node_image}:${node_image_tag} as doc_build
WORKDIR /docs
COPY ./docs-website /docs

# Only for when running locally
# RUN npm config set strict-ssl false

RUN npm install
RUN npm run build

#
# == Python runtime image
#
FROM ${python_image}:${python_image_tag}

ENV PYTHONUNBUFFERED 1

RUN adduser pyuser

WORKDIR /app
COPY requirements.txt /app
# Copy the static docs into the python app
COPY --from=doc_build /docs/build /app/docs

# To handle strange root cert issues for local builds, pass with the 'pip_install_args' argument
ARG pip_install_args
RUN pip install ${pip_install_args} --upgrade pip
RUN pip install ${pip_install_args} -r requirements.txt
RUN pip install ${pip_install_args} gunicorn

# Edit the .dockerignore file to include only what we want
COPY . .

# Remove the code used to build the static docs
RUN rm -rf docs-website
RUN chmod +x run.py
RUN chown -R pyuser:pyuser /app

USER pyuser

EXPOSE 8080

CMD ["gunicorn", "--config=config.py", "run"]
