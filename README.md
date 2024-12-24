# Personal website

Once deployed (via GitHub pages), my personal website can be found here:
[https://alexander-mead.github.io./](https://alexander-mead.github.io./)

## Backend

First, install the (global) `poetry` environment:

```bash
poetry install
```

To build and deploy the backend (from the root directory):

Locally (runs on [http://127.0.0.1:3000](http://127.0.0.1:3000)):

```bash
sh build.sh local
```

Cloud:

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

Run the test script:

```bash
poetry run python nbody.py
```

An image of a slice through an N-body simulation should appear.

Return to the root directory

```bash
cd ../..
```
