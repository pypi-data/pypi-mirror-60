# SG Markets XSF API - COFBOX - Cof Box V1

## 1- Introduction

This repo is meant to make it easy for clients (and employees) to SG XSF [Cof Box V1](https://analytics-api.sgmarkets.com/cofbox/swagger/ui) API.

This repo contains:

-   a ready-to-use [demo notebook](https://nbviewer.jupyter.org/urls/gitlab.com/sgmarkets/sgmarkets-api-xsf-cofbox/raw/master/demo_sgmarkets_api_xsf_cofbox.ipynb)
-   the underlying library in folder [sgmarkets_api_xsf_cofbox](https://gitlab.com/sgmarkets/sgmarkets-api-xsf-cofbox/tree/master/sgmarkets_api_xsf_cofbox)

## 2 - Install

From terminal:

```bash
# download and install package from pypi.org
pip install sgmarkets_api_xsf_cofbox

# launch notebook
jupyter notebook
```

Create a notebook or run the demo notebook and modify it to your own use case.

## 3 - User guide

Read the [demo notebook](https://nbviewer.jupyter.org/urls/gitlab.com/sgmarkets/sgmarkets-api-xsf-cofbox/raw/master/demo_sgmarkets_api_xsf_cofbox.ipynb).

The key steps are the following.

### 3.1 - Read the info

The package contains the corresponding API swagger url and contact info:

```python
import sgmarkets_api_xsf_cofbox as COFBOX
# info about COFBOX
COFBOX.info()
```

### 3.2 - Define you credentials

See the user guide in the [sgmarkets-api-auth repo](https://gitlab.com/sgmarkets/sgmarkets-api-auth#3-user-guide)

### 3.3 - Pick an endpoint

Select it from the list of those available in the package.

```python
import sgmarkets_api_xsf_cofbox as COFBOX
# Examples
ep = COFBOX.endpoint.v1_instruments
ep = COFBOX.endpoint.v1_analysis
```

### 3.4 - Create the associated request

Each end point comes with a `Request` object.

```python
# For all endpoints
rq = ep.request()
```

And fill the object with the necessary data.  
This part is specific to the endpoint selected.  
See the [demo notebook](https://nbviewer.jupyter.org/urls/gitlab.com/sgmarkets/sgmarkets-api-xsf-cofbox/raw/master/demo_sgmarkets_api_xsf_cofbox.ipynb) for examples.

Then explore your `Request` object to make sure it is properly set.

```python
# For all endpoints
# display the structure of the object
rq.info()
```

### 3.5 - Call the API

You can call the API directly from the `Request` object.

```python
# For all endpoints
# a is an Api object (see 3.2)
res = rq.call_api(a)
```

The returned object is a `Response` object associated to this endpoint.  
You can explore it starting with

```python
# For all endpoints
# display the structure of the object
res.info()
```

### 3.6 - Save the results

As `.csv` or `.json` file.

```python
# For all endpoints
# save to disk
res.save()
```

The `Response` objects are different for each endpoint.  
See the [demo notebook](https://nbviewer.jupyter.org/urls/gitlab.com/sgmarkets/sgmarkets-api-xsf-cofbox/raw/master/demo_sgmarkets_api_xsf_cofbox.ipynb) for examples.
