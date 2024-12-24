# Personal website

Once deployed (via GitHub pages), my personal website can be found here:
[https://alexander-mead.github.io./](https://alexander-mead.github.io./)

## Backend

First, install the (global) `poetry` environment:

```bash
poetry install
```

To build and deploy the backend (from the root directory):

For a local deployment (runs on [http://127.0.0.1:3000](http://127.0.0.1:3000)):

```bash
sh build.sh local
```

or for a cloud deployment:

```bash
sh build.sh cloud
```

### Mandelplot

Go to the function directory:

```bash
cd functions/mandelbrot
```

Install the Fortran part of the backend

```bash
cd Fortran
poetry run sh f2py.sh
cd ..
```

Run the test script:

```bash
poetry run python mandelbrot.py
```

An image of the Mandelbrot set should appear.

If a local deployment is running, try the API invocation script:

```bash
sh test.sh
```

some gibberish (which is the image in a weird format) should be displayed on the
terminal.

Return to the root directory

```bash
cd ../..
```

### Nbody

Go to the function directory:

```bash
cd functions/nbody
```

Ensure the model is trained:

```bash
poetry run python training.py
```

Run the test scripts:

```bash
poetry run python nbody.py
```

an image of a slice through an N-body simulation should appear.

If a local deployment is running, try the API invocation script:

```bash
sh test.sh
```

some gibberish (which is the image in a weird format) should be displayed on the
terminal.

Return to the root directory

```bash
cd ../..
```

## Deployment troubleshooting

If there are any problems with deployment, try looking in the following files:

- samconfig.toml
- template.base.yaml
- functions/mandelbrot/Dockerfile
- functions/nbody/Dockerfile
