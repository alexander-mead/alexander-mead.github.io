# Personal website

Once deployed (via GitHub pages), my personal website can be found here:
[https://alexander-mead.github.io./](https://alexander-mead.github.io./)

## Backend

### Mandelplot

Go to the function directory:

```sh
cd functions/mandelbrot
```

First, install the `poetry` environment:

```sh
poetry install
```

Install the Fortran part of the backend

```sh
cd Fortran
poetry run sh f2py.sh
cd ..
```

Run the test script:

```sh
poetry run python mandelbrot.py
```

An image of the Mandelbrot set should appear.

For a local or coloud deployment use the deployment script:

```sh
./scripts/deploy.sh
```

If a deployment is running, try the API invocation script:

```sh
./scripts/test.sh
```

some gibberish (which is the image in a weird format) should be displayed on the
terminal.

Return to the root directory

```sh
cd ../..
```

### N-body

Go to the function directory:

```sh
cd functions/nbody
```

First, install the `poetry` environment:

```sh
poetry install
```

Ensure that the twinLab model (if this is being used) is trained:

```sh
poetry run python training.py
```

Run the test scripts:

```sh
poetry run python nbody.py
```

an image of a slice through an N-body simulation should appear.

For a local deployment (runs on [http://127.0.0.1:3000](http://127.0.0.1:3000)):

```sh
sh build.sh local
```

or for a cloud deployment:

```sh
sh build.sh cloud
```

If a deployment is running, try the API invocation script:

```sh
sh test.sh <url>
```

some gibberish (which is the image in a weird format) should be displayed on the
terminal.

Return to the root directory

```sh
cd ../..
```

## Deployment troubleshooting

If there are any problems with deployment, try looking in the following files:

- `functions/*/samconfig.toml`
- `functions/*/template(.base).yaml` (ensure the architecture matches)
- `functions/*/Dockerfile`

Otherwise, try restarting Docker and/or purging the current set of containers.
